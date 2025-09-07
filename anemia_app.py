import streamlit as st

st.set_page_config(page_title="Anemia Evaluation Tool", layout="centered")

st.title("🩸 Anemia Evaluation Assistant")
st.markdown("An interactive, stepwise tool to support anemia workup in internal medicine clinic. For educational use.")

# Step 1
st.header("Step 1: CBC Basics")
mcv = st.selectbox("MCV (Mean Corpuscular Volume)", ["Microcytic (<80)", "Normocytic (80–100)", "Macrocytic (>100)"])
retic = st.selectbox("Reticulocyte Count", ["Low", "Normal", "High"])

# Step 2
st.header("Step 2: Iron Studies")
ferritin = st.number_input("Ferritin (ng/mL)", min_value=0)
transferrin_sat = st.number_input("Transferrin Saturation (%)", min_value=0.0, max_value=100.0)

# Step 3
st.header("Step 3: Vitamin & Hemolysis Markers")
b12 = st.number_input("Vitamin B12 (pg/mL)", min_value=0)
folate = st.number_input("Folate (ng/mL)", min_value=0.0)
ldh = st.selectbox("LDH", ["Normal", "High"])
haptoglobin = st.selectbox("Haptoglobin", ["Normal", "Low"])
indirect_bili = st.selectbox("Indirect Bilirubin", ["Normal", "High"])

# TSH and Cr
st.header("Step 4: Other Contributing Factors")
tsh = st.number_input("TSH (μIU/mL)", min_value=0.0)
creatinine = st.number_input("Creatinine (mg/dL)", min_value=0.0)

# Medications
meds = st.multiselect(
    "Current Medications (select all that apply):",
    ["PPI (e.g., omeprazole)", "NSAIDs", "Methotrexate", "Hydroxyurea", "None of the above"]
)

# Summary
st.markdown("---")
st.subheader("🩺 Summary Interpretation")

summary = ""

# MCV logic
if mcv == "Microcytic (<80)":
    if ferritin < 30:
        summary += "- Likely **iron deficiency anemia**.\n"
    elif ferritin < 100 and transferrin_sat < 15:
        summary += "- Possible **anemia of chronic disease** with iron restriction.\n"
    else:
        summary += "- Consider **thalassemia** or mixed etiology.\n"
elif mcv == "Normocytic (80–100)":
    if retic == "High":
        summary += "- Likely **blood loss or hemolysis**.\n"
    elif retic == "Low":
        summary += "- Possible **ACD, CKD, or marrow suppression**.\n"
elif mcv == "Macrocytic (>100)":
    if b12 < 200 or folate < 4:
        summary += "- Likely **B12 or folate deficiency**.\n"
    else:
        summary += "- Consider **alcohol, liver disease, meds, hypothyroid**.\n"

# Hemolysis
if ldh == "High" and haptoglobin == "Low" and indirect_bili == "High":
    summary += "- Hemolysis suspected. Evaluate with Coombs, smear, LDH, etc.\n"

# TSH
if tsh > 5:
    summary += "- Elevated TSH: **Consider hypothyroidism-induced anemia**.\n"

# Cr
if creatinine >= 2:
    summary += "- Elevated Cr: **Consider anemia of CKD (↓EPO production)**.\n"

# Medications
if "PPI (e.g., omeprazole)" in meds:
    summary += "- PPI use may contribute to **B12 malabsorption**.\n"
if "NSAIDs" in meds:
    summary += "- NSAIDs may cause **chronic GI blood loss**.\n"
if "Methotrexate" in meds or "Hydroxyurea" in meds:
    summary += "- Selected medication may cause **marrow suppression** or macrocytosis.\n"

# Referral logic
referral = False
if (retic == "Low" and ferritin > 100 and mcv == "Normocytic (80–100)" and b12 > 200) or (ldh == "High" and haptoglobin == "Low"):
    referral = True

st.code(summary)

if referral:
    st.warning("📣 Consider Hematology referral for unclear etiology or hemolysis suspicion.")


st.markdown("---")
st.caption("Created by Manal Ahmidouch – GMA Clinic • Med-Ed Track • For Educational Use Only")


