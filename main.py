import joblib
import numpy as np
import google.generativeai as genai
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

app = FastAPI()

model = joblib.load("model_new2.pkl")


genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
gemini = genai.GenerativeModel('gemini-2.5-flash')


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      
        "http://127.0.0.1:5173",       
        "https://insaytia-app.web.app",
        "https://insaytia-app.firebaseapp.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EnergiaInput(BaseModel):
    Uvedomovanie: float
    Agentnost: float
    Sustredenost: float
    Smerovanie: float
    Tlak: float
    Vazby: float
    Zdatnost: float
    Pochybnosti: float
    Izolacia: float
    Presadzovanie: float
    Potreba_uznania: float
    Indiferentnost: float
    token: str


VALID_TOKEN = os.getenv("APP_ACCESS_TOKEN", "default_emergency_password")

@app.post("/predict")
async def predict(data: EnergiaInput, only_score: bool = False):
    
    features = np.array([[
        data.Uvedomovanie, data.Agentnost, data.Sustredenost,
        data.Smerovanie, data.Tlak, data.Vazby,
        data.Zdatnost, data.Pochybnosti, data.Izolacia,
        data.Presadzovanie,
        data.Potreba_uznania, data.Indiferentnost
    ]])
   
    
    score = model.predict(features)[0]
    if only_score:
       return {"score": score}
    
    if data.token != VALID_TOKEN:
        return {
            "score": score,
            "interpretation": "❌ Zadaný kód je neplatný alebo jeho platnosť vypršala. Pre odomknutie AI reflexie zadajte prístupový kód z workshopu."
        }
    
    prompt = f"""
    Si odborný konzultant v oblasti organizačnej psychológie a dátovej analytiky zameranej na rozvoj ľudského kapitálu. V úvodnej vete definuj svoju rolu ako "AI facilitátor reflexie" a vysvetli, že model ukazuje pravdepodobnosť, jedinečnú perspektívu a nie osud. 
    Tvoja úloha: > Interpretuj výslednú konfiguráciu modelu, ktorá pri zadaných vstupoch predikuje úroveň potenčno-agentickej vitality (špecifický pocit energie a nabudenia, ktorý pramení zo zážitku vplyvu a moci ovplyvňovať pracovné prostredie, projekty a uvedomenia si svojej vlastnej úlohy pri dosahovaní pracovných a osobných cieľov) na hodnote {score:.2f} z 7.
    Štruktúra odpovede: 
    1. Stručne vysvetli, prečo pri tejto kombinácii model predpovedá takúto úroveň agentickej vitality. Zameraj sa na kritické faktory.
    2. Identifikuj, ktorá kombinácia faktorov v tomto modeli štatisticky najviac oslabuje predikovanú vitálnu kapacitu.
    3. Navrhni jednu-dve praktické zmeny v tejto konfigurácii, ktoré majú podľa logiky modelu najväčší potenciál posunúť predikciu smerom k vyššej agentickej vitalite a tým ovplyvniť pracovnú činorodosť.
    ### LOGIKA INTERAKCIE (STRIKTNÉ PRAVIDLO) ###
    POZOR: Premenné v tomto modeli nie sú lineárne. Pri analýze profilu aplikuj tieto špecifické pravidlá interakcie:
    Bod presýtenia: Zvýšenie premenných [Presadzovanie] a [Zdatnost] z úrovne 4 na 5 a premenná [Sustredenost] z úrovne 5 na 6 nevedie k nárastu vitality, ale k jej miernemu poklesu (indikuje kognitívne preťaženie alebo systémovú únavu).

    Aktivačný paradox: Zvýšenie premenných [Pochybnosti] a [Izolacia] z úrovne 3 na 4 vyvoláva mierny nárast energie (paradoxne funguje ako katalyzátor agentickej vitality).

    Pri generovaní insightov sa nesústreď na priemery v týchto premenných, ale identifikuj tieto kritické zlomy v profile klienta a vysvetli im, prečo 'viac' v ich prípade znamená 'menej' (a naopak).
    ###########################################
    Hodnoty zdrojov a bariér: Autentické smerovanie reflektuje zážitok slobody, autorstva svojich činov a vplyvu na proces: {data.Smerovanie}/5, Sociálne bezpečie a väzba odráža kvalitu pracovných vzťahov. Energia z pocitu byť rešpektovanou súčasťou kolektívu/organizácie/oblasti podnikania, v ktorých môže byť sám/sama sebou: {data.Vazby}/5, Agentické nabudenie kvôli zážitku efektivity, rastu a zvládania nárokov pracovného prostredia: {data.Zdatnost}/5, Uvedomovanie reflektuje sebavedomú pracovnú identitu. Odráža vnútorné prepojenie medzi „kým som“ a „čo robím“ v práci, čo zvyšuje vitalitu: {data.Uvedomovanie}/5, 
    Agentické rozhodovanie reflektuje aktívny pocit rozhodnovania a zodpovednosti v pracovnom smerovaní a preventívne chráni voči cudzím rozhodnutím: {data.Agentnost}/5, Kognitívna sústredenosť na pracovné úlohy reflektuje kapacitu mentálnej vytrvalosti, prítomnosť pri výkone a flow: {data.Sustredenost}/6, Kontrola a tlak vznikajúce zo striktného dodržiavania postupov, ktoré nie sú v súlade s vnútorným presvedčením: {data.Tlak}/5, Pochybnosti o pracovných schopnostiach, spôsobilostiach a zručnostiach: {data.Pochybnosti}/5, Nedostatok opory, akceptácie, prijatia alebo pochopenia zo strany spolupracovníkov/klientov: {data.Izolacia}/5, 
    Strategický pragmatizmus reflektuje schopnosť účelového presadzovania, strategické plánovanie a využívanie sociálnej dynamiky na dosiahnutie cieľa: {data.Presadzovanie}/5, Potreba uznania a vplyvu prejavovaná ako expanzívna agencia a sebadôvera: {data.Potreba_uznania}/5, Operatívna nekompromisnosť ako schopnosť chladne dominovať a konať neuvážene v práci: {data.Indiferentnost}/5.
    Tón a štýl: > Píš ako vedec-praktik: empaticky, profesionálne a edukatívne. Nepoužívaj klinické diagnózy. Dôsledne komunikuj, že ide o pravdepodobnostnú interpretáciu štatistického modelu, nie o diagnostiku konkrétnej osoby. Model odráža trendy vo vzorke dát, nie fixný osud jednotlivca.
    """
   

    response = gemini.generate_content(prompt)
   
    return {
        "score": round(float(score), 2),
        "interpretation": response.text
    }
