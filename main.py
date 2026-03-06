import joblib
import numpy as np
import google.generativeai as genai
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

app = FastAPI()

# 1. Načítanie vášho nového modelu
model = joblib.load("model_new2.pkl")


# 2. Konfigurácia Gemini
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
gemini = genai.GenerativeModel('gemini-2.5-flash')


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",        # Tvoj lokálny React (Vite)
        "http://127.0.0.1:5173",       # Alternatívna adresa localhostu
        "https://tvoj-projekt.web.app", # TVOJA FIREBASE ADRESA (po nasadení)
        "https://tvoj-projekt.firebaseapp.com"
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


@app.post("/predict")
async def predict(data: EnergiaInput, only_score: bool = False):
    # A. Príprava dát pre model
    features = np.array([[
        data.Uvedomovanie, data.Agentnost, data.Sustredenost,
        data.Smerovanie, data.Tlak, data.Vazby,
        data.Zdatnost, data.Pochybnosti, data.Izolacia,
        data.Presadzovanie,
        data.Potreba_uznania, data.Indiferentnost
    ]])
   
    # B. Výpočet skóre
    score = model.predict(features)[0]
    if only_score:
       return {"score": score}
   
    # C. Tvorba promptu pre Gemini
    prompt = f"""
    Si psychologický mentor pre zvyšovanie mentálnej výkonnosti a emocionálnej energie zamestnancov a manažérov. Tvoja úloha: 1. Krátko vysvetli, prečo pri tejto kombinácii model predpovedá takúto úroveň psychickej energie. 2. Identifikuj najväčšie riziko pre zníženie vnútorných kapacít zamestnanca v tejto konfigurácii. 3. Navrhni jednu praktickú zmenu, ktorá by najviac zvýšila psychickú energiu a mentálnu kapacitu. Píš empaticky, profesionálne a nepoužívaj klinické diagnózy. Tvoj tón je podporný a edukatívny. Vysvetľuj, že model ukazuje pravdepodobnosť, nie osud.
 Skóre psychickej energie je {score:.2f} z 7.
    Hodnoty zdrojov: Autentické smerovanie: {data.Smerovanie}/5, Sociálne bezpečie a väzba: {data.Vazby}/5, Zážitok majstrovstva a kompetentnosti: {data.Zdatnost}/5, Uvedomovanie seba: {data.Uvedomovanie}/5, Zážitok rozhodovania: {data.Agentnost}/5, Kognitívna prítomnosť: {data.Sustredenost}/6, Kontrola a tlak: {data.Tlak}/5, Pochybnosti o schopnostiach: {data.Pochybnosti}/5, Sociálna izolácia: {data.Izolacia}/5, Účelové presadzovanie: {data.Presadzovanie}/5, Potreba uznania a vplyvu: {data.Potreba_uznania}/5, Citový nezáujem o dianie: {data.Indiferentnost}/5.
    Interpretuj tento výsledok empaticky a navrhni jeden praktický krok.
    """
   
    # D. Volanie Gemini
    response = gemini.generate_content(prompt)
   
    return {
        "score": round(float(score), 2),
        "interpretation": response.text
    }
