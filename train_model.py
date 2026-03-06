import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
import joblib


df = pd.read_csv("data_new.csv")




features = [
    'Uvedomovanie', 'Agentnost', 'Sustredenost', 'Smerovanie', 'Tlak', 'Vazby', 'Zdatnost', 'Pochybnosti', 'Izolacia', 'Presadzovanie', 'Potreba_uznania', 'Indiferentnost'
]
target = 'Energia'




X = df[features]
y = df[target]


model = GradientBoostingRegressor(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=3,
    random_state=42
)




model.fit(X, y)


joblib.dump(model, "model_new2.pkl")


print("✅ Model bol úspešne natrénovaný a uložený ako 'model_new2.pkl'")

