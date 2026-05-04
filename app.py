import streamlit as st
import numpy as np
import pickle
import os

# ---------------- LOAD MODEL ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")

if not os.path.exists(MODEL_PATH):
    st.error("❌ Model not found. Run train_model.py first.")
    st.stop()

model, feature_names = pickle.load(open(MODEL_PATH, "rb"))

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Health Analyzer", layout="wide")

# ---------------- PREMIUM UI ----------------
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #0f172a, #020617);
    color: #e2e8f0;
}
h1 { text-align: center; color: #38bdf8; }
.card {
    background: rgba(255,255,255,0.04);
    padding: 20px;
    border-radius: 20px;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08);
}
.stMetric {
    background: rgba(30,41,59,0.8);
    border-radius: 15px;
    padding: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("🏥 AI Health Risk Analyzer")
st.warning("⚠️ Not a medical diagnosis tool")

# ---------------- BMI ----------------
st.subheader("📏 BMI Calculator")
st.markdown('<div class="card">', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    weight = st.number_input("Weight (kg)", 30.0, 150.0, 65.0)
with col2:
    height = st.number_input("Height (cm)", 120.0, 220.0, 170.0)

bmi = weight / ((height/100) ** 2)
st.metric("BMI", f"{bmi:.2f}")

if bmi < 18.5:
    st.info("Underweight")
elif bmi < 25:
    st.success("Normal")
elif bmi < 30:
    st.warning("Overweight")
else:
    st.error("Obese")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- INPUT ----------------
st.subheader("🧑‍⚕️ Patient Data")
st.markdown('<div class="card">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    glucose = st.slider("Glucose", 70, 200, 110)
    bp = st.slider("Blood Pressure", 60, 140, 80)
    age = st.slider("Age", 18, 80, 35)

with col2:
    skin = st.slider("Skin Thickness", 0, 50, 20)
    insulin = st.slider("Insulin", 0, 300, 90)
    dpf = st.slider("Genetic Risk", 0.0, 2.5, 0.4)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- PREDICTION ----------------
input_data = np.array([[glucose, bp, skin, insulin, bmi, dpf, age]])
prob = model.predict_proba(input_data)[0][1]

st.subheader("📊 Risk Analysis")
st.metric("Risk Score", f"{prob:.2f}")

if prob > 0.7:
    st.error("High Risk (Possible Diabetes)")
elif prob > 0.4:
    st.warning("Moderate Risk")
else:
    st.success("Low Risk")

# ---------------- INSIGHTS ----------------
st.subheader("🧠 Insights")

if glucose > 140:
    st.warning("High glucose detected")
if bmi > 30:
    st.warning("High BMI")
if bp > 90:
    st.warning("High blood pressure")

# ---------------- RECOMMENDATIONS ----------------
st.subheader("💡 Recommendations")

if prob > 0.7:
    st.write("""
- Exercise daily  
- Avoid sugar  
- Monitor health regularly  
""")
else:
    st.write("""
- Maintain healthy lifestyle  
- Balanced diet  
- Regular checkups  
""")

# ---------------- DIET ----------------
st.subheader("🥗 Diet Plan")

if prob > 0.7:
    st.write("""
Breakfast: Oats + fruits  
Lunch: Brown rice + vegetables  
Dinner: Salad + protein  
""")
else:
    st.write("""
Breakfast: Fruits + milk  
Lunch: Balanced meal  
Dinner: Light meal  
""")