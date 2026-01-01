import streamlit as st

st.set_page_config(page_title="Anemia Evaluation Tool", layout="centered")

st.title("🩸 Anemia Evaluation Assistant")
st.markdown(
    "An interactive, stepwise tool to support anemia workup in primary care. "
    "**Educational use only**"
)

# ---------- Helpers ----------
def to_float(x: str):
    x = (x or "").strip()
    if x == "":
        return None
    try:
        return float(x)
    except ValueError:
        return None

def fmt(x, digits=2):
    if x is None:
        return "—"
    try:
        return f"{x:.{digits}f}"
    except Exception:
        return str(x)

def maturation_factor(hct):
    """
    Common teaching table:
      Hct >= 40 -> 1.0
      30–39 -> 1.5
      20–29 -> 2.0
      <20  -> 2.5
    """
    if hct is None:
        return None
    if hct >= 40:
        return 1.0
    if 30 <= hct < 40:
        return 1.5
    if 20 <= hct < 30:
        return 2.0
    return 2.5

def add_item(lst, title, rationale="", workup=None):
    lst.append({"title": title, "rationale": rationale, "workup": workup or []})

def selected(x: str):
    """Return None if user hasn't selected a real option yet."""
    if x in (None, "", "Select…"):
        return None
    return x

def yesno_unknown(label: str, help_text: str = ""):
    return selected(st.selectbox(label, ["Select…", "Yes", "No", "Unknown"], index=0, help=help_text))

def tri_state(label: str, options=("Select…", "Unknown", "Normal", "High"), help_text: str = ""):
    return selected(st.selectbox(label, list(options), index=0, help=help_text))

# ---------- Step 0: Symptoms / Severity ----------
st.header("Step 0: Symptoms & Severity")

colS1, colS2 = st.columns(2)
with colS1:
    symptomatic_any = selected(
        st.selectbox(
            "Is the patient symptomatic from anemia?",
            ["Select…", "Yes", "No", "Unknown"],
            index=0,
            help="Examples: dyspnea, fatigue limiting function, dizziness, chest pain, syncope.",
        )
    )
    high_risk_symptoms = selected(
        st.selectbox(
            "Any high-risk symptoms/signs?",
            ["Select…", "Yes", "No", "Unknown"],
            index=0,
            help="Examples: chest pain/ischemia, dyspnea at rest, syncope, hemodynamic instability, active bleeding.",
        )
    )
with colS2:
    active_bleeding = selected(
        st.selectbox(
            "Concern for active/ongoing bleeding?",
            ["Select…", "Yes", "No", "Unknown"],
            index=0,
        )
    )
    cvd = selected(
        st.selectbox(
            "Significant cardiovascular disease (CAD/HF) present?",
            ["Select…", "Yes", "No", "Unknown"],
            index=0,
        )
    )

# ---------- Step 1: CBC Basics (includes Retic Index) ----------
st.header("Step 1: CBC Basics")

colA, colB = st.columns(2)
with colA:
    hb = to_float(st.text_input("Hemoglobin (g/dL)", value="", placeholder="leave blank if unknown"))
    hct = to_float(st.text_input("Hematocrit (%)", value="", placeholder="leave blank if unknown"))
with colB:
    mcv_cat = selected(
        st.selectbox(
            "MCV category",
            ["Select…", "Microcytic (<80)", "Normocytic (80–100)", "Macrocytic (>100)"],
            index=0,
        )
    )
    rdw = selected(st.selectbox("RDW", ["Select…", "Normal", "High", "Unknown"], index=0))

# Other CBC red flags
st.subheader("CBC context (optional)")
colC1, colC2, colC3 = st.columns(3)
with colC1:
    other_cytopenias = selected(
        st.selectbox(
            "Other cytopenias (WBC or platelets low)?",
            ["Select…", "Yes", "No", "Unknown"],
            index=0,
            help="If yes/unknown with persistent anemia, consider broader marrow evaluation.",
        )
    )
with colC2:
    rapid_onset = selected(
        st.selectbox(
            "Rapid onset / acute Hb drop suspected?",
            ["Select…", "Yes", "No", "Unknown"],
            index=0,
        )
    )
with colC3:
    smear_abnormal = selected(
        st.selectbox(
            "Peripheral smear abnormal (if known)?",
            ["Select…", "Yes", "No", "Unknown"],
            index=0,
            help="Examples: blasts, schistocytes, marked dysplasia.",
        )
    )

# Reticulocyte input
st.subheader("Reticulocytes")
retic_mode = st.radio(
    "Reticulocyte input",
    ["Select…", "Qualitative (Low/Normal/High)", "Numeric (%)"],
    horizontal=True,
    index=0,
)

retic_qual = None
retic_pct = None

if retic_mode == "Qualitative (Low/Normal/High)":
    retic_qual = selected(st.selectbox("Reticulocyte count", ["Select…", "Low", "Normal", "High"], index=0))
elif retic_mode == "Numeric (%)":
    retic_pct = to_float(st.text_input("Reticulocyte %", value="", placeholder="leave blank if unknown"))

# Retic Index / RPI
st.subheader("Reticulocyte Index (Corrected Retic) & RPI")
expected_hct = to_float(st.text_input("Expected Hematocrit (%)", value="", placeholder="40"))
if expected_hct is None:
    expected_hct = 40.0  # default, but still respects blank handling

mf = maturation_factor(hct)
corrected_retic = None
rpi = None
if retic_pct is not None and hct is not None and expected_hct is not None and expected_hct != 0:
    corrected_retic = retic_pct * (hct / expected_hct)
    if mf is not None and mf != 0:
        rpi = corrected_retic / mf

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Corrected retic (%)", fmt(corrected_retic, 2))
with c2:
    st.metric("Maturation factor", fmt(mf, 1))
with c3:
    st.metric("RPI", fmt(rpi, 2))
st.caption("Informational: RPI <2 suggests underproduction; ≥2 suggests appropriate marrow response (e.g., hemolysis/bleeding).")

# ---------- Step 2: Iron Studies ----------
st.header("Step 2: Iron Studies")

# Give users the option to indicate whether they have iron studies at all
iron_done = selected(st.selectbox("Are iron studies available?", ["Select…", "Yes", "No"], index=0))
ferritin = transferrin_sat = None

if iron_done == "Yes":
    colI1, colI2 = st.columns(2)
    with colI1:
        ferritin = to_float(st.text_input("Ferritin (ng/mL)", value="", placeholder="leave blank if unknown"))
    with colI2:
        transferrin_sat = to_float(st.text_input("Transferrin Saturation (%)", value="", placeholder="leave blank if unknown"))

# ---------- Step 3: Vitamin & Hemolysis Markers ----------
st.header("Step 3: Vitamin & Hemolysis Markers")

vit_done = selected(st.selectbox("B12/Folate available?", ["Select…", "Yes", "No"], index=0))
b12 = folate = None
if vit_done == "Yes":
    colV1, colV2 = st.columns(2)
    with colV1:
        b12 = to_float(st.text_input("Vitamin B12 (pg/mL)", value="", placeholder="leave blank if unknown"))
    with colV2:
        folate = to_float(st.text_input("Folate (ng/mL)", value="", placeholder="leave blank if unknown"))

hemo_done = selected(st.selectbox("Hemolysis markers available?", ["Select…", "Yes", "No"], index=0))
ldh = haptoglobin = indirect_bili = None
if hemo_done == "Yes":
    colH1, colH2, colH3 = st.columns(3)
    with colH1:
        ldh = selected(st.selectbox("LDH", ["Select…", "Normal", "High", "Unknown"], index=0))
    with colH2:
        haptoglobin = selected(st.selectbox("Haptoglobin", ["Select…", "Normal", "Low", "Unknown"], index=0))
    with colH3:
        indirect_bili = selected(st.selectbox("Indirect Bilirubin", ["Select…", "Normal", "High", "Unknown"], index=0))

# ---------- Step 4: Other Contributing Factors ----------
st.header("Step 4: Other Contributing Factors")

tsh_done = selected(st.selectbox("TSH available?", ["Select…", "Yes", "No"], index=0))
tsh = None
if tsh_done == "Yes":
    tsh = to_float(st.text_input("TSH (μIU/mL)", value="", placeholder="leave blank if unknown"))

egfr_done = selected(st.selectbox("eGFR available?", ["Select…", "Yes", "No"], index=0))
egfr = None
if egfr_done == "Yes":
    egfr = to_float(st.text_input("eGFR (mL/min/1.73m²)", value="", placeholder="leave blank if unknown"))

# ---------- Step 5: High-yield Medications / Exposures ----------
st.header("Step 5: High-yield Medications / Exposures (optional)")
exposures_done = selected(st.selectbox("Medication/exposure screen completed?", ["Select…", "Yes", "No"], index=0))
exposures = []
if exposures_done == "Yes":
    exposures = st.multiselect(
        "Select any that apply:",
        [
            "NSAIDs / aspirin (chronic)",
            "Anticoagulant/antiplatelet use",
            "PPI (long-term)",
            "Metformin (long-term)",
            "Alcohol use (heavy)",
            "Chemotherapy / antimetabolites",
            "Hydroxyurea",
            "Methotrexate / TMP-SMX / pyrimethamine (folate antagonists)",
            "Linezolid",
            "Valproate",
            "Zidovudine / other marrow-toxic antivirals",
            "Recent transfusion (last 3 months)",
        ],
    )

# ---------- Derived: marrow response ----------
marrow_response = "Unknown"
if rpi is not None:
    marrow_response = "Appropriate (RPI ≥2)" if rpi >= 2 else "Inadequate (RPI <2)"
elif retic_qual is not None:
    if retic_qual == "High":
        marrow_response = "Appropriate/High retic"
    elif retic_qual == "Low":
        marrow_response = "Inadequate/Low retic"

# ---------- Output gating ----------
st.markdown("---")
st.subheader("🩺 Differential & Recommended Workup")

if mcv_cat is None:
    st.info(
        "Select an MCV category to generate the differential. "
        "Blank numeric fields are treated as **unknown (not 0)**."
    )
else:
    st.markdown(f"**Marrow response:** {marrow_response}")

    # ---------- Severity prompts (primary care framing; informational) ----------
    triage_msgs = []
    if hb is not None:
        if hb < 6:
            triage_msgs.append("Hb < 6 g/dL: may warrant urgent evaluation depending on symptoms/comorbidities.")
        elif hb < 7:
            triage_msgs.append("Hb < 7 g/dL: transfusion is often considered in many settings, especially if symptomatic.")
        elif hb < 8 and cvd in ("Yes", "Unknown"):
            triage_msgs.append("Hb < 8 g/dL with cardiovascular disease/possible ischemic symptoms: clinicians may consider a higher transfusion threshold.")

    if high_risk_symptoms in ("Yes", "Unknown") or active_bleeding in ("Yes", "Unknown") or rapid_onset in ("Yes", "Unknown"):
        triage_msgs.append("High-risk features or possible acute process: consider prompt clinical evaluation (urgent care/ED depending on severity and context).")

    if egfr is not None and egfr < 30:
        triage_msgs.append("Advanced CKD (eGFR <30) may reduce physiologic reserve—symptoms and trajectory often matter more than a single Hb cutoff.")

    if triage_msgs:
        st.warning("**Severity/triage prompts (informational):**\n- " + "\n- ".join(triage_msgs))

    # ---------- Build differential ----------
    dx = []

    # Microcytic
    if mcv_cat == "Microcytic (<80)":
        if ferritin is not None and ferritin < 30:
            add_item(
                dx,
                "Iron deficiency anemia",
                "Low ferritin supports depleted iron stores.",
                [
                    "Assess source of blood loss (GI/menstrual)",
                    "Consider GI evaluation when appropriate (age/risk-based)",
                    "Consider celiac testing if indicated",
                ],
            )
        elif ferritin is not None and ferritin >= 100 and transferrin_sat is not None and transferrin_sat < 20:
            add_item(
                dx,
                "Anemia of chronic inflammation with functional iron deficiency",
                "Ferritin may be normal/high with low TSAT in inflammatory states.",
                ["CRP/ESR (if inflammatory disease suspected)", "Review chronic inflammatory/infectious disease history"],
            )
        else:
            add_item(
                dx,
                "Thalassemia trait / hemoglobinopathy",
                "Microcytosis without clear low ferritin may suggest thal trait or mixed etiologies.",
                ["CBC indices review (RBC count, RDW)", "Peripheral smear", "Hemoglobin electrophoresis"],
            )

    # Normocytic
    if mcv_cat == "Normocytic (80–100)":
        if marrow_response in ["Appropriate (RPI ≥2)", "Appropriate/High retic"]:
            add_item(
                dx,
                "Blood loss (acute or occult)",
                "Appropriate/High retic suggests response to loss (or recovery phase).",
                ["Assess bleeding history", "Consider iron studies if not done", "Stool testing/GI evaluation when appropriate"],
            )
            add_item(
                dx,
                "Hemolysis",
                "Appropriate/High retic can be seen in hemolysis; confirm with labs and smear.",
                ["Hemolysis panel (LDH, haptoglobin, bilirubin) if not done", "Peripheral smear", "DAT/Coombs if suspected AIHA"],
            )
        elif marrow_response in ["Inadequate (RPI <2)", "Inadequate/Low retic", "Unknown"]:
            add_item(
                dx,
                "Anemia of chronic inflammation",
                "Common hypoproliferative normocytic pattern in chronic disease.",
                ["CRP/ESR if clinically indicated", "Complete iron studies if missing", "Review chronic disease burden"],
            )
            if egfr is not None and egfr < 60:
                add_item(
                    dx,
                    "Anemia associated with CKD",
                    "CKD can cause hypoproliferative normocytic anemia; likelihood increases as eGFR declines.",
                    ["Confirm iron status (ferritin, TSAT)", "Assess for other contributors (B12/folate, bleeding)"],
                )
            add_item(
                dx,
                "Bone marrow underproduction (consider if persistent or with other cytopenias)",
                "Low retic/other cytopenias can suggest marrow process or suppression.",
                ["Peripheral smear", "Repeat CBC trend", "Consider hematology referral if unexplained or if other cytopenias present"],
            )

    # Macrocytic
    if mcv_cat == "Macrocytic (>100)":
        if b12 is not None and b12 < 200:
            add_item(
                dx,
                "Vitamin B12 deficiency",
                "Low B12 supports megaloblastic anemia.",
                ["MMA ± homocysteine if borderline", "Assess diet/malabsorption risks", "Consider IF antibody if pernicious anemia suspected"],
            )
        if folate is not None and folate < 4:
            add_item(
                dx,
                "Folate deficiency",
                "Low folate supports megaloblastic anemia.",
                ["Assess nutrition/alcohol use", "Review folate-antagonist meds/exposures"],
            )
        if (b12 is None or b12 >= 200) and (folate is None or folate >= 4):
            add_item(
                dx,
                "Non-megaloblastic macrocytosis (alcohol, liver disease, hypothyroid, meds, marrow disorders)",
                "Macrocytosis without clear B12/folate deficiency suggests alternative etiologies.",
                ["TSH (if not done)", "LFTs", "Peripheral smear", "Consider hematology referral if persistent/unexplained"],
            )

    # Hemolysis pattern (only if selected and consistent)
    if ldh == "High" and haptoglobin == "Low" and indirect_bili == "High":
        add_item(
            dx,
            "Hemolysis (supported by labs)",
            "LDH high + haptoglobin low + indirect bilirubin high is a classic hemolysis pattern.",
            ["Peripheral smear (schistocytes/spherocytes)", "DAT/Coombs", "Retic absolute count", "Consider G6PD if indicated"],
        )

    # Hypothyroid
    if tsh is not None and tsh > 5:
        add_item(
            dx,
            "Hypothyroidism-associated anemia",
            "Elevated TSH can contribute to normocytic/macrocytic anemia.",
            ["Repeat TSH/FT4 if needed", "Evaluate other causes in parallel (iron/B12/folate)"],
        )

    # Exposure-driven adds
    if "NSAIDs / aspirin (chronic)" in exposures:
        add_item(
            dx,
            "Medication-associated occult GI blood loss (NSAIDs/ASA)",
            "Chronic NSAID/ASA use can contribute to gastritis/ulcer-related blood loss.",
            ["Assess GI symptoms", "Evaluate for iron deficiency; consider GI workup when appropriate", "Review need for NSAID/ASA"],
        )
    if "Anticoagulant/antiplatelet use" in exposures:
        add_item(
            dx,
            "Bleeding risk contribution (anticoagulant/antiplatelet)",
            "These agents can increase bleeding risk and unmask occult sources.",
            ["Bleeding history", "Medication reconciliation and indication review"],
        )
    if "PPI (long-term)" in exposures or "Metformin (long-term)" in exposures:
        add_item(
            dx,
            "Medication-associated B12 deficiency risk (PPI/metformin)",
            "Long-term PPI/metformin use may reduce B12 absorption in some patients.",
            ["Check B12 ± MMA if borderline", "Assess neuropathy/glossitis"],
        )
    if "Alcohol use (heavy)" in exposures:
        add_item(
            dx,
            "Alcohol-related macrocytosis / nutritional deficiency",
            "Alcohol can cause macrocytosis and contribute to folate deficiency.",
            ["LFTs", "Folate/B12 assessment", "Consider counseling/support resources"],
        )
    if (
        "Chemotherapy / antimetabolites" in exposures
        or "Linezolid" in exposures
        or "Valproate" in exposures
        or "Zidovudine / other marrow-toxic antivirals" in exposures
        or "Hydroxyurea" in exposures
        or "Methotrexate / TMP-SMX / pyrimethamine (folate antagonists)" in exposures
    ):
        add_item(
            dx,
            "Medication-associated marrow suppression / macrocytosis risk",
            "Several medications can suppress marrow or cause macrocytosis/cytopenias.",
            ["Review timing vs anemia onset", "Trend CBC", "Consider hematology referral if severe/persistent or with other cytopenias"],
        )

    # De-duplicate by title (preserve order)
    seen = set()
    dx_unique = []
    for item in dx:
        if item["title"] not in seen:
            dx_unique.append(item)
            seen.add(item["title"])

    if len(dx_unique) == 0:
        st.info("Add more data to generate a differential.")
    else:
        for i, item in enumerate(dx_unique[:10], start=1):
            st.markdown(f"### {i}. {item['title']}")
            if item["rationale"]:
                st.markdown(f"**Why:** {item['rationale']}")
            if item["workup"]:
                st.markdown("**Suggested next workup:**")
                for w in item["workup"]:
                    st.markdown(f"- {w}")

    # ---------- Hematology referral guidance (primary care framing) ----------
    st.markdown("---")
    st.subheader("📣 When to consider Hematology referral (primary care)")

    referral_reasons = []

    # Severe/urgent patterns (informational)
    if hb is not None and hb < 7 and (symptomatic_any in ("Yes", "Unknown") or high_risk_symptoms in ("Yes", "Unknown")):
        referral_reasons.append("Severe anemia with symptoms/high-risk features (coordinate urgent evaluation; hematology input may be appropriate).")

    # Marrow flags
    if other_cytopenias in ("Yes", "Unknown"):
        referral_reasons.append("Anemia with other cytopenias (WBC/platelets low) or pancytopenia.")
    if smear_abnormal in ("Yes", "Unknown"):
        referral_reasons.append("Abnormal smear (e.g., blasts, schistocytes, marked dysplasia) or concerning morphology.")
    if marrow_response in ("Inadequate (RPI <2)", "Inadequate/Low retic") and mcv_cat == "Normocytic (80–100)":
        referral_reasons.append("Hypoproliferative normocytic anemia not explained by common primary-care etiologies (e.g., iron/B12/folate/TSH/CKD).")

    # Hemolysis concern
    if (ldh == "High" and haptoglobin == "Low") or (indirect_bili == "High" and ldh == "High"):
        referral_reasons.append("Suspected hemolysis (especially if unexplained, severe, or with abnormal smear).")

    # Persistent / unclear
    if iron_done in ("No", "Select…") and mcv_cat == "Microcytic (<80)":
        referral_reasons.append("Microcytic anemia without available iron studies (or unclear etiology after initial workup).")
    if mcv_cat == "Macrocytic (>100)" and vit_done in ("No", "Select…"):
        referral_reasons.append("Macrocytic anemia without B12/folate evaluation or persistent macrocytosis without clear cause.")

    if not referral_reasons:
        st.caption("No specific referral triggers detected from entered data (limited by missing inputs).")
    else:
        for r in referral_reasons[:8]:
            st.markdown(f"- {r}")

# ---------- Baseline items ----------
st.markdown("---")
st.subheader("Baseline items to consider (if not already available)")
baseline = [
    "Repeat CBC with indices + RDW",
    "Peripheral smear review",
    "Reticulocyte % and/or absolute retic count",
    "Iron studies (ferritin, iron, TIBC, TSAT)",
    "B12 and folate",
]
for b in baseline:
    st.markdown(f"- {b}")

st.markdown("---")
st.caption("Created by Manal Ahmidouch – GMA Clinic • Med-Ed Track • For Educational Use Only")
