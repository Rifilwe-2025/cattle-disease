from django.apps import AppConfig


class MlEngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ml_engine'
    verbose_name = 'Machine Learning Engine'

    def ready(self):
        """
        Pre-load the pickled model, preprocessor and label encoder.

        Without this the artefacts are unpickled lazily, which means the first
        farmer to submit a case after a deploy (or after Render spins the free
        instance back up) pays the whole load cost inside their request. Doing
        it here moves that cost to process start.

        Skipped for management commands that have no business touching the
        model - `migrate` and `collectstatic` run on every deploy and would
        otherwise load ~40MB of scikit-learn for nothing.
        """
        import sys

        argv = sys.argv
        if len(argv) > 1 and argv[1] in {
            'migrate', 'makemigrations', 'collectstatic', 'createcachetable',
            'shell', 'test', 'createsuperuser', 'check', 'compilemessages',
            'makemessages', 'dbshell',
        }:
            return

        from . import services
        services.warm_up()
