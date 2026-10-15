"""
General waiting-room advice shown to farmers after ML disease prediction,
while they wait for their vet's final recommendation.
"""
from __future__ import annotations

from core.cattle_terms import get_disease_label, normalize_disease_key

# Each entry: intro sentence + actionable steps (general care only — not prescriptions).
_ADVICE_EN: dict[str, dict] = {
    'acetonaemia': {
        'intro': 'The model suggests acetonaemia (ketosis). While you wait for your vet:',
        'steps': [
            'Keep the animal calm with access to clean water and shade.',
            'Offer good-quality hay or roughage; avoid forcing concentrates.',
            'Do not stress or move the animal unnecessarily.',
            'Monitor appetite, milk drop, and weakness — call your vet if these worsen.',
        ],
    },
    'blackleg': {
        'intro': 'The model suggests blackleg. While you wait for your vet:',
        'steps': [
            'Isolate the affected animal immediately and limit movement.',
            'Do not cut open swellings or attempt home surgery.',
            'Check vaccination records for the rest of the herd.',
            'Contact your vet urgently — blackleg can progress very quickly.',
        ],
    },
    'bloat': {
        'intro': 'The model suggests bloat. While you wait for your vet:',
        'steps': [
            'Keep the animal standing and walking gently if it is safe to do so.',
            'Remove access to lush pasture or large amounts of fresh feed.',
            'Do not give oils or drenches unless your vet instructs you.',
            'Treat this as urgent — bloat can become fatal within hours.',
        ],
    },
    'calf_diphtheria': {
        'intro': 'The model suggests calf diphtheria. While you wait for your vet:',
        'steps': [
            'Isolate the calf from the rest of the herd.',
            'Clean feeding bottles, teats, and calf pens thoroughly.',
            'Provide soft, palatable feed and clean water if the calf will eat.',
            'Improve ventilation and keep bedding dry.',
        ],
    },
    'calf_pneumonia': {
        'intro': 'The model suggests calf pneumonia. While you wait for your vet:',
        'steps': [
            'Move the calf to a clean, dry, draft-free shelter.',
            'Isolate it from healthy calves to reduce spread.',
            'Reduce dust in the pen and avoid overcrowding.',
            'Keep the calf warm and monitor breathing — contact your vet if breathing worsens.',
        ],
    },
    'coccidiosis': {
        'intro': 'The model suggests coccidiosis. While you wait for your vet:',
        'steps': [
            'Isolate affected calves and keep pens clean and dry.',
            'Provide clean water and avoid overcrowding.',
            'Rotate pastures or resting areas where possible.',
            'Improve hygiene in feeding and watering areas.',
        ],
    },
    'cryptosporidiosis': {
        'intro': 'The model suggests cryptosporidiosis. While you wait for your vet:',
        'steps': [
            'Isolate affected calves immediately — this spreads easily.',
            'Scrub feeders, pens, and boots; wash hands after handling sick calves.',
            'Keep calves warm with clean bedding and fresh water.',
            'Follow your vet\'s advice on electrolytes and do not share equipment between calves.',
        ],
    },
    'displaced_abomasum': {
        'intro': 'The model suggests a displaced abomasum. While you wait for your vet:',
        'steps': [
            'Keep the animal comfortable and avoid unnecessary movement.',
            'Do not force-feed concentrates or large volumes of feed.',
            'Ensure access to clean water.',
            'Contact your vet promptly — this often needs professional treatment.',
        ],
    },
    'fatty_liver_syndrome': {
        'intro': 'The model suggests fatty liver syndrome. While you wait for your vet:',
        'steps': [
            'Reduce stress and avoid forcing the animal to move long distances.',
            'Do not push high-energy concentrates unless your vet advises.',
            'Provide good roughage and clean water.',
            'Monitor appetite and behaviour closely until your vet responds.',
        ],
    },
    'fog_fever': {
        'intro': 'The model suggests fog fever (pasture-associated lung disease). While you wait for your vet:',
        'steps': [
            'Move cattle off very lush or new pasture if you can do so safely.',
            'Keep animals resting in shade with minimal handling.',
            'Avoid dusty yards and long walks.',
            'Watch for rapid breathing or collapse — call your vet if breathing gets worse.',
        ],
    },
    'foot_and_mouth': {
        'intro': 'The model suggests foot-and-mouth disease. While you wait for your vet:',
        'steps': [
            'Isolate the herd area and stop all animal movement immediately.',
            'Report suspected foot-and-mouth to your vet and local authorities at once.',
            'Disinfect boots, vehicles, and equipment used near the animals.',
            'Do not allow visitors or mixing with other herds until officially cleared.',
        ],
    },
    'foot_rot': {
        'intro': 'The model suggests foot rot. While you wait for your vet:',
        'steps': [
            'Move affected cattle to clean, dry ground away from mud.',
            'Keep them on firm footing to reduce further hoof damage.',
            'Isolate severely lame animals if possible.',
            'Clean the feet gently; wait for your vet before applying strong treatments.',
        ],
    },
    'gut_worms': {
        'intro': 'The model suggests gut worms (internal parasites). While you wait for your vet:',
        'steps': [
            'Isolate severely affected animals and provide shade, water, and good nutrition.',
            'Rotate pastures and avoid grazing the same area continuously.',
            'Collect a faecal sample if your vet asks for one before deworming.',
            'Plan strategic deworming with your vet — do not repeat products without advice.',
        ],
    },
    'infectious_bovine_rhinotracheitis': {
        'intro': 'The model suggests infectious bovine rhinotracheitis (IBR). While you wait for your vet:',
        'steps': [
            'Isolate sick animals from the rest of the herd.',
            'Improve airflow in housing and reduce overcrowding.',
            'Avoid introducing new cattle until your vet clears the herd.',
            'Discuss vaccination and biosecurity with your vet when they review the case.',
        ],
    },
    'listeriosis': {
        'intro': 'The model suggests listeriosis. While you wait for your vet:',
        'steps': [
            'Isolate the animal in a quiet, shaded area.',
            'Remove spoiled silage, mouldy hay, or poor-quality feed from all animals.',
            'Do not force-feed; keep clean water available.',
            'Contact your vet urgently — listeriosis can worsen quickly and affects people too.',
        ],
    },
    'liver_fluke': {
        'intro': 'The model suggests liver fluke. While you wait for your vet:',
        'steps': [
            'Fence off or avoid very wet, swampy grazing where possible.',
            'Provide good nutrition and clean water.',
            'Plan fluke treatment with your vet rather than guessing the product or dose.',
            'Monitor body condition and bottle jaw (swelling under the jaw) until your vet responds.',
        ],
    },
    'mastitis': {
        'intro': 'The model suggests mastitis. While you wait for your vet:',
        'steps': [
            'Milk out the affected quarter gently if you can, and discard that milk.',
            'Clean teats before and after milking; use clean towels or disposable wipes.',
            'Do not drink or sell milk from the affected quarter.',
            'Isolate the cow if she is very sick or if you hand-milk into shared containers.',
        ],
    },
    'necrotic_enteritis': {
        'intro': 'The model suggests necrotic enteritis. While you wait for your vet:',
        'steps': [
            'Isolate affected young stock immediately.',
            'Keep pens clean, dry, and well ventilated.',
            'Provide clean water; avoid sudden feed changes.',
            'Contact your vet urgently — this condition can progress quickly in calves.',
        ],
    },
    'peri_weaning_diarrhoea': {
        'intro': 'The model suggests peri-weaning diarrhoea. While you wait for your vet:',
        'steps': [
            'Keep calves in a clean, dry pen with fresh water.',
            'Wean gradually rather than stopping milk suddenly if still possible.',
            'Separate sick calves from healthy ones.',
            'Use electrolytes only as your vet recommends.',
        ],
    },
    'ragwort_poisoning': {
        'intro': 'The model suggests ragwort poisoning. While you wait for your vet:',
        'steps': [
            'Remove cattle from pastures with ragwort or other known toxic plants.',
            'Provide good-quality hay and clean water.',
            'Do not force concentrates unless your vet advises.',
            'Prevent other animals from grazing the same toxic area.',
        ],
    },
    'rift_valley_fever': {
        'intro': 'The model suggests Rift Valley fever. While you wait for your vet:',
        'steps': [
            'Isolate sick animals and report the case to your vet and authorities.',
            'Reduce mosquito exposure where possible (drain stagnant water, use approved controls).',
            'Restrict animal movement and avoid handling abortions or fresh blood without protection.',
            'Discuss vaccination in your area with your vet.',
        ],
    },
    'rumen_acidosis': {
        'intro': 'The model suggests rumen acidosis (grain overload). While you wait for your vet:',
        'steps': [
            'Stop access to concentrates and lush feeds immediately.',
            'Provide good hay and clean water.',
            'Keep the animal standing and walking gently if safe.',
            'Do not drench with home remedies unless your vet instructs you.',
        ],
    },
    'schmallen_berg_virus': {
        'intro': 'The model suggests Schmallenberg virus. While you wait for your vet:',
        'steps': [
            'Isolate affected animals and note any calving or birth problems in the herd.',
            'Control biting midges where practical (drain standing water, shelter at peak fly times).',
            'Do not move animals to other farms until your vet advises.',
            'Discuss breeding and vaccination options with your vet.',
        ],
    },
    'traumatic_reticulitis': {
        'intro': 'The model suggests traumatic reticulitis (hardware disease). While you wait for your vet:',
        'steps': [
            'Keep the animal calm and limit movement.',
            'Do not force-feed; provide only what your vet recommends.',
            'Check feeding areas for wire, nails, or other metal objects.',
            'Contact your vet promptly if pain, bloating, or reluctance to eat worsens.',
        ],
    },
    'trypanosomosis': {
        'intro': 'The model suggests trypanosomosis. While you wait for your vet:',
        'steps': [
            'Rest the animal in shade and avoid long treks or heavy work.',
            'Isolate from the herd to reduce spread by tsetse flies where relevant.',
            'Use approved fly/tsetse control measures for your area.',
            'Contact your vet urgently — trypanosomosis needs proper diagnosis and treatment.',
        ],
    },
    'wooden_tongue': {
        'intro': 'The model suggests wooden tongue. While you wait for your vet:',
        'steps': [
            'Isolate the affected animal.',
            'Offer soft feed and mash if the animal has difficulty eating.',
            'Control flies and avoid rough, stalky pasture that can injure the mouth.',
            'Monitor drooling and swelling — call your vet if the animal stops eating or drinking.',
        ],
    },
}

_DEFAULT_EN = {
    'intro': 'While you wait for your vet to review this case:',
    'steps': [
        'Isolate the affected animal from the rest of the herd.',
        'Provide clean water, shade, and a calm environment.',
        'Monitor symptoms closely and note any changes.',
        'Follow your vet\'s recommendation when they respond — it overrides this general guidance.',
    ],
}

# Shona (sn) — farmer-facing summaries for all model diseases.
_ADVICE_SN: dict[str, dict] = {
    'acetonaemia': {
        'intro': 'Chishandiso chinofungidza acetonaemia (ketosis). Mungamirira vet:',
        'steps': [
            'Chengeta mhuka yakanyarara, ine mvura yakachena nemumvuri.',
            'Ipa huswa hwakanaka; usamanikidzire chikafu chakawanda checoncentrate.',
            'Usaita kumanikidza kufamba kana kushushikana.',
            'Tarisa kushaya kudya, kuderera kwemukaka, uye kusava nesimba.',
        ],
    },
    'blackleg': {
        'intro': 'Chishandiso chinofungidza blackleg. Mungamirira vet:',
        'steps': [
            'Paradzana nemhuka inorwadza nekukurumidza uye dzivisa kufamba.',
            'Usacheke kuzvimba kana kuedza kurapa pawega.',
            'Tarisa marekodhi emajekiseni eboka rose.',
            'Fonera vet nekukurumidza — blackleg inogona kukurumidza.',
        ],
    },
    'bloat': {
        'intro': 'Chishandiso chinofungidza bloat (dumbu rinodziya). Mungamirira vet:',
        'steps': [
            'Chengeta mhuka imire uye fambisa zvishoma kana zvichibvira.',
            'Bvisa mafuro anosvibira kana chikafu chitsva chakawanda.',
            'Usapa mafuta kana mishonga pasina kuraira kwevet.',
            'Tora seyakakosha — bloat inogona kupedzisa hupenyu muawa.',
        ],
    },
    'calf_diphtheria': {
        'intro': 'Chishandiso chinofungidza calf diphtheria. Mungamirira vet:',
        'steps': [
            'Paradzana mhuru kubva kumamwe.',
            'Chenesa zvipfuo zvekupa chikafu nemakamuri emhuru.',
            'Ipa chikafu chakoromba uye mvura yakachena kana ichida kudya.',
            'Vandudza mhepo uye chengeta huswa hwakachena.',
        ],
    },
    'calf_pneumonia': {
        'intro': 'Chishandiso chinofungidza pneumonia yemhuru. Mungamirira vet:',
        'steps': [
            'Isa mhuru panzvimbo yakachena, yakachena, isina mhepo inomhanya.',
            'Paradzana nemhuru dzinogara.',
            'Deredza guruva uye usapinze mhuru dzakawanda pamwechete.',
            'Chengeta mhuru inodziya uye tarisa kupfuya.',
        ],
    },
    'coccidiosis': {
        'intro': 'Chishandiso chinofungidza coccidiosis. Mungamirira vet:',
        'steps': [
            'Paradzana mhuru dzinorwadza uye chengeta makamuri akachena.',
            'Ipa mvura yakachena uye usapinze zvakawanda pamwechete.',
            'Chinja mafuro kana zvichibvira.',
            'Vandudza hunhu hwekuchenesa panopa chikafu nemvura.',
        ],
    },
    'cryptosporidiosis': {
        'intro': 'Chishandiso chinofungidza cryptosporidiosis. Mungamirira vet:',
        'steps': [
            'Paradzana mhuru dzinorwadza nekukurumidza — inotapurirana.',
            'Chenesa zvipfuo, makamuri, uye bhutsu; geza maoko.',
            'Chengeta mhuru dzinodziya nehuswa hwakachena nemvura.',
            'Tevedzera zano revet pamusoro peelectrolytes.',
        ],
    },
    'displaced_abomasum': {
        'intro': 'Chishandiso chinofungidza displaced abomasum. Mungamirira vet:',
        'steps': [
            'Chengeta mhuka yakanyarara uye usaita kufamba kunopinza.',
            'Usamanikidzire kudya kweconcentrate.',
            'Ipa mvura yakachena.',
            'Bata vet nekukurumidza — izvi zvinoda kurapa kwehunyanzvi.',
        ],
    },
    'fatty_liver_syndrome': {
        'intro': 'Chishandiso chinofungidza fatty liver syndrome. Mungamirira vet:',
        'steps': [
            'Deredza kushushikana uye usaita kufambisa kwenguva refu.',
            'Usamanikidzire chikafu chine simba rakawanda.',
            'Ipa huswa hwakanaka nemvura.',
            'Tarisa kudya uye maitiro kusvika vet apindura.',
        ],
    },
    'fog_fever': {
        'intro': 'Chishandiso chinofungidza fog fever. Mungamirira vet:',
        'steps': [
            'Bvisa mombe pamafuro anosvibira kana zvichibvira.',
            'Chengeta zvakanyarara mumumvuri.',
            'Dzivisa guruva uye kufamba kwenguva refu.',
            'Tarisa kupfuya — fonera vet kana kwakanyanya.',
        ],
    },
    'foot_and_mouth': {
        'intro': 'Chishandiso chinofungidza foot-and-mouth. Mungamirira vet:',
        'steps': [
            'Vhara nzvimbo yeboka uye misa kufamba kwemombe.',
            'Taura kuveti nehurumende nekukurumidza.',
            'Chenesa bhutsu, mota, nezvinoshandiswa.',
            'Usabvumire vashanyi kana kuxubana nemamwe mapoka.',
        ],
    },
    'foot_rot': {
        'intro': 'Chishandiso chinofungidza foot rot. Mungamirira vet:',
        'steps': [
            'Isa mombe panzvimbo yakachena, yakachena kure nemadziva.',
            'Chengeta pakati pemakumbo akasimba.',
            'Paradzana dzinorema zvikuru kana zvichibvira.',
            'Chenesa makumbo zvakanaka; mirira kuraira kwevet.',
        ],
    },
    'gut_worms': {
        'intro': 'Chishandiso chinofungidza minzwa mudumbu (gut worms). Mungamirira vet:',
        'steps': [
            'Paradzana dzinorwadwa zvikuru uye ipa mvura nemumvuri.',
            'Chinja mafuro — usashandise imwechete nguva dzose.',
            'unganidza sample yemhodzi kana vet akakumbira.',
            'Ronga deworming neveterinary — usadzokorore mishonga pasina bvunzo.',
        ],
    },
    'infectious_bovine_rhinotracheitis': {
        'intro': 'Chishandiso chinofungidza IBR. Mungamirira vet:',
        'steps': [
            'Paradzana mhuka dzinorwadza.',
            'Vandudza mhepo mukamuri uye usapinze zvakawanda.',
            'Usaisa mhuka itsva kusvika vet abvuma.',
            'Bvunza nezvemajekiseni neveterinary.',
        ],
    },
    'listeriosis': {
        'intro': 'Chishandiso chinofungidza listeriosis. Mungamirira vet:',
        'steps': [
            'Paradzana mhuka munzvimbo yakanyarara.',
            'Bvisa silage yakashata kana chikafu chine muviri.',
            'Usamanikidzire kudya; ipa mvura yakachena.',
            'Fonera vet nekukurumidza — inogona kukanganisa vanhu.',
        ],
    },
    'liver_fluke': {
        'intro': 'Chishandiso chinofungidza liver fluke. Mungamirira vet:',
        'steps': [
            'Dzivisa mafuro anonwira kana ane mvura yakawanda.',
            'Ipa chikafu chakanaka nemvura.',
            'Ronga kurapa fluke neveterinary.',
            'Tarisa muviri uye kuzvimba pasi pemuromo.',
        ],
    },
    'mastitis': {
        'intro': 'Chishandiso chinofungidza mastitis. Mungamirira vet:',
        'steps': [
            'Kama chikamu chinorwadza zvishoma uye usashandise mukaka uyo.',
            'Chenesa mazamu usati wakama uye mushure.',
            'Usamwa kana kutengesa mukaka unobva muchikamu chinorwadza.',
            'Paradzana mhuri kana iri kushaya simba.',
        ],
    },
    'necrotic_enteritis': {
        'intro': 'Chishandiso chinofungidza necrotic enteritis. Mungamirira vet:',
        'steps': [
            'Paradzana mhuru dzinorwadza nekukurumidza.',
            'Chengeta makamuri akachena, akachena, ane mhepo.',
            'Ipa mvura; usachinja chikafu kamwe kamwe.',
            'Fonera vet nekukurumidza.',
        ],
    },
    'peri_weaning_diarrhoea': {
        'intro': 'Chishandiso chinofungidza peri-weaning diarrhoea. Mungamirira vet:',
        'steps': [
            'Chengeta mhuru mukamuri akachena ane mvura.',
            'Bvisa mukaka zvishoma-zvishoma kupfuura kumisa kamwe kamwe.',
            'Paradzana mhuru dzinorwara.',
            'Shandisa electrolytes sezvarairwa neveterinary.',
        ],
    },
    'ragwort_poisoning': {
        'intro': 'Chishandiso chinofungidza ragwort poisoning. Mungamirira vet:',
        'steps': [
            'Bvisa mombe pamafuro ane ragwort kana zvinorawa.',
            'Ipa huswa hwakanaka nemvura.',
            'Usamanikidzire concentrate.',
            'Dzivisa mamwe mhuka kudya munzvimbo imwechete.',
        ],
    },
    'rift_valley_fever': {
        'intro': 'Chishandiso chinofungidza Rift Valley fever. Mungamirira vet:',
        'steps': [
            'Paradzana uye taura kuveti nehurumende.',
            'Deredza zvipukanana (mvura inomira, kudzora zvinobvumidzwa).',
            'Misikidza kufamba uye chengeta kana uchibata zvinhu zvinorwara.',
            'Bvunza nezvemajekiseni munzvimbo yako.',
        ],
    },
    'rumen_acidosis': {
        'intro': 'Chishandiso chinofungidza rumen acidosis. Mungamirira vet:',
        'steps': [
            'Misa kuipa concentrate nemafuro anosvibira.',
            'Ipa huswa hwakanaka nemvura.',
            'Chengeta mhuka imire uye fambise zvishoma kana zvichibvira.',
            'Usapai mishonga yemumba pasina kuraira kwevet.',
        ],
    },
    'schmallen_berg_virus': {
        'intro': 'Chishandiso chinofungidza Schmallenberg virus. Mungamirira vet:',
        'steps': [
            'Paradzana uye nyora matambudziko ekubereka kana aripo.',
            'Dzora zvipukanana zvinoruma.',
            'Usafambise mhuka kumamwe mafamu kusvika vet abvuma.',
            'Bvunza nezvekubereka nemajekiseni.',
        ],
    },
    'traumatic_reticulitis': {
        'intro': 'Chishandiso chinofungidza traumatic reticulitis. Mungamirira vet:',
        'steps': [
            'Chengeta mhuka yakanyarara uye deredza kufamba.',
            'Usamanikidzire kudya.',
            'Tarisa nzvimbo yekupa chikafu kune waya kana zvinhu zvechishongo.',
            'Fonera vet kana kurwadza kana bloat kwakawedzera.',
        ],
    },
    'trypanosomosis': {
        'intro': 'Chishandiso chinofungidza trypanosomosis (domora). Mungamirira vet:',
        'steps': [
            'Zorora mhuka mumumvuri — usaita basa rakareba.',
            'Paradzana kubva kumamwe kudzivisa tsetse.',
            'Shandisa nzira dzekudzora tsetse dzinobvumidzwa.',
            'Fonera vet nekukurumidza — inoda kurapa kwakakodzera.',
        ],
    },
    'wooden_tongue': {
        'intro': 'Chishandiso chinofungidza wooden tongue. Mungamirira vet:',
        'steps': [
            'Paradzana mhuka inorwadza.',
            'Ipa chikafu chakoromba kana iri kunetseka kudya.',
            'Dzora nhata uye dzivisa mafuro ane zvinokuvadza muromo.',
            'Tarisa kubuda mate uye kuzvimba.',
        ],
    },
}

_DEFAULT_SN = {
    'intro': 'Mungamirira vet akabva aona nyaya yako:',
    'steps': [
        'Paradzana mhuka inorwadza kubva kumamwe.',
        'Ipa mvura yakachena, mumvuri, uye nzvimbo yakanyarara.',
        'Tarisa zviratidzo uye nyora shanduko.',
        'Tevedzera zano re veterinary — rinopfuura izvi.',
    ],
}

# Ndebele (nd)
_ADVICE_ND: dict[str, dict] = {
    'acetonaemia': {
        'intro': 'Imodeli icabanga i-acetonaemia. Ngelixa ulinde udokotela:',
        'steps': [
            'Gcina isilwane sithule, sinamanzi ahlanzekileyo nomthunzi.',
            'Nikeza uhlaza oluhle; ungaphoqi ukudla okunamandla.',
            'Ungasiphoqi ukuthi sihambe noma sibe nengcindezi.',
            'Qaphela ukungadli, ukwehla kobisi, nokuthakazeka.',
        ],
    },
    'blackleg': {
        'intro': 'Imodeli icabanga i-blackleg. Ngelixa ulinde udokotela:',
        'steps': [
            'Hlukanisa isilwane esigulayo masinyane bese unciphisa ukuhamba.',
            'Ungavuli ukuvuvukala noma uzame ukwelapha wedwa.',
            'Hlola amarekhodi okugoma omhlambini.',
            'Thinta udokotela ngokushesha — i-blackleg iyashesha.',
        ],
    },
    'bloat': {
        'intro': 'Imodeli icabanga i-bloat. Ngelixa ulinde udokotela:',
        'steps': [
            'Gcina isilwane simi bese uhambe kancane uma kuphephile.',
            'Susa ukudla okushibhile noma okusha okuningi.',
            'Unganiki amafutha noma imithi ngaphandle kweluleko lodokotela.',
            'Thatha lokhu njengokuphuthumayo — i-bloat ingabulala ngamahora.',
        ],
    },
    'calf_diphtheria': {
        'intro': 'Imodeli icabanga i-calf diphtheria. Ngelixa ulinde udokotela:',
        'steps': [
            'Hlukanisa ithole kumanye.',
            'Hlanza izinto zokuphakela nezindlu zezincane.',
            'Nikeza ukudla okuthambile namanzi ahlanzekileyo.',
            'Thuthukisa umoya bese ugcina ubuso buhle.',
        ],
    },
    'calf_pneumonia': {
        'intro': 'Imodeli icabanga isifo samaphaphu ezincane. Ngelixa ulinde udokotela:',
        'steps': [
            'Yisa ithole endaweni ehlanzekileyo, emnyama, engenamoya.',
            'Hlukanisa kwezinye izincane.',
            'Nciphisa uthuli bese ugwema ukugcwalisa izindlu.',
            'Gcina ithole lifudumele bese uqaphela ukuphefumula.',
        ],
    },
    'coccidiosis': {
        'intro': 'Imodeli icabanga i-coccidiosis. Ngelixa ulinde udokotela:',
        'steps': [
            'Hlukanisa izincane ezigulayo bese ugcina izindlu zihlanzekile.',
            'Nikeza amanzi ahlanzekileyo bese ugwema ukugcwala.',
            'Shintsha amadlelo uma kungenzeka.',
            'Thuthukisa ukuhlanza lapho kuphakwa namanzi.',
        ],
    },
    'cryptosporidiosis': {
        'intro': 'Imodeli icabanga i-cryptosporidiosis. Ngelixa ulinde udokotela:',
        'steps': [
            'Hlukanisa izincane masinyane — iyasabalala.',
            'Hlanza izinto, izindlu nezicathulo; geza izandla.',
            'Gcina izincane zifudumele ngezindlu ezihlanzekileyo.',
            'Landela udokotela mayelana nama-electrolytes.',
        ],
    },
    'displaced_abomasum': {
        'intro': 'Imodeli icabanga i-displaced abomasum. Ngelixa ulinde udokotela:',
        'steps': [
            'Gcina isilwane sikhululekile bese unciphisa ukuhamba.',
            'Ungaphoqi ukudla okunamandla.',
            'Nikeza amanzi ahlanzekileyo.',
            'Xhumana nodokotela ngokushesha — kudinga ukwelashwa okusezingeni eliphezulu.',
        ],
    },
    'fatty_liver_syndrome': {
        'intro': 'Imodeli icabanga i-fatty liver syndrome. Ngelixa ulinde udokotela:',
        'steps': [
            'Nciphisa ingcindezi bese ungaphoqi ukuhamba okude.',
            'Ungaphoqi ukudla okunamandla.',
            'Nikeza uhlaza oluhle namanzi.',
            'Qaphela ukudla nokuziphatha kuze kube udokotela uphendula.',
        ],
    },
    'fog_fever': {
        'intro': 'Imodeli icabanga i-fog fever. Ngelixa ulinde udokotela:',
        'steps': [
            'Susa izinkomo emadlelweni amabele uma kuphephile.',
            'Gcina zithule emthunzini.',
            'Gwema uthuli nokuhamba okude.',
            'Qaphela ukuphefumula — thinta udokotela uma kubi.',
        ],
    },
    'foot_and_mouth': {
        'intro': 'Imodeli icabanga isifo senyawo nomlomo. Ngelixa ulinde udokotela:',
        'steps': [
            'Vala indawo yomhlambi bese umisa ukuhamba kwezilwane.',
            'Bika ku-dokotela naseziphathweni masinyane.',
            'Hlanzisa izicathulo, izimoto nezinto.',
            'Ungavumeli izivakashi noma ukuhlanganiswa kwemihlambi.',
        ],
    },
    'foot_rot': {
        'intro': 'Imodeli icabanga i-foot rot. Ngelixa ulinde udokotela:',
        'steps': [
            'Yisa izinkomo endaweni ehlanzekileyo, emnyama.',
            'Gcina ezinyaweni endaweni eqinile.',
            'Hlukanisa ezilimele kakhulu uma kungenzeka.',
            'Hlanza izinyawo zibheke; linda udokotela ngaphambi kokwelapha.',
        ],
    },
    'gut_worms': {
        'intro': 'Imodeli icabanga izibungu zesisu. Ngelixa ulinde udokotela:',
        'steps': [
            'Hlukanisa ezigulayo kakhulu bese unikeza amanzi nomthunzi.',
            'Shintsha amadlelo — ungawasebenzisi njalo endaweni efanayo.',
            'Qoqa isampula yobulongwe uma udokotela ecela.',
            'Hlela ukudeworma nodokotela — ungaphindi imithi ngaphandle kweluleko.',
        ],
    },
    'infectious_bovine_rhinotracheitis': {
        'intro': 'Imodeli icabanga i-IBR. Ngelixa ulinde udokotela:',
        'steps': [
            'Hlukanisa izilwane ezigulayo.',
            'Thuthukisa umoya ezindlini bese ugwema ukugcwalisa.',
            'Ungangeni izilwane ezintsha kuze kube udokotela evumile.',
            'Xoxa ngokugoma nokuvikeleka nodokotela.',
        ],
    },
    'listeriosis': {
        'intro': 'Imodeli icabanga i-listeriosis. Ngelixa ulinde udokotela:',
        'steps': [
            'Hlukanisa isilwane endaweni ethulile emthunzini.',
            'Susa ukudla okubolile noma okunomuvi.',
            'Ungaphoqi ukudla; nikeza amanzi ahlanzekileyo.',
            'Thinta udokotela ngokushesha — iyingozi nakubantu.',
        ],
    },
    'liver_fluke': {
        'intro': 'Imodeli icabanga i-liver fluke. Ngelixa ulinde udokotela:',
        'steps': [
            'Vala noma gwema amadlela anamanzi amaningi.',
            'Nikeza ukudla okuhle namanzi.',
            'Hlela ukwelashwa kwe-fluke nodokotela.',
            'Qaphela isimo somzimba nokuvuvukala ngaphansi komlomo.',
        ],
    },
    'mastitis': {
        'intro': 'Imodeli icabanga i-mastitis. Ngelixa ulinde udokotela:',
        'steps': [
            'Kama ingxenye ekhathazayo kancane bese ulahla lobo bisi.',
            'Hlanza amabele ngaphambi nangemva kokukama.',
            'Ungaphuzi noma uthengise ubisi obulimele.',
            'Hlukanisa inkomo uma igula kakhulu.',
        ],
    },
    'necrotic_enteritis': {
        'intro': 'Imodeli icabanga i-necrotic enteritis. Ngelixa ulinde udokotela:',
        'steps': [
            'Hlukanisa izilwane ezincane masinyane.',
            'Gcina izindlu zihlanzekile, zomile, zinomoya.',
            'Nikeza amanzi; ungashintshi ukudla ngokuzumayo.',
            'Thinta udokotela ngokushesha.',
        ],
    },
    'peri_weaning_diarrhoea': {
        'intro': 'Imodeli icabanga ukudlulisa ngaphambi kokuhlikihla. Ngelixa ulinde udokotela:',
        'steps': [
            'Gcina izincane ezihlanzekile ezinamanzi.',
            'Hlikihla kancane kancane kunokumisa ubisi ngokuphazima.',
            'Hlukanisa izincane ezigulayo.',
            'Sebenzisa ama-electrolytes njengeluleko lodokotela.',
        ],
    },
    'ragwort_poisoning': {
        'intro': 'Imodeli icabanga ukugaxekwa yi-ragwort. Ngelixa ulinde udokotela:',
        'steps': [
            'Susa izinkomo emadlelweni ane-ragwort.',
            'Nikeza uhlaza oluhle namanzi.',
            'Ungaphoqi ukudla okunamandla.',
            'Vimbela ezinye izilwane ukudla endaweni efanayo.',
        ],
    },
    'rift_valley_fever': {
        'intro': 'Imodeli icabanga ifiva ye-Rift Valley. Ngelixa ulinde udokotela:',
        'steps': [
            'Hlukanisa bese ubika ku-dokotela neziphathwo.',
            'Nciphisa izinambuzane (manzi amile, izindlela ezivunyelwe).',
            'Nciphisa ukuhamba bese uvikeleka uma ubamba izilwane ezigulayo.',
            'Xoxa ngokugoma endaweni yakho.',
        ],
    },
    'rumen_acidosis': {
        'intro': 'Imodeli icabanga i-rumen acidosis. Ngelixa ulinde udokotela:',
        'steps': [
            'Misa ukudla okunamandla nokudla okushibhile.',
            'Nikeza uhlaza oluhle namanzi.',
            'Gcina isilwane simi bese uhambe kancane uma kuphephile.',
            'Unganiki imithi yasendlini ngaphandle kweluleko lodokotela.',
        ],
    },
    'schmallen_berg_virus': {
        'intro': 'Imodeli icabanga i-Schmallenberg virus. Ngelixa ulinde udokotela:',
        'steps': [
            'Hlukanisa bese ubhala ngezinkinga zokuzala uma zikhona.',
            'Lawula izinambuzane eziluma.',
            'Ungahambisi izilwane kwezinye izifuyo kuze kube udokotela evumile.',
            'Xoxa ngokuzala nokugoma nodokotela.',
        ],
    },
    'traumatic_reticulitis': {
        'intro': 'Imodeli icabanga i-traumatic reticulitis. Ngelixa ulinde udokotela:',
        'steps': [
            'Gcina isilwane sithule bese unciphisa ukuhamba.',
            'Ungaphoqi ukudla.',
            'Hlola indawo yokuphakela ngezintambo noma izinto zensimbi.',
            'Thinta udokotela uma ubuhlungu noma i-bloat kubi.',
        ],
    },
    'trypanosomosis': {
        'intro': 'Imodeli icabanga i-trypanosomosis. Ngelixa ulinde udokotela:',
        'steps': [
            'Phumulisa isilwane emthunzini — ungasebenzisi kanzima.',
            'Hlukanisa ukuze unciphise tsetse.',
            'Sebenzisa izindlela ezivunyelwe zokulawula tsetse.',
            'Thinta udokotela ngokushesha — kudinga ukwelashwa okufanele.',
        ],
    },
    'wooden_tongue': {
        'intro': 'Imodeli icabanga i-wooden tongue. Ngelixa ulinde udokotela:',
        'steps': [
            'Hlukanisa isilwane esigulayo.',
            'Nikeza ukudla okuthambile uma kunzima ukudla.',
            'Lawula izinambuzane bese ugwema amadlela anobuhlungu emlonyeni.',
            'Qaphela ukuchichima nokuvuvukala.',
        ],
    },
}

_DEFAULT_ND = {
    'intro': 'Ngelixa ulinde udokotela akubuyekeze lesi sigameko:',
    'steps': [
        'Hlukanisa isilwane esigulayo kumhlambi.',
        'Nikeza amanzi ahlanzekileyo, umthunzi, nendawo ethulile.',
        'Qaphela izimpawu bese ubhala izinguquko.',
        'Landela udokotela uma ephendula — lokho kuyinkomba yokugcina.',
    ],
}

_LANG_TABLES = {
    'en': (_ADVICE_EN, _DEFAULT_EN),
    'sn': (_ADVICE_SN, _DEFAULT_SN),
    'nd': (_ADVICE_ND, _DEFAULT_ND),
}


def _lang_code(lang: str | None) -> str:
    code = (lang or 'en').lower().split('-')[0]
    return code if code in _LANG_TABLES else 'en'


def get_waiting_advice(disease_name: str | None, lang: str | None = 'en') -> dict:
    """
    Return {disease_key, disease_label, intro, steps} for the predicted disease.
    Falls back to generic herd-care advice if the disease is unknown.
    """
    code = _lang_code(lang)
    table, default = _LANG_TABLES[code]
    key = normalize_disease_key(disease_name)
    payload = table.get(key) or _ADVICE_EN.get(key) or default
    return {
        'disease_key': key,
        'disease_label': get_disease_label(disease_name),
        'intro': payload['intro'],
        'steps': list(payload['steps']),
    }


def get_waiting_advice_for_case(case, lang: str | None = 'en') -> dict:
    """Pick the primary disease for advice (top prediction, or #1 when low confidence)."""
    disease = case.predicted_disease
    if case.is_low_confidence and case.top_diseases:
        first = case.top_diseases[0]
        if isinstance(first, dict) and first.get('disease'):
            disease = first['disease']
    return get_waiting_advice(disease, lang)
