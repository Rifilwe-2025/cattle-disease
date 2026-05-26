from django.core.management.base import BaseCommand
from django.db import transaction

from cases.models import Case, Symptom, Disease, CaseSymptom, CasePrediction
from django.conf import settings


class Command(BaseCommand):
    help = (
        "Back-fill normalised Symptom, Disease, CaseSymptom and CasePrediction tables "
        "from existing Case.symptoms, Case.predicted_disease and Case.top_diseases JSON. "
        "This is a read-only migration with respect to existing fields (no behaviour change)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not write anything to the database, just show what would be done.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        self.stdout.write(self.style.MIGRATE_HEADING("Starting back-fill of normalised case data..."))

        with transaction.atomic():
            self._backfill_diseases()
            self._backfill_symptoms()
            self._backfill_case_symptoms()
            self._backfill_case_predictions()

            if dry_run:
                self.stdout.write(self.style.WARNING("Dry-run enabled – rolling back all changes."))
                raise transaction.TransactionManagementError("Dry run – rollback")

        self.stdout.write(self.style.SUCCESS("Back-fill completed successfully."))

    # ---- helpers ---------------------------------------------------------

    def _backfill_diseases(self):
        """
        Ensure a Disease row exists for each disease code used in DISEASE_SEVERITY
        and for each predicted_disease already stored on Case records.
        """
        from django.conf import settings as dj_settings

        existing_codes = set(Disease.objects.values_list("code", flat=True))

        # From settings.DISEASE_SEVERITY (authoritative list)
        severity_map = getattr(dj_settings, "DISEASE_SEVERITY", {})
        for code, severity in severity_map.items():
            if code in existing_codes:
                continue
            Disease.objects.create(
                code=code,
                name=code.replace("_", " ").title(),
                severity=severity,
            )
            existing_codes.add(code)

        # From any existing Case.predicted_disease values (in case new ones appear)
        case_codes = set(
            Case.objects.values_list("predicted_disease", flat=True).distinct()
        )
        for code in case_codes:
            if not code:
                continue
            if code in existing_codes:
                continue
            # default severity if not in map
            severity = severity_map.get(code, "NON_SEVERE")
            Disease.objects.create(
                code=code,
                name=code.replace("_", " ").title(),
                severity=severity,
            )
            existing_codes.add(code)

        self.stdout.write(self.style.SUCCESS(f"Ensured Disease rows for {len(existing_codes)} disease codes."))

    def _backfill_symptoms(self):
        """
        Create Symptom rows for all ML symptom feature names and any symptoms
        already present in Case.symptoms JSON.
        """
        import joblib

        existing_codes = set(Symptom.objects.values_list("code", flat=True))

        # Load feature names from ML artifacts if available
        try:
            feature_names = joblib.load(settings.FEATURE_NAMES_PATH)
        except Exception:
            feature_names = []

        contextual_features = [
            "age_years",
            "sex",
            "breed",
            "vaccinated",
            "herd_size",
            "farming_type",
            "recent_movement",
            "season",
            "province",
        ]

        ml_symptoms = [
            f
            for f in feature_names
            if f not in contextual_features
            and not f.startswith("sex_")
            and not f.startswith("breed_")
            and not f.startswith("vaccinated_")
            and not f.startswith("farming_type_")
            and not f.startswith("recent_movement_")
            and not f.startswith("season_")
            and not f.startswith("province_")
        ]

        created = 0
        for code in ml_symptoms:
            if code in existing_codes:
                continue
            Symptom.objects.create(
                code=code,
                name=code.replace("_", " ").title(),
            )
            existing_codes.add(code)
            created += 1

        # Also ensure we have rows for any symptoms present in existing cases
        for case in Case.objects.all().only("symptoms"):
            if not case.symptoms:
                continue
            if isinstance(case.symptoms, dict):
                # if stored as {symptom: 0/1}
                symptom_codes = [k for k, v in case.symptoms.items() if v]
            else:
                # assume list of codes
                symptom_codes = list(case.symptoms)

            for code in symptom_codes:
                if not code:
                    continue
                if code in existing_codes:
                    continue
                Symptom.objects.create(
                    code=code,
                    name=str(code).replace("_", " ").title(),
                )
                existing_codes.add(code)
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Ensured Symptom rows for {len(existing_codes)} symptom codes (created {created}).")
        )

    def _backfill_case_symptoms(self):
        """
        For each Case, mirror Case.symptoms JSON into CaseSymptom rows,
        without removing or changing the original JSON.
        """
        count_links = 0
        for case in Case.objects.all().only("id", "symptoms"):
            if not case.symptoms:
                continue

            if isinstance(case.symptoms, dict):
                symptom_codes = [k for k, v in case.symptoms.items() if v]
            else:
                symptom_codes = list(case.symptoms)

            for idx, code in enumerate(symptom_codes):
                try:
                    symptom = Symptom.objects.get(code=code)
                except Symptom.DoesNotExist:
                    # Skip unknown codes – they should have been created earlier
                    continue

                obj, created = CaseSymptom.objects.get_or_create(
                    case=case,
                    symptom=symptom,
                    defaults={"is_primary": idx == 0},
                )
                if created:
                    count_links += 1

        self.stdout.write(self.style.SUCCESS(f"Back-filled {count_links} CaseSymptom links from existing cases."))

    def _backfill_case_predictions(self):
        """
        Mirror Case.predicted_disease and Case.top_diseases JSON into CasePrediction rows.
        """
        created = 0
        for case in Case.objects.all().only("id", "predicted_disease", "confidence_score", "top_diseases"):
            # Skip if we already have predictions for this case
            if case.predictions.exists():
                continue

            disease_code = case.predicted_disease
            if not disease_code:
                continue

            try:
                main_disease = Disease.objects.get(code=disease_code)
            except Disease.DoesNotExist:
                # Should not happen if _backfill_diseases ran, but guard anyway
                main_disease = Disease.objects.create(
                    code=disease_code,
                    name=disease_code.replace("_", " ").title(),
                    severity="NON_SEVERE",
                )

            CasePrediction.objects.create(
                case=case,
                disease=main_disease,
                probability=max(0.0, min(1.0, float(case.confidence_score or 0.0))),
                rank=1,
            )
            created += 1

            # Add any additional top_3 diseases
            top = case.top_diseases or []
            for idx, item in enumerate(top, start=1):
                code = item.get("disease")
                prob = float(item.get("probability", 0.0))
                if not code:
                    continue
                # Avoid duplicating the main prediction at rank 1
                if code == disease_code and idx == 1:
                    continue

                disease_obj, _ = Disease.objects.get_or_create(
                    code=code,
                    defaults={
                        "name": code.replace("_", " ").title(),
                        "severity": "NON_SEVERE",
                    },
                )
                CasePrediction.objects.get_or_create(
                    case=case,
                    disease=disease_obj,
                    rank=idx + 1,  # start from 2 if top list includes predicted disease
                    defaults={
                        "probability": max(0.0, min(1.0, prob)),
                    },
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Back-filled {created} CasePrediction rows from existing cases."))

