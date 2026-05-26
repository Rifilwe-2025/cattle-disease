"""
AI Assistant knowledge base for cattle health guidance.
Provides disease tips, herd health advice, and daily tips for Zimbabwean farmers.
"""
import random
from datetime import datetime

# NOTE:
# We keep the English knowledge base as the source-of-truth, and provide curated
# Shona (sn) and Ndebele (nd) versions for the farmer-facing assistant so that
# replies follow the language selected on the site.

# Disease tips - common cattle diseases in Zimbabwe and prevention
DISEASE_TIPS = [
    {
        "title": "Lumpy Skin Disease",
        "content": "Lumpy skin disease is spread by biting insects. Prevent by: vaccinating annually, controlling flies and ticks, isolating new animals for 28 days, and keeping cattle away from infected herds. Early signs: fever, nodules on skin, reduced milk."
    },
    {
        "title": "Anthrax",
        "content": "Anthrax is often fatal. Prevention: annual vaccination before rainy season, avoid grazing in anthrax-prone areas, report sudden deaths immediately. Never cut open animals that die suddenly - contact your vet."
    },
    {
        "title": "Foot and Mouth Disease",
        "content": "Highly contagious. Signs: lameness, blisters on mouth and feet, drooling. Prevention: vaccinate as advised by your vet, limit movement of cattle, disinfect equipment. Report suspected cases to the Ministry immediately."
    },
    {
        "title": "Blackleg",
        "content": "Affects young cattle 6-24 months. Prevention: vaccinate calves at 3-4 months with booster, avoid wound contamination. Signs: sudden lameness, swelling, depression. Vaccination is highly effective."
    },
    {
        "title": "Tick-borne Diseases",
        "content": "Redwater, heartwater, and gall sickness spread by ticks. Use approved acaricides, rotate pastures, inspect cattle daily. Consult your vet for the right dipping/spraying schedule for your area."
    },
    {
        "title": "Mastitis",
        "content": "Udder inflammation affects milk quality. Prevent by: clean milking hygiene, dry cow therapy, cull chronic cases. Early signs: swollen udder, abnormal milk. Treat quickly to avoid spread."
    },
]

# Herd health guidance
HERD_HEALTH_TIPS = [
    "Provide clean water daily - cattle need 30-50 litres per day depending on size and heat.",
    "Ensure proper nutrition: good quality hay or grazing, mineral licks, and protein supplements when needed.",
    "Maintain vaccination records. Keep a calendar for boosters - missing a dose can leave your herd vulnerable.",
    "Quarantine new animals for at least 21 days before mixing with your herd to prevent disease spread.",
    "Regular hoof trimming prevents lameness. Inspect feet during handling and address issues early.",
    "Provide shade and shelter - heat stress reduces growth and milk production significantly.",
    "Deworm strategically: treat before rainy season and during high parasite challenge periods.",
    "Monitor body condition score - aim for 2.5-3.5. Thin or overfat cattle are less productive.",
]

# Tips of the day (date-based for variety)
DAILY_TIPS = [
    "Tip: Check your cattle's water sources daily. Dirty or low water reduces intake and productivity.",
    "Tip: Keep a simple health record for each animal - date of vaccination, any illness, treatment given.",
    "Tip: Isolate sick animals promptly. Early separation can prevent disease spread through your herd.",
    "Tip: Work with your vet to create a vaccination calendar. Stick to the schedule for best protection.",
    "Tip: Observe your herd at the same time daily. You'll notice subtle changes that signal early problems.",
    "Tip: Clean and disinfect equipment between animals when treating or vaccinating to prevent cross-contamination.",
    "Tip: Provide mineral licks year-round. Mineral deficiencies weaken immunity and productivity.",
    "Tip: Report unusual symptoms quickly. CattleCare AI can help with predictions - submit a case for guidance.",
]

# General responses for keyword matching
KEYWORD_RESPONSES = {
    "vaccination": "Vaccination is essential for herd health. Common vaccines in Zimbabwe include: lumpy skin, anthrax, blackleg, and foot-and-mouth. Consult your vet for a schedule suited to your area. Keep records of all vaccinations.",
    "vaccinate": "Vaccination is essential for herd health. Common vaccines in Zimbabwe include: lumpy skin, anthrax, blackleg, and foot-and-mouth. Consult your vet for a schedule suited to your area. Keep records of all vaccinations.",
    "symptom": "Watch for these warning signs: loss of appetite, fever, lethargy, diarrhea, coughing, lameness, swollen joints, skin nodules, or changes in milk. When you notice symptoms, use CattleCare AI to submit a case for instant predictions and vet referral if needed.",
    "symptoms": "Watch for these warning signs: loss of appetite, fever, lethargy, diarrhea, coughing, lameness, swollen joints, skin nodules, or changes in milk. When you notice symptoms, use CattleCare AI to submit a case for instant predictions and vet referral if needed.",
    "prevent": "Key prevention steps: 1) Vaccinate on schedule 2) Quarantine new animals 3) Control ticks and flies 4) Provide clean water and good nutrition 5) Maintain clean facilities 6) Report sick animals early. Use CattleCare AI to get predictions for any concerns.",
    "prevention": "Key prevention steps: 1) Vaccinate on schedule 2) Quarantine new animals 3) Control ticks and flies 4) Provide clean water and good nutrition 5) Maintain clean facilities 6) Report sick animals early. Use CattleCare AI to get predictions for any concerns.",
    "feed": "Good nutrition is vital. Provide quality forage (grass, hay), ensure mineral supplementation, and consider protein supplements when pasture is poor. Cattle need consistent access to feed - avoid sudden changes that can cause digestive upset.",
    "feeding": "Good nutrition is vital. Provide quality forage (grass, hay), ensure mineral supplementation, and consider protein supplements when pasture is poor. Cattle need consistent access to feed - avoid sudden changes that can cause digestive upset.",
    "water": "Cattle need 30-50 litres of clean water per day. Ensure troughs are clean, refilled daily, and placed in shaded areas. Dirty or restricted water reduces intake and productivity significantly.",
    "tick": "Ticks spread diseases like redwater and heartwater. Use approved acaricides, follow the dipping/spraying schedule for your region, and inspect cattle regularly. Rotate pastures to reduce tick load.",
    "ticks": "Ticks spread diseases like redwater and heartwater. Use approved acaricides, follow the dipping/spraying schedule for your region, and inspect cattle regularly. Rotate pastures to reduce tick load.",
    "parasite": "Internal parasites (worms) affect growth and health. Deworm before rainy season and during high challenge periods. Work with your vet to choose the right product and avoid resistance.",
    "worm": "Internal parasites (worms) affect growth and health. Deworm before rainy season and during high challenge periods. Work with your vet to choose the right product and avoid resistance.",
    "lumpy": "Lumpy skin disease causes skin nodules and fever. Vaccinate annually, control biting insects, and isolate new animals. Report cases - use CattleCare AI to submit symptoms for guidance.",
    "anthrax": "Anthrax is serious and often fatal. Vaccinate before rainy season. Never open animals that die suddenly - contact your vet. Avoid grazing in known anthrax areas.",
    "vet": "For urgent or severe cases, contact a vet. Use the CattleCare AI 'Submit Case' feature for instant ML-based disease predictions. For severe or critical predictions, you'll be guided to select a vet in your region.",
    "help": "I can help with disease tips, herd health advice, and daily tips. Click the buttons above or ask a question like 'How do I prevent disease?' or 'What are common symptoms?' You can also submit a case for AI-powered disease prediction.",
    "hello": "Hello! I'm your CattleCare AI assistant. I can help with herd health tips, disease prevention, and cattle care guidance. Try 'Disease Tips', 'Herd Health', or ask me a question!",
    "hi": "Hello! I'm your CattleCare AI assistant. Ask me about disease prevention, herd health, or cattle care. You can also submit a case for instant disease predictions.",
    "nutrition": "Good nutrition means quality forage, mineral licks, clean water, and protein when pasture is poor. Avoid sudden feed changes. Monitor body condition - aim for score 2.5-3.5.",
    "shelter": "Provide shade in summer and shelter from wind and rain in winter. Heat stress reduces milk and growth. Calving areas should be dry and clean.",
    "submit": "To submit a case: go to 'Submit Case' from your dashboard or the plus icon. Enter the symptoms you observe and CattleCare AI will give an instant disease prediction and guidance.",
    "case": "Submit a case when you notice unusual symptoms. Go to Submit Case, select symptoms, and get AI-powered predictions. For severe or critical cases, you'll be guided to select a vet in your region.",
}

# Default response when no match
DEFAULT_RESPONSE = (
    "I'm here to help with cattle health! Try asking about:\n\n"
    "• Disease prevention and vaccination\n"
    "• Herd health and nutrition\n"
    "• Common symptoms to watch for\n"
    "• Tick and parasite control\n\n"
    "Or click the quick buttons: Disease Tips, Herd Health, or Tip of the Day. "
    "For specific symptoms, use the Submit Case feature to get AI-powered disease predictions."
)

_KB_SN = {
    "disease_tips": [
        {
            "title": "Chirwere cheLumpy Skin",
            "content": "Chirwere chelumpy skin chinoparadzirwa nezvipukanana zvinoruma. Dzivirira nekubaya majekiseni gore rega rega, kudzora nhata nematiki, kuparadzanisa mhuka itsva kwemazuva 28, uye kudzivisa kusanganisa nemapoka ane chirwere. Zviratidzo: fivha, mapundu paganda, kuderera kwemukaka."
        },
        {
            "title": "Anthrax",
            "content": "Anthrax inouraya zvikuru. Dzivirira nekubaya majekiseni gore rega rega usati wanaya, kudzivisa mafuro ane njodzi, uye taura kufa kamwe kamwe ipapo. Usambocheka mhuka yakafa kamwe kamwe—fonera vet."
        },
        {
            "title": "Foot and Mouth",
            "content": "Inotapuriranwa nyore. Zviratidzo: kurema kwemakumbo, mabhirisita mumuromo nemumakumbo, kubuda mate. Dzivirira nekubaya majekiseni sezvinorairwa, kuderedza kufamba kwemombe, kuchenesa zvishandiso. Taura kuMinistry kana wafungira."
        },
        {
            "title": "Blackleg",
            "content": "Inowanzobata mombe diki 6–24 months. Dzivirira nekubaya majekiseni mhuru pa3–4 months pamwe nebooster. Zviratidzo: kurema kamwe kamwe, kuzvimba, kusuruvara."
        },
        {
            "title": "Zvirwere zvinounzwa nematiki",
            "content": "Redwater, heartwater, ne gall sickness zvinoparadzirwa nematiki. Shandisa mishonga yakabvumidzwa, chinja mafuro, uye ongorora mombe mazuva ose. Bvunza vet nezvechirongwa chekudipisa/kusprayer munzvimbo yako."
        },
        {
            "title": "Mastitis",
            "content": "Kuzvimba kwemazamu kunokanganisa mukaka. Dzivirira nekuchenesa paunokama, kurapa nguva yakaoma (dry cow therapy), uye kubvisa mhuka dzinoramba dzichirwara. Zviratidzo: zamu rakazvimba, mukaka usingaite."
        },
    ],
    "herd_health_tips": [
        "Ipa mvura yakachena mazuva ose—mombe dzinoda 30–50 litres pazuva zvinoenderana nehukuru nekupisa.",
        "Ipa chikafu chakakwana: huswa hwakanaka, mineral licks, uye mapuroteni kana mafuro asina kusimba.",
        "Chengeta marekodhi emajekiseni. Kusapihwa booster kunosiya boka riri panjodzi.",
        "Paradzana nemhuka itsva kwemazuva 21 usati waidzosa muboka kuti udzivise kutapurirana.",
        "Tarisa makumbo nguva dzose; kugadzirisa nekukurumidza kunodzivirira kurema.",
        "Ipa mumvuri nekudzivirira kupisa; heat stress inoderedza kukura nemukaka.",
        "Deworma nenguva: usati wanaya uye panguva dzinowanda maparasites.",
        "Tarisa body condition score; chinangwa 2.5–3.5.",
    ],
    "daily_tips": [
        "Zano: Tarisa nzvimbo dzemvura mazuva ose. Mvura ine tsvina kana shoma inoderedza kudya nemugumisiro.",
        "Zano: Nyora marekodhi emhuka—jekiseni, chirwere, kurapwa, uye mazuva.",
        "Zano: Paradzana nemhuka inorwara nekukurumidza kudzivisa kutapurirana muboka.",
        "Zano: Gadzira kalendari yekubaya majekiseni neveterinary, uye itevedzere.",
        "Zano: Tarisa boka nguva imwe chete mazuva ose kuti uone shanduko diki dzinoratidza dambudziko.",
        "Zano: Chenesa zvishandiso pakati pemhuka paunorapa/kubaya majekiseni kudzivisa kutapurirana.",
        "Zano: Ipa mineral licks gore rose; kushomeka kwemaminerals kunoderedza masoja.",
        "Zano: Taura zviratidzo zvisingawanzo nekukurumidza. Shandisa CattleCare AI kuisa nyaya kuti uwane fungidziro.",
    ],
    "keyword_responses": {
        "vaccination": "Majekiseni akakosha. Majekiseni anowanzoitwa anosanganisira: lumpy skin, anthrax, blackleg, ne foot-and-mouth. Bvunza vet nezvechirongwa munzvimbo yako uye chengeta marekodhi.",
        "vaccinate": "Majekiseni akakosha. Majekiseni anowanzoitwa anosanganisira: lumpy skin, anthrax, blackleg, ne foot-and-mouth. Bvunza vet nezvechirongwa munzvimbo yako uye chengeta marekodhi.",
        "symptom": "Tarisa zviratidzo: kusada kudya, fivha, kusava nesimba, manyoka, chikosoro, kurema, kuzvimba, mapundu paganda, kana shanduko yemukaka. Kana waona, isa nyaya muCattleCare AI kuti uwane fungidziro nekukurumidza.",
        "symptoms": "Tarisa zviratidzo: kusada kudya, fivha, kusava nesimba, manyoka, chikosoro, kurema, kuzvimba, mapundu paganda, kana shanduko yemukaka. Kana waona, isa nyaya muCattleCare AI kuti uwane fungidziro nekukurumidza.",
        "prevent": "Matanho ekudzivirira: 1) Majekiseni nenguva 2) Quarantine mhuka itsva 3) Dzora matiki nenhata 4) Mvura yakachena nechikafu 5) Chenesa nzvimbo 6) Taura chirwere nekukurumidza. Shandisa CattleCare AI kana uine kunetseka.",
        "prevention": "Matanho ekudzivirira: 1) Majekiseni nenguva 2) Quarantine mhuka itsva 3) Dzora matiki nenhata 4) Mvura yakachena nechikafu 5) Chenesa nzvimbo 6) Taura chirwere nekukurumidza. Shandisa CattleCare AI kana uine kunetseka.",
        "help": "Ndinogona kubatsira nemazano ezvirwere, hutano hweboka, uye zano rezuva. Dzvanya mabhatani pamusoro kana bvunza mubvunzo. Unogonawo kuisa nyaya kuti uwane fungidziro.",
        "hello": "Mhoro! Ndiri mubatsiri weCattleCare AI. Bvunza nezvekudzivirira zvirwere, hutano hweboka, kana kutarisira mombe.",
        "hi": "Mhoro! Bvunza nezvekudzivirira zvirwere, hutano hweboka, kana kutarisira mombe.",
        "submit": "Kuisa nyaya: enda ku 'Submit Case' kubva kuDashboard, isa zviratidzo, wobva wawana fungidziro nekurairwa. Kana zvakaoma, uchabatsirwa kusarudza vet.",
        "case": "Isa nyaya kana waona zviratidzo zvisingawanzo. Enda ku Submit Case kuti uwane fungidziro. Kana yakanyanya, uchabatsirwa kusarudza vet.",
    },
    "default_response": (
        "Ndiri pano kubatsira hutano hwemombe! Bvunza nezve:\n\n"
        "• Kudzivirira zvirwere nemajekiseni\n"
        "• Hutano hweboka nechikafu\n"
        "• Zviratidzo zvekutarisa\n"
        "• Matiki nemaparasites\n\n"
        "Kana dzvanya mabhatani: Disease Tips, Herd Health, kana Tip of the Day. "
        "Kana uine zviratidzo, shandisa Submit Case kuti uwane fungidziro."
    ),
    "empty_question": "Ndapota bvunza mubvunzo nezvehutano hwemombe kana kudzivirira zvirwere. Ndiri pano kubatsira!",
}

_KB_ND = {
    "disease_tips": [
        {
            "title": "Lumpy Skin Disease",
            "content": "I-lumpy skin disease isabalaliswa yizibungu eziluma. Vimbela ngokugoma minyaka yonke, ukulawula izintwala lamathikhi, ukuhlukanisa izilwane ezintsha izinsuku 28, nokugwema ukuxubana lemihlambi elamagciwane. Izimpawu: umkhuhlane, amaqhuqhuva esikhumbeni, ukwehla kobisi."
        },
        {
            "title": "Anthrax",
            "content": "I-Anthrax iyingozi kakhulu. Vimbela ngokugoma ngaphambi kwemvula, gwema amadlelo ayingozi, njalo bika ukufa okungazelelwe masinyane. Ungavuli isilwane esife ngokuzuma—thinta inyanga."
        },
        {
            "title": "Foot and Mouth Disease",
            "content": "Iyasabalala kakhulu. Izimpawu: ukuxhuga, amabhamuza emlonyeni lasezinyaweni, ukuchichima amathe. Vimbela ngokugoma, nciphisa ukuhamba, hlanzisisa izinto. Bika kuMinistry uma usola."
        },
        {
            "title": "Blackleg",
            "content": "Ihlasela ikakhulu amathole 6–24 months. Vimbela ngokugoma 3–4 months kunye lebooster. Izimpawu: ukuxhuga ngokuzuma, ukuvuvukala, ukudangala."
        },
        {
            "title": "Tick-borne Diseases",
            "content": "I-Redwater, heartwater, le gall sickness kusabalaliswa ngamathikhi. Sebenzisa ama-acaricides avunyelweyo, shintsha amadlelo, hlola izinkomo nsuku zonke. Buza inyanga ngesheduli yokudipha/spraya."
        },
        {
            "title": "Mastitis",
            "content": "Ukuvuvukala kwamabele kuphazamisa ubisi. Vimbela ngokuhlanzeka ekusengeni, dry cow therapy, lokususa izilwane ezihlala zigula. Izimpawu: ibele elivuvukileyo, ubisi olungajwayelekile."
        },
    ],
    "herd_health_tips": [
        "Nika amanzi ahlanzekileyo nsuku zonke—izinkomo zidinga 30–50 litres ngosuku.",
        "Nikeza ukudla okwaneleyo: amadlelo/ihay, ama-mineral licks, lamaprotheni lapho kudingeka.",
        "Gcina amarekhodi okugoma; ukweqa i-booster kubeka umhlambi engcupheni.",
        "Hlukanisa izilwane ezintsha okungenani izinsuku 21 ngaphambi kokuzixuba.",
        "Hlola izinyawo njalo; ukulungisa masinyane kuvimbela ukuxhuga.",
        "Nikeza umthunzi lokukhosela; ukushisa kwehlisa ukukhula lobisi.",
        "Deworma ngesimiso, ikakhulu ngaphambi kwemvula.",
        "Hlola body condition score; hlosa 2.5–3.5.",
    ],
    "daily_tips": [
        "Icebo: Hlola amanzi nsuku zonke. Amanzi angcolileyo noma ancane ehlisa ukukhiqiza.",
        "Icebo: Bhala amarekhodi wesilwane—ukugoma, ukugula, lokwelashwa.",
        "Icebo: Hlukanisa izilwane ezigulayo masinyane ukuvimbela ukusabalala.",
        "Icebo: Hlela ikhalenda yokugoma lenyanga, ulinamathele.",
        "Icebo: Buka umhlambi ngesikhathi esifanayo nsuku zonke ukuze ubone utshintsho oluncane.",
        "Icebo: Hlanzisisa amathuluzi phakathi kwezilwane ukuvimbela ukuthelelana.",
        "Icebo: Nikeza ama-mineral licks unyaka wonke; ukushoda kwehlisa amasosha.",
        "Icebo: Bika izimpawu ezingajwayelekile masinyane. Sebenzisa CattleCare AI ukufaka isigameko.",
    ],
    "keyword_responses": {
        "vaccination": "Ukugoma kubalulekile. Okugoma okuvamile: lumpy skin, anthrax, blackleg, foot-and-mouth. Xoxa lenyanga ngesheduli yendawo yakho, ugcine amarekhodi.",
        "vaccinate": "Ukugoma kubalulekile. Okugoma okuvamile: lumpy skin, anthrax, blackleg, foot-and-mouth. Xoxa lenyanga ngesheduli yendawo yakho, ugcine amarekhodi.",
        "symptom": "Qaphela: ukungadli, umkhuhlane, ubuthakathaka, isifo sohudo, ukukhwehlela, ukuxhuga, ukuvuvukala, amaqhuqhuva, noma utshintsho ebisini. Uma ukubona, faka isigameko kuCattleCare AI ukuze uthole ukubikezela.",
        "symptoms": "Qaphela: ukungadli, umkhuhlane, ubuthakathaka, isifo sohudo, ukukhwehlela, ukuxhuga, ukuvuvukala, amaqhuqhuva, noma utshintsho ebisini. Uma ukubona, faka isigameko kuCattleCare AI ukuze uthole ukubikezela.",
        "prevent": "Ukuvimbela: 1) Goma ngesikhathi 2) Quarantine izilwane ezintsha 3) Lawula amathikhi lezintwala 4) Amanzi ahlanzekileyo lokudla 5) Hlanzeka 6) Bika kugula masinyane. Sebenzisa CattleCare AI uma kukhona okukhathazayo.",
        "prevention": "Ukuvimbela: 1) Goma ngesikhathi 2) Quarantine izilwane ezintsha 3) Lawula amathikhi lezintwala 4) Amanzi ahlanzekileyo lokudla 5) Hlanzeka 6) Bika kugula masinyane. Sebenzisa CattleCare AI uma kukhona okukhathazayo.",
        "help": "Ngingakunceda ngamacebo ezifo, impilo yomhlambi, lecebo losuku. Cofa amabhathini ngenhla noma ubuze umbuzo. Ungafaka isigameko ukuze uthole ukubikezela.",
        "hello": "Sawubona! Ngingumsizi weCattleCare AI. Buza mayelana nokuvimbela izifo, impilo yomhlambi, noma ukunakekela izinkomo.",
        "hi": "Sawubona! Buza mayelana nokuvimbela izifo, impilo yomhlambi, noma ukunakekela izinkomo.",
        "submit": "Ukufaka isigameko: iya ku 'Submit Case' kuDashboard, faka izimpawu, uthole ukubikezela lokwelulekwa. Uma kubi, uzakhokhelwa ukuthi ukhethe inyanga.",
        "case": "Faka isigameko uma ubona izimpawu ezingajwayelekile. Iya ku Submit Case ukuze uthole ukubikezela. Uma kubi, uzakhokhelwa ukukhetha inyanga.",
    },
    "default_response": (
        "Ngilapha ukukunceda ngempilo yezinkomo! Zama ukubuza:\n\n"
        "• Ukuvimbela izifo lokugoma\n"
        "• Impilo yomhlambi lokudla\n"
        "• Izimpawu okufanele uzibuke\n"
        "• Ukulawula amathikhi lamaparasites\n\n"
        "Noma cofa amabhathini: Disease Tips, Herd Health, noma Tip of the Day. "
        "Uma unezimpawu, sebenzisa Submit Case ukuze uthole ukubikezela."
    ),
    "empty_question": "Ngicela ubuze umbuzo mayelana lempilo yezinkomo noma ukuvimbela izifo. Ngilapha ukukunceda!",
}


def get_tip_of_the_day():
    """Return a tip based on the day of year for consistency."""
    day_of_year = datetime.now().timetuple().tm_yday
    return DAILY_TIPS[day_of_year % len(DAILY_TIPS)]


def get_disease_tip():
    """Return a random disease tip."""
    tip = random.choice(DISEASE_TIPS)
    return f"**{tip['title']}**\n\n{tip['content']}"


def get_herd_health_tip():
    """Return a random herd health tip."""
    return random.choice(HERD_HEALTH_TIPS)

def _pick_kb(lang: str):
    lang = (lang or "en").lower()
    if lang.startswith("sn"):
        return _KB_SN
    if lang.startswith("nd"):
        return _KB_ND
    return None

def _get_tip_of_the_day(lang: str) -> str:
    kb = _pick_kb(lang)
    if not kb:
        return get_tip_of_the_day()
    day_of_year = datetime.now().timetuple().tm_yday
    tips = kb["daily_tips"]
    return tips[day_of_year % len(tips)]

def _get_disease_tip(lang: str) -> str:
    kb = _pick_kb(lang)
    if not kb:
        return get_disease_tip()
    tip = random.choice(kb["disease_tips"])
    return f"**{tip['title']}**\n\n{tip['content']}"

def _get_herd_health_tip(lang: str) -> str:
    kb = _pick_kb(lang)
    if not kb:
        return get_herd_health_tip()
    return random.choice(kb["herd_health_tips"])


def get_response_for_question(question: str, lang: str = "en") -> str:
    """Match question to knowledge base and return appropriate response."""
    if not question or not question.strip():
        kb = _pick_kb(lang)
        if kb:
            return kb["empty_question"]
        return "Please ask a question about cattle health, disease prevention, or herd management. I'm here to help!"
    
    q = question.lower().strip()

    kb = _pick_kb(lang)
    
    # Check keywords
    if kb:
        for keyword, response in kb["keyword_responses"].items():
            if keyword in q:
                return response
    for keyword, response in KEYWORD_RESPONSES.items():
        if keyword in q:
            return response
    
    # Check for question patterns
    if "how" in q and ("healthy" in q or "health" in q):
        return _get_herd_health_tip(lang)
    if "disease" in q or "sick" in q:
        return _get_disease_tip(lang)
    if "tip" in q or "advice" in q:
        return _get_tip_of_the_day(lang)
    
    if kb:
        return kb["default_response"]
    return DEFAULT_RESPONSE


def get_response_for_topic(topic: str, lang: str = "en") -> str:
    """Get response for a predefined topic button."""
    topic = topic.lower().strip()
    if topic in ("disease", "disease tips", "diseasetips"):
        return _get_disease_tip(lang)
    if topic in ("herd", "herd health", "herdhealth"):
        return _get_herd_health_tip(lang)
    if topic in ("tip", "tip of the day", "tipoftheday", "daily"):
        return _get_tip_of_the_day(lang)
    return get_response_for_question(topic, lang=lang)
