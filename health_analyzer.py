import streamlit as st

st.set_page_config(page_title="AI Health Analyzer", page_icon="🩺", layout="centered")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#f0f9ff;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding-top:1rem;}
div.stButton>button{
  background:linear-gradient(135deg,#38bdf8,#0284c7);
  color:#fff;font-weight:700;font-size:15px;border:none;
  border-radius:12px;padding:14px;width:100%;
  box-shadow:0 4px 16px #bae6fd;transition:all .2s;
}
div.stButton>button:hover{background:linear-gradient(135deg,#0ea5e9,#0369a1);transform:translateY(-1px);}
.card{background:#fff;border:1.5px solid #bae6fd;border-radius:16px;padding:1.25rem 1.4rem;margin-bottom:1rem;}
.sec{font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#38bdf8;margin-bottom:.5rem;}
.tag{display:inline-block;font-size:11px;font-weight:700;border-radius:20px;padding:3px 10px;letter-spacing:.03em;}
.gauge-wrap{background:#e0f2fe;border-radius:5px;height:9px;overflow:hidden;margin:6px 0 3px;}
.gauge-fill{height:100%;border-radius:5px;}
</style>""", unsafe_allow_html=True)


# ── Rule engine ──────────────────────────────────────────────────────────────
def calc_bmi(weight, height):
    return round(weight / (height / 100) ** 2, 1)

def bmi_info(bmi):
    if bmi < 18.5: return {"label":"Underweight","color":"#0284c7","bg":"#f0f9ff","bar":18,"desc":"Body weight is too low. Focus on calorie-dense nutritious foods and strength training."}
    if bmi < 25:   return {"label":"Normal","color":"#065f46","bg":"#ecfdf5","bar":42,"desc":"Healthy weight range. Maintain with balanced meals and regular physical activity."}
    if bmi < 30:   return {"label":"Overweight","color":"#92400e","bg":"#fffbeb","bar":65,"desc":"Slightly above ideal. Reduce processed foods, increase fibre and daily movement."}
    return               {"label":"Obese","color":"#9f1239","bg":"#fff1f2","bar":88,"desc":"Above healthy range. Consult a doctor for a safe, structured weight-loss plan."}

def bp_info(sys, dia):
    if sys < 120 and dia < 80: return {"label":"Normal","color":"#065f46","bg":"#ecfdf5","what":"Blood pressure is healthy. Maintain with regular exercise and low-sodium diet."}
    if sys < 130 and dia < 80: return {"label":"Elevated","color":"#0369a1","bg":"#f0f9ff","what":"Slightly above normal. Increase physical activity, reduce salt and caffeine intake to bring it down."}
    if sys < 140 or  dia < 90: return {"label":"High — Stage 1","color":"#9a3412","bg":"#fff7ed","what":"Systolic 130–139 or diastolic 80–89 mmHg. Your heart is pumping harder than ideal. Start with lifestyle changes — cut sodium to <1500 mg/day, walk 30 min daily, limit alcohol, manage stress. Doctor may add medication based on your overall heart risk."}
    return                           {"label":"High — Stage 2","color":"#9f1239","bg":"#fff1f2","what":"Systolic ≥140 or diastolic ≥90 mmHg. Serious level — requires immediate lifestyle changes AND likely medication. Please consult a doctor soon to avoid stroke or heart disease risk."}

def health_score(bmi, sys, dia, activity, smoking, diabetic):
    score = 100
    # BMI
    if bmi < 18.5 or (25 <= bmi < 30): score -= 10
    elif bmi >= 30: score -= 22
    # BP
    if 120 <= sys < 130: score -= 5
    elif 130 <= sys < 140 or 80 <= dia < 90: score -= 15
    elif sys >= 140 or dia >= 90: score -= 25
    # Activity
    act_pen = {"sedentary":15,"lightly active":8,"moderately active":3,"very active":0}
    score -= act_pen.get(activity, 0)
    # Smoking
    if smoking == "smoker": score -= 18
    elif smoking == "former smoker": score -= 6
    # Diabetes
    if diabetic in ("type 1","type 2"): score -= 12
    elif diabetic == "pre-diabetic": score -= 6
    return max(10, min(100, score))

def get_conditions(bmi, sys, dia, smoking, diabetic, activity, age, gender):
    conds = []
    # Cardiovascular
    cv_risk = "low"
    if sys >= 140 or dia >= 90: cv_risk = "high"
    elif sys >= 130 or dia >= 80: cv_risk = "medium"
    elif bmi >= 30 or smoking == "smoker": cv_risk = "medium"
    conds.append({"name":"Cardiovascular Disease","risk":cv_risk,
        "desc":{"low":"Heart health looks good. Maintain with aerobic exercise and heart-healthy diet.",
                "medium":"Moderate cardiovascular risk. Reduce saturated fats, salt and increase cardio exercise.",
                "high":"High cardiovascular risk due to blood pressure. Consult a cardiologist and prioritise lifestyle changes."}[cv_risk]})
    # Diabetes
    if diabetic in ("type 1","type 2"):
        conds.append({"name":"Diabetes Management","risk":"high","desc":"Monitor blood glucose regularly, follow a low-GI diet, exercise daily and take medications as prescribed."})
    elif diabetic == "pre-diabetic" or bmi >= 30:
        conds.append({"name":"Type 2 Diabetes Risk","risk":"medium","desc":"Elevated risk due to weight or pre-diabetic status. Cut sugar, refined carbs and walk at least 30 min daily."})
    else:
        conds.append({"name":"Type 2 Diabetes Risk","risk":"low","desc":"Low diabetes risk. Keep it up with a low-sugar diet and regular physical activity."})
    # Weight-related
    if bmi >= 30:
        conds.append({"name":"Obesity-related Complications","risk":"high","desc":"High BMI raises risk of joint issues, sleep apnoea and fatty liver. Aim for 0.5–1 kg/week gradual weight loss."})
    elif bmi >= 25:
        conds.append({"name":"Metabolic Syndrome","risk":"medium","desc":"Overweight status raises metabolic risk. Prioritise whole foods, reduce portion sizes and increase daily steps."})
    else:
        conds.append({"name":"Metabolic Health","risk":"low","desc":"Metabolic markers look healthy. Continue balanced eating and stay active to maintain this."})
    # Smoking
    if smoking == "smoker":
        conds.append({"name":"Respiratory & Cancer Risk","risk":"high","desc":"Smoking significantly raises risk of lung disease, heart disease and several cancers. Quitting is the single best health decision you can make."})
    elif smoking == "former smoker":
        conds.append({"name":"Residual Smoking Risk","risk":"medium","desc":"Former smokers still carry elevated risk for 5–10 years. Lung function improves over time — focus on cardio fitness and antioxidant-rich foods."})
    # Activity
    if activity == "sedentary":
        conds.append({"name":"Sedentary Lifestyle Risk","risk":"medium","desc":"Physical inactivity raises risk of depression, metabolic disease and early mortality. Start with a 20-min daily walk and build from there."})
    return conds[:3]

def get_meal_plan(bmi, sys, dia, diabetic, activity, gender, age):
    low_cal  = bmi >= 25
    low_gi   = diabetic in ("type 1","type 2","pre-diabetic")
    low_salt = sys >= 130 or dia >= 80
    high_cal = bmi < 18.5

    def _note(base, ls="", lg="", lc="", hc=""):
        notes = [base]
        if low_salt and ls: notes.append(ls)
        if low_gi   and lg: notes.append(lg)
        if low_cal  and lc: notes.append(lc)
        if high_cal and hc: notes.append(hc)
        return " ".join(notes)

    if low_gi:
        breakfast = {"meal":"Oats porridge with chia seeds, berries & almonds","calories":310,
            "tip":_note("High-fibre, low-GI start.",lg="Avoid sugar — use cinnamon to sweeten.")}
        lunch = {"meal":"Brown rice, grilled chicken, spinach & cucumber salad","calories":460,
            "tip":_note("Balanced macros.",lg="Brown rice keeps blood sugar steady.",ls="Skip added salt — use lemon & herbs.")}
        dinner = {"meal":"Lentil soup, whole wheat roti & sautéed greens","calories":420,
            "tip":_note("Plant protein & fibre.",lg="Lentils have a low glycaemic index.",ls="Cook without salt — add cumin & turmeric.")}
        snacks = {"meal":"Handful of walnuts & 1 small apple","calories":160,
            "tip":_note("Healthy fats + slow carbs.",lg="Apple with skin provides soluble fibre.")}
    elif low_cal:
        breakfast = {"meal":"2 boiled eggs, whole wheat toast & fruit salad","calories":320,
            "tip":_note("Protein-rich breakfast reduces hunger later.",lc="Skip butter on toast.",ls="No added salt on eggs.")}
        lunch = {"meal":"Grilled fish, quinoa & mixed vegetable stir-fry","calories":450,
            "tip":_note("Lean protein + complex carbs.",lc="Use olive oil sparingly.",ls="Season with garlic & pepper, not salt.")}
        dinner = {"meal":"Dal (lentil curry), 1 roti & side salad","calories":380,
            "tip":_note("Fibre-rich and filling.",lc="Skip the extra roti.",ls="Limit salt in dal — use tamarind for flavour.")}
        snacks = {"meal":"Carrot & cucumber sticks with hummus","calories":130,
            "tip":_note("Low-calorie crunch.",lc="Portion hummus to 2 tbsp.")}
    elif high_cal:
        breakfast = {"meal":"Banana smoothie with peanut butter, milk & oats","calories":480,
            "tip":"Calorie-dense, nutrient-rich start to support healthy weight gain."}
        lunch = {"meal":"Rice, chicken curry, dal & curd","calories":620,
            "tip":"Full plate with carbs, protein and probiotics for muscle building."}
        dinner = {"meal":"Paneer bhurji, 2 rotis & vegetable curry","calories":560,
            "tip":"Cottage cheese is rich in protein — ideal for weight and muscle gain."}
        snacks = {"meal":"Handful of mixed nuts, dates & a glass of whole milk","calories":320,
            "tip":"Healthy calorie-dense snack between meals."}
    else:
        breakfast = {"meal":"Upma with vegetables & 1 boiled egg","calories":340,
            "tip":_note("Balanced South Indian breakfast.",ls="Use minimal salt in upma.")}
        lunch = {"meal":"2 rotis, mixed vegetable sabzi, dal & curd","calories":490,
            "tip":_note("Complete Indian thali — good macro balance.",ls="Use rock salt sparingly.")}
        dinner = {"meal":"Vegetable soup, brown rice & grilled paneer","calories":410,
            "tip":_note("Light but nutritious dinner.",ls="Skip table salt — use pepper & jeera.")}
        snacks = {"meal":"Roasted chana & 1 seasonal fruit","calories":180,
            "tip":"High protein, high fibre snack that keeps you full."}

    return {"breakfast":breakfast,"lunch":lunch,"dinner":dinner,"snacks":snacks}

def get_exercise_plan(bmi, sys, dia, activity, age, diabetic):
    intense = "high" if activity in ("very active","moderately active") and bmi < 30 and sys < 140 else "moderate"
    safe    = sys < 160 and dia < 100  # avoid intense if very high BP

    if not safe:
        return [
            {"day":"Monday",   "activity":"Gentle walking","duration":"20 min","intensity":"low","benefit":"Safe cardio that lowers BP gradually"},
            {"day":"Wednesday","activity":"Chair yoga / stretching","duration":"25 min","intensity":"low","benefit":"Improves flexibility and reduces cortisol"},
            {"day":"Friday",   "activity":"Slow cycling or stationary bike","duration":"20 min","intensity":"low","benefit":"Low-impact cardio safe for high BP"},
            {"day":"Saturday", "activity":"Breathing exercises (Pranayama)","duration":"15 min","intensity":"low","benefit":"Reduces blood pressure and stress"},
            {"day":"Sunday",   "activity":"Leisurely walk in nature","duration":"30 min","intensity":"low","benefit":"Mental reset and gentle heart conditioning"},
        ]
    elif bmi >= 30:
        return [
            {"day":"Monday",   "activity":"Brisk walking","duration":"30 min","intensity":"moderate","benefit":"Burns calories without stressing joints"},
            {"day":"Tuesday",  "activity":"Water aerobics or swimming","duration":"30 min","intensity":"moderate","benefit":"Full-body workout, easy on joints"},
            {"day":"Thursday", "activity":"Bodyweight squats & wall push-ups","duration":"25 min","intensity":"moderate","benefit":"Builds muscle to boost metabolism"},
            {"day":"Saturday", "activity":"Cycling (flat terrain)","duration":"35 min","intensity":"moderate","benefit":"Heart-healthy cardio, low joint impact"},
            {"day":"Sunday",   "activity":"Yoga (weight loss sequence)","duration":"30 min","intensity":"low","benefit":"Improves metabolism and flexibility"},
        ]
    elif bmi < 18.5:
        return [
            {"day":"Monday",   "activity":"Dumbbell strength training","duration":"35 min","intensity":"moderate","benefit":"Builds lean muscle mass"},
            {"day":"Wednesday","activity":"Resistance band exercises","duration":"30 min","intensity":"moderate","benefit":"Full-body muscle activation"},
            {"day":"Friday",   "activity":"Compound lifts (squats, deadlifts)","duration":"40 min","intensity":"high","benefit":"Maximises muscle and weight gain"},
            {"day":"Saturday", "activity":"Short jog + stretching","duration":"25 min","intensity":"moderate","benefit":"Cardio fitness without burning excess calories"},
            {"day":"Sunday",   "activity":"Active rest — light yoga or walk","duration":"20 min","intensity":"low","benefit":"Recovery while staying mobile"},
        ]
    else:
        return [
            {"day":"Monday",   "activity":"Jogging or brisk walk","duration":"30 min","intensity":"moderate","benefit":"Boosts heart health and burns fat"},
            {"day":"Wednesday","activity":"Full-body strength training","duration":"35 min","intensity":"moderate","benefit":"Maintains muscle mass and metabolism"},
            {"day":"Friday",   "activity":"HIIT (jumping jacks, burpees, plank)","duration":"25 min","intensity":"high","benefit":"Maximum calorie burn in less time"},
            {"day":"Saturday", "activity":"Swimming or cycling","duration":"40 min","intensity":"moderate","benefit":"Low-impact full-body cardio"},
            {"day":"Sunday",   "activity":"Yoga / stretching","duration":"30 min","intensity":"low","benefit":"Recovery, flexibility and stress relief"},
        ]

def get_tips(bmi, sys, dia, activity, smoking, diabetic, age):
    tips = []
    if sys >= 130 or dia >= 80:
        tips.append({"tip":"Reduce sodium to under 1,500 mg per day","reason":"Excess salt makes the kidneys retain water, directly raising blood pressure."})
        tips.append({"tip":"Practice deep breathing for 10 minutes daily","reason":"Slow diaphragmatic breathing activates the parasympathetic system and lowers BP by 5–8 mmHg."})
    if bmi >= 25:
        tips.append({"tip":"Eat slowly and stop at 80% fullness","reason":"It takes 20 minutes for fullness signals to reach your brain — eating slowly prevents overeating."})
        tips.append({"tip":"Replace refined carbs with whole grains","reason":"Whole grains digest slowly, keeping you full longer and stabilising blood sugar."})
    if bmi < 18.5:
        tips.append({"tip":"Eat 5–6 smaller meals spread across the day","reason":"Frequent meals make it easier to consume enough calories for healthy weight gain."})
    if diabetic in ("type 1","type 2","pre-diabetic"):
        tips.append({"tip":"Walk for 10–15 minutes after every meal","reason":"Post-meal walks reduce blood sugar spikes by up to 30% by using glucose as energy."})
        tips.append({"tip":"Choose water or buttermilk instead of sugary drinks","reason":"Liquid sugar causes rapid blood glucose spikes with no nutritional benefit."})
    if smoking == "smoker":
        tips.append({"tip":"Set a quit date and try nicotine replacement therapy","reason":"Quitting smoking cuts heart disease risk by 50% within one year of stopping."})
    if activity == "sedentary":
        tips.append({"tip":"Stand and move for 5 minutes every hour","reason":"Prolonged sitting raises blood sugar and triglycerides even in otherwise healthy people."})
    if age and int(age) > 40:
        tips.append({"tip":"Get annual health check-ups including lipid profile and HbA1c","reason":"Early detection of cholesterol or blood sugar issues allows intervention before serious disease develops."})
    # always
    tips.append({"tip":"Drink 8–10 glasses of water daily","reason":"Proper hydration supports kidney function, blood pressure regulation and metabolism."})
    tips.append({"tip":"Sleep 7–8 hours every night","reason":"Poor sleep raises cortisol, increases appetite and is linked to hypertension, obesity and diabetes."})
    return tips[:4]

def tag(label, color, bg):
    return f'<span class="tag" style="background:{bg};color:{color};">{label}</span>'

def gauge(pct, color):
    return f'<div class="gauge-wrap"><div class="gauge-fill" style="width:{pct}%;background:{color};"></div></div>'


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:1.25rem 0 .75rem;">
  <div style="width:64px;height:64px;border-radius:20px;margin:0 auto .875rem;
    background:linear-gradient(135deg,#38bdf8,#0284c7);
    display:flex;align-items:center;justify-content:center;
    box-shadow:0 8px 24px #bae6fd;font-size:30px;">🩺</div>
  <h1 style="font-size:25px;font-weight:700;color:#0c4a6e;margin:0 0 5px;letter-spacing:-.02em;">
    AI Health Analyzer
  </h1>
  <p style="font-size:13px;color:#0369a1;margin:0;">
    Personalized health insights · No internet required · Instant results
  </p>
</div>""", unsafe_allow_html=True)


# ── Form ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<p class="sec">Personal info</p>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
age    = c1.number_input("Age *",         min_value=10, max_value=100, value=None, step=1,   placeholder="28")
weight = c2.number_input("Weight (kg) *", min_value=20, max_value=300, value=None, step=1,   placeholder="70")
height = c3.number_input("Height (cm) *", min_value=100,max_value=250, value=None, step=1,   placeholder="170")
gender = c4.selectbox("Gender", ["Male","Female","Other"])

bmi = None
if weight and height:
    bmi = calc_bmi(weight, height)
    bi  = bmi_info(bmi)
    st.markdown(f"""
    <div style="background:{bi['bg']};border:1.5px solid {bi['color']}33;border-radius:12px;padding:.875rem;margin:.4rem 0 .75rem;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <span style="font-size:12px;font-weight:600;color:{bi['color']};">Your BMI</span>
        <div style="display:flex;align-items:center;gap:8px;">
          <span style="font-size:26px;font-weight:700;color:{bi['color']};">{bmi}</span>
          {tag(bi['label'],bi['color'],bi['color']+'22')}
        </div>
      </div>
      {gauge(bi['bar'],bi['color'])}
      <div style="display:flex;justify-content:space-between;">
        {''.join(f'<span style="font-size:10px;color:{bi["color"]}99;">{v}</span>' for v in ["10","18.5","25","30","45+"])}
      </div>
      <p style="margin:7px 0 0;font-size:12px;color:{bi['color']};line-height:1.5;">{bi['desc']}</p>
    </div>""", unsafe_allow_html=True)

st.markdown('<p class="sec" style="margin-top:.25rem;">Blood pressure</p>', unsafe_allow_html=True)
b1, b2 = st.columns(2)
systolic  = b1.number_input("Systolic (top number) *",    min_value=70, max_value=250, value=None, step=1, placeholder="120")
diastolic = b2.number_input("Diastolic (bottom number) *", min_value=40, max_value=150, value=None, step=1, placeholder="80")

bp = None
if systolic and diastolic:
    bp = bp_info(int(systolic), int(diastolic))
    with st.expander(f"💓  {int(systolic)}/{int(diastolic)} mmHg — **{bp['label']}** · tap to understand"):
        st.markdown(f"<p style='font-size:13px;color:{bp['color']};line-height:1.6;margin:0;'>{bp['what']}</p>", unsafe_allow_html=True)

st.markdown('<p class="sec" style="margin-top:.5rem;">Lifestyle</p>', unsafe_allow_html=True)
l1, l2, l3 = st.columns(3)
activity = l1.selectbox("Activity level", ["Sedentary","Lightly active","Moderately active","Very active"])
smoking  = l2.selectbox("Smoking",        ["Non-smoker","Smoker","Former smoker"])
diabetic = l3.selectbox("Diabetes",       ["None","Pre-diabetic","Type 1","Type 2"])
st.markdown('</div>', unsafe_allow_html=True)

# ── Analyze ──────────────────────────────────────────────────────────────────
if st.button("🔬  Analyze my health", use_container_width=True):
    if not all([age, weight, height, systolic, diastolic]):
        st.error("Please fill in all required fields (marked *).")
        st.stop()

    f_activity = activity.lower()
    f_smoking  = smoking.lower()
    f_diabetic = diabetic.lower()

    score  = health_score(bmi, int(systolic), int(diastolic), f_activity, f_smoking, f_diabetic)
    conds  = get_conditions(bmi, int(systolic), int(diastolic), f_smoking, f_diabetic, f_activity, age, gender.lower())
    meals  = get_meal_plan(bmi, int(systolic), int(diastolic), f_diabetic, f_activity, gender.lower(), age)
    explan = get_exercise_plan(bmi, int(systolic), int(diastolic), f_activity, age, f_diabetic)
    tips   = get_tips(bmi, int(systolic), int(diastolic), f_activity, f_smoking, f_diabetic, age)

    # Summary text
    summaries = []
    bi2 = bmi_info(bmi)
    summaries.append(f"Your BMI of {bmi} is classified as <b>{bi2['label']}</b>.")
    if bp:
        summaries.append(f"Blood pressure {int(systolic)}/{int(diastolic)} mmHg is <b>{bp['label']}</b>.")
    if f_smoking == "smoker":     summaries.append("Smoking significantly elevates your health risks.")
    if f_activity == "sedentary": summaries.append("Increasing daily movement will have a major positive impact.")
    summary = " ".join(summaries[:3])

    # Score color
    sc = "#065f46" if score >= 80 else "#0369a1" if score >= 60 else "#9f1239"

    # ── Score banner ──
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0ea5e9,#075985);border-radius:20px;
      padding:1.5rem;margin:1rem 0;display:flex;align-items:center;gap:1.25rem;">
      <div style="width:72px;height:72px;border-radius:50%;flex-shrink:0;
        background:rgba(255,255,255,.18);border:3px solid rgba(255,255,255,.45);
        display:flex;flex-direction:column;align-items:center;justify-content:center;">
        <span style="font-size:26px;font-weight:700;color:#fff;line-height:1;">{score}</span>
        <span style="font-size:11px;color:rgba(255,255,255,.65);">/100</span>
      </div>
      <div>
        <p style="margin:0 0 6px;font-weight:700;font-size:15px;color:#fff;">Overall Health Score</p>
        <p style="margin:0;font-size:13px;color:rgba(255,255,255,.88);line-height:1.65;">{summary}</p>
      </div>
    </div>""", unsafe_allow_html=True)

    RISK = {
        "low":   {"color":"#065f46","bg":"#ecfdf5"},
        "medium":{"color":"#92400e","bg":"#fffbeb"},
        "high":  {"color":"#9f1239","bg":"#fff1f2"},
    }

    # ── Conditions ──
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**🏥 Health conditions to watch**")
    for c in conds:
        rc = RISK.get(c["risk"], RISK["medium"])
        st.markdown(f"""
        <div style="background:{rc['bg']};border:1px solid {rc['color']}33;border-radius:12px;
          padding:.875rem;margin-bottom:8px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
            <span style="font-size:14px;font-weight:700;color:{rc['color']};">● {c['name']}</span>
            {tag(c['risk']+' risk',rc['color'],rc['color']+'22')}
          </div>
          <p style="margin:0;font-size:12px;color:{rc['color']};line-height:1.55;opacity:.88;">{c['desc']}</p>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Meal plan ──
    total_cal = sum(m["calories"] for m in meals.values())
    MEAL_META = {
        "breakfast":{"icon":"🌅","accent":"#0ea5e9","label":"Breakfast"},
        "lunch":    {"icon":"🥗","accent":"#10b981","label":"Lunch"},
        "dinner":   {"icon":"🌙","accent":"#6366f1","label":"Dinner"},
        "snacks":   {"icon":"🍎","accent":"#f59e0b","label":"Snacks"},
    }
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"**🍽️ Daily meal plan** &nbsp;<span style='font-size:12px;background:#e0f2fe;color:#0369a1;border-radius:20px;padding:3px 10px;font-weight:600;'>~{total_cal} kcal total</span>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (key, val) in enumerate(meals.items()):
        mm = MEAL_META[key]
        with cols[i]:
            st.markdown(f"""
            <div style="background:{mm['accent']}0d;border:1.5px solid {mm['accent']}44;
              border-radius:14px;padding:1rem;border-top:3px solid {mm['accent']};">
              <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;">
                <span style="font-size:17px;">{mm['icon']}</span>
                <span style="font-size:11px;font-weight:700;color:{mm['accent']};letter-spacing:.04em;">{mm['label'].upper()}</span>
              </div>
              <p style="margin:0 0 4px;font-size:13px;font-weight:600;color:#0c4a6e;line-height:1.4;">{val['meal']}</p>
              <p style="margin:0 0 5px;font-size:13px;font-weight:700;color:{mm['accent']};">{val['calories']} kcal</p>
              <p style="margin:0;font-size:11px;color:#0369a1;line-height:1.4;">{val['tip']}</p>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Exercise ──
    INT_META = {
        "low":     {"color":"#065f46","bg":"#ecfdf5"},
        "moderate":{"color":"#0369a1","bg":"#e0f2fe"},
        "high":    {"color":"#9f1239","bg":"#fff1f2"},
    }
    DAY_COL = ["#0ea5e9","#6366f1","#065f46","#92400e","#9a3412"]
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**🏃 Weekly exercise plan**")
    for i, e in enumerate(explan):
        ic  = INT_META.get(e["intensity"], INT_META["moderate"])
        col = DAY_COL[i % len(DAY_COL)]
        st.markdown(f"""
        <div style="background:{col}0c;border:1px solid {col}33;border-left:4px solid {col};
          border-radius:12px;padding:.875rem 1rem;margin-bottom:7px;
          display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
          <span style="font-size:12px;font-weight:700;color:{col};min-width:72px;">{e['day']}</span>
          <div style="flex:1;">
            <p style="margin:0 0 2px;font-size:13px;font-weight:600;color:#0c4a6e;">{e['activity']}</p>
            <p style="margin:0;font-size:11px;color:#0369a1;">{e['benefit']}</p>
          </div>
          <span style="font-size:12px;color:#0369a1;">{e['duration']}</span>
          {tag(e['intensity'],ic['color'],ic['bg'])}
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Tips ──
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**💡 Personalised lifestyle tips**")
    for t in tips:
        st.markdown(f"""
        <div style="background:#ecfdf5;border:1px solid #6ee7b766;border-radius:12px;
          padding:.875rem;margin-bottom:8px;display:flex;gap:10px;align-items:flex-start;">
          <div style="width:22px;height:22px;border-radius:6px;background:#065f46;
            display:flex;align-items:center;justify-content:center;
            flex-shrink:0;font-size:13px;color:#fff;margin-top:1px;">✓</div>
          <div>
            <p style="margin:0 0 2px;font-size:13px;font-weight:700;color:#065f46;">{t['tip']}</p>
            <p style="margin:0;font-size:12px;color:#065f46;opacity:.78;line-height:1.5;">{t['reason']}</p>
          </div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<p style='font-size:11px;color:#7dd3fc;text-align:center;margin-top:.5rem;'>For informational purposes only — not a substitute for professional medical advice.</p>", unsafe_allow_html=True)
