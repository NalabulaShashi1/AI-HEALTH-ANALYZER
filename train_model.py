import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

data = pd.DataFrame({
    "Glucose": [148,85,183,89,137,120,130,110,140,95],
    "BloodPressure": [72,66,64,66,40,70,80,75,85,60],
    "SkinThickness": [35,29,0,23,35,20,25,30,32,28],
    "Insulin": [0,0,0,94,168,100,120,130,150,80],
    "BMI": [33.6,26.6,23.3,28.1,43.1,30.5,32.0,29.5,35.0,27.0],
    "DiabetesPedigreeFunction": [0.627,0.351,0.672,0.167,2.288,0.5,0.6,0.4,0.7,0.3],
    "Age": [50,31,32,21,33,40,45,38,50,29],
    "Outcome": [1,0,1,0,1,0,1,0,1,0]
})

X = data.drop("Outcome", axis=1)
y = data["Outcome"]

model = RandomForestClassifier()
model.fit(X, y)

with open(MODEL_PATH, "wb") as f:
    pickle.dump((model, X.columns.tolist()), f)

print("✅ Model retrained with 7 features")