import re
import streamlit as st

st.set_page_config(page_title="Anemia Evaluation Tool", layout="centered")

st.title("🩸 Anemia Evaluation Assistant")
st.markdown(
    "An interactive, stepwise tool to support anemia workup in primary care. "
    "**Educational use only**"
)

# ---------------- Mode Toggles ----------------
colM1, colM2 = st.columns([2, 1])
with colM1:
    teaching_mode = st.toggle("Teaching Mode (decision tree + reasoning)", value=False)
with colM2:
    show_all_details = st.toggle("Show all details", value=False) if teaching_mode else False

st.caption(
    "Tip: Keep Teaching Mode off for a clean point-of-care workflow; turn it on for structured reasoning."
)

# ---------------- Helpers ----------------
def to_float(x: str):
    """Blank -> None. Invalid -> None. Never returns 0 unless user typed 0."""
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

def selected(x: str):
    """Return None if user hasn't selected a real option yet."""
    if x in (None, "", "Select…"):
        return None
    return x

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

def add_item(lst, title, rationale="", workup=None, rule="", what_changes=""):
    lst.append(
        {
            "title": title,
            "rationale": rationale,
            "workup": workup or [],
            "rule": rule,
            "what_changes": what_changes,
        }
    )

def dedupe_by_title(items):
    seen = set()
    out = []
    for it in items:
        if it["title"] not in seen:
            out.append(it)
            seen.add(it["title"])
    return out

def _has_value(x):
    return x is not None

def build_known(inputs):
    """
    Track which labs/data are already entered so we can:
      - hide 'check X' suggestions in Clinician view
      - replace with 'Already entered: ...' in Teaching view
    """
    known = {
        "tsh": _has_value(inputs["tsh"]),
        "egfr": _has_value(inputs["egfr"]),
        "ferritin": _has_value(inputs["ferritin"]),
        "tsat": _has_value(inputs["tsat"]),
        "b12": _has_value(inputs["b12"]),
        "folate": _has_value(inputs["folate"]),
        "ldh": _has_value(inputs["ldh"]),
        "haptoglobin": _has_value(inputs["haptoglobin"]),
        "indirect_bili": _has_value(inputs["indirect_bili"]),
        "retic_pct": _has_value(inputs["retic_pct"]),
        "retic_qual": _has_value(inputs["retic_qual"]),
        "rpi": _has_value(inputs["rpi"]),
    }
    return known

# Workup filtering: map line -> which "key" it depends on
WORKUP_PATTERNS = [
    (re.compile(r"\bTSH\b", re.I), "tsh"),
    (re.compile(r"\beGFR\b|\bGFR\b", re.I), "egfr"),
    (re.compile(r"\bFerritin\b", re.I), "ferritin"),
    (re.compile(r"\bTSAT\b|\bTransferrin Saturation\b|\btransferrin\b", re.I), "tsat"),
    (re.compile(r"\bIron studies\b|\bTIBC\b|\biron\b", re.I), "ferritin"),  # treat as iron-entered if ferritin present
    (re.compile(r"\bB12\b|\bVitamin B12\b", re.I), "b12"),
    (re.compile(r"\bFolate\b", re.I), "folate"),
    (re.compile(r"\bLDH\b", re.I), "ldh"),
    (re.compile(r"\bHaptoglobin\b", re.I), "haptoglobin"),
    (re.compile(r"\bIndirect Bilirubin\b|\bBilirubin\b", re.I), "indirect_bili"),
    (re.compile(r"\bRetic\b|\bReticulocyte\b", re.I), "retic_pct"),  # numeric retic entered
]

def suppress_or_annotate_workup_line(line: str, known: dict, inputs: dict, teaching: bool):
    """
    Returns:
      - None if line should be hidden
      - or a replacement string if teaching and we want an 'Already entered' annotation
      - or the original line
    """
    for pat, key in WORKUP_PATTERNS:
        if pat.search(line):
            if known.get(key, False):
                if teaching:
                    # Make a nice "Already entered" note
                    if key == "tsh":
                        return f"Already entered: TSH = {fmt(inputs['tsh'], 2)}"
                    if key == "egfr":
                        return f"Already entered: eGFR = {fmt(inputs['egfr'], 0)}"
                    if key == "ferritin":
                        return f"Already entered: Ferritin = {fmt(inputs['ferritin'], 0)}"
                    if key == "tsat":
                        return f"Already entered: TSAT = {fmt(inputs['tsat'], 0)}%"
                    if key == "b12":
                        return f"Already entered: Vitamin B12 = {fmt(inputs['b12'], 0)}"
                    if key == "folate":
                        return f"Already entered: Folate = {fmt(inputs['folate'], 1)}"
                    if key == "ldh":
                        return f"Already entered: LDH = {inputs['ldh']}"
                    if key == "haptoglobin":
                        return f"Already entered: Haptoglobin = {inputs['haptoglobin']}"
                    if key == "indirect_bili":
                        return f"Already entered: Indirect bilirubin = {inputs['indirect_bili']}"
                    return "Already entered."
                return None
            return line
    return line

def decision_tree_dot(mcv_cat, marrow_response, known, inputs):
    """
    Build a small dynamic tree that visually narrows as you input data.
    Keep it simple + readable.
    """
    def node_style(active=False):
        if active:
            return 'shape="box", style="rounded,bold"'
        return 'shape="box", style="rounded"'

    def status_label(key, label):
        return f"{label}: {'✅' if known.get(key, False) else '❓'}"

    # Active flags
    micro = mcv_cat == "Microcytic (<80)"
    normo = mcv_cat == "Normocytic (80–100)"
    macro = mcv_cat == "Macrocytic (>100)"

    retic_known = known.get("rpi") or known.get("retic_pct") or known.get("retic_qual")
    iron_known = known.get("ferritin") or known.get("tsat")
    vits_known = known.get("b12") or known.get("folate")
    hemo_known = known.get("ldh") or known.get("haptoglobin") or known.get("indirect_bili")

    dot = ['digraph G { rankdir=TB; splines=false; nodesep=0.3; ranksep=0.35;']
    dot.append(f'Start [{node_style(True)} label="Start"];')

    dot.append(f'MCV [{node_style(mcv_cat is not None)} label="MCV category: {mcv_cat or "Select…"}"];')
    dot.append('Start -> MCV;')

    dot.append(f'Micro [{node_style(micro)} label="Microcytic (<80)"];')
    dot.append(f'Normo [{node_style(normo)} label="Normocytic (80–100)"];')
    dot.append(f'Macro [{node_style(macro)} label="Macrocytic (>100)"];')
    dot.append('MCV -> Micro; MCV -> Normo; MCV -> Macro;')

    # Micro branch
    dot.append(f'Iron [{node_style(micro and iron_known)} label="{status_label("ferritin","Ferritin")}\\n{status_label("tsat","TSAT")}"];')
    dot.append('Micro -> Iron;')
    dot.append(f'MicroNext [{node_style(micro and not iron_known)} label="If iron studies missing:\\nfirst narrow with ferritin/TSAT"];')
    dot.append('Micro -> MicroNext;')

    # Normo branch
    dot.append(f'Retic [{node_style(normo and retic_known)} label="Marrow response\\n(RPI/retic): {marrow_response}"];')
    dot.append('Normo -> Retic;')
    dot.append(f'NormoNext [{node_style(normo and not retic_known)} label="If retic/RPI missing:\\nthis is the key next step"];')
    dot.append('Normo -> NormoNext;')
    dot.append(f'Hemo [{node_style(normo and hemo_known)} label="{status_label("ldh","LDH")}\\n{status_label("haptoglobin","Haptoglobin")}\\n{status_label("indirect_bili","Indirect bili")}"];')
    dot.append('Retic -> Hemo;')

    # Macro branch
    dot.append(f'Vits [{node_style(macro and vits_known)} label="{status_label("b12","B12")}\\n{status_label("folate","Folate")}"];')
    dot.append('Macro -> Vits;')
    dot.append(f'MacroOther [{node_style(macro)} label="{status_label("tsh","TSH")}\\nConsider LFTs + smear + meds/exposures"];')
    dot.append('Vits -> MacroOther;')

    dot.append('}')
    return "\n".join(dot)

# ---------------- Step 0: Symptoms & Severity ----------------
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

# ---------------- Step 1: CBC Basics ----------------
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
            help="Microcytic: iron deficiency/thalassemia/inflammation; Normocytic: underproduction vs hemolysis/bleeding; Macrocytic: B12/folate vs non-megaloblastic causes.",
        )
    )
    rdw = selected(
        st.selectbox(
            "RDW",
            ["Select…", "Normal", "High", "Unknown"],
            index=0,
            help="High RDW can suggest mixed etiologies or evolving deficiency states; normal RDW may fit thal trait (context-dependent).",
        )
    )

st.subheader("CBC context (optional)")
colC1, colC2, colC3 = st.columns(3)
with colC1:
    other_cytopenias = selected(
        st.selectbox(
            "Other cytopenias (WBC or platelets low)?",
            ["Select…", "Yes", "No", "Unknown"],
            index=0,
            help="If yes/unknown with persistent anemia, broaden to marrow/process considerations.",
        )
    )
with colC2:
    rapid_onset = selected(
        st.selectbox(
            "Rapid onset / acute Hb drop suspected?",
            ["Select…", "Yes", "No", "Unknown"],
            index=0,
            help="Acute drops raise bleeding/hemolysis concerns; trends matter.",
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

# ---------------- Reticulocytes + RPI ----------------
st.subheader("Reticulocytes")

retic_mode = st.radio(
    "Reticulocyte input",
    ["Qualitative (Low/Normal/High)", "Numeric (%)"],
    horizontal=True,
    index=0,
    help="Retic/RPI helps separate underproduction from hemolysis/bleeding physiology.",
)

retic_qual = None
retic_pct = None

if retic_mode == "Qualitative (Low/Normal/High)":
    retic_qual = selected(st.selectbox("Reticulocyte count", ["Select…", "Low", "Normal", "High"], index=0))
else:
    retic_pct = to_float(st.text_input("Reticulocyte %", value="", placeholder="leave blank if unknown"))

st.subheader("Reticulocyte Index (Corrected Retic) & RPI")

expected_hct_input = to_float(st.text_input("Expected Hematocrit (%)", value="", placeholder="40"))
expected_hct = expected_hct_input if expected_hct_input is not None else 40.0

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

# Marrow response label used later
marrow_response = "Unknown"
if rpi is not None:
    marrow_response = "Appropriate (RPI ≥2)" if rpi >= 2 else "Inadequate (RPI <2)"
elif retic_qual is not None:
    if retic_qual == "High":
        marrow_response = "Appropriate/High retic"
    elif retic_qual == "Low":
        marrow_response = "Inadequate/Low retic"

# ---------------- Step 2: Iron Studies ----------------
st.header("Step 2: Iron Studies")

iron_done = selected(st.selectbox("Are iron studies available?", ["Select…", "Yes", "No"], index=0))
ferritin = transferrin_sat = None

if iron_done == "Yes":
    colI1, colI2 = st.columns(2)
    with colI1:
        ferritin = to_float(st.text_input("Ferritin (ng/mL)", value="", placeholder="leave blank if unknown"))
    with colI2:
        transferrin_sat = to_float(st.text_input("Transferrin Saturation (%)", value="", placeholder="leave blank if unknown"))

# ---------------- Step 3: Vitamin & Hemolysis ----------------
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
        ldh = selected(st.selectbox("LDH", ["Select…", "Normal", "High", "Unknown"], index=0, help="Hemolysis pattern often: LDH ↑"))
    with colH2:
        haptoglobin = selected(st.selectbox("Haptoglobin", ["Select…", "Normal", "Low", "Unknown"], index=0, help="Hemolysis pattern often: haptoglobin ↓"))
    with colH3:
        indirect_bili = selected(st.selectbox("Indirect Bilirubin", ["Select…", "Normal", "High", "Unknown"], index=0, help="Hemolysis pattern often: indirect bili ↑"))

# ---------------- Step 4: Other Contributors ----------------
st.header("Step 4: Other Contributing Factors")

tsh_done = selected(st.selectbox("TSH available?", ["Select…", "Yes", "No"], index=0))
tsh = None
if tsh_done == "Yes":
    tsh = to_float(st.text_input("TSH (μIU/mL)", value="", placeholder="leave blank if unknown"))

egfr_done = selected(st.selectbox("eGFR available?", ["Select…", "Yes", "No"], index=0))
egfr = None
if egfr_done == "Yes":
    egfr = to_float(st.text_input("eGFR (mL/min/1.73m²)", value="", placeholder="leave blank if unknown"))

# ---------------- Step 5: Meds/Exposures ----------------
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
        help="This is a high-yield screen; it does not replace a full medication review.",
    )

# ---------------- Collect inputs for filtering/teaching ----------------
inputs = {
    "tsh": tsh,
    "egfr": egfr,
    "ferritin": ferritin,
    "tsat": transferrin_sat,
    "b12": b12,
    "folate": folate,
    "ldh": ldh,
    "haptoglobin": haptoglobin,
    "indirect_bili": indirect_bili,
    "retic_pct": retic_pct,
    "retic_qual": retic_qual,
    "rpi": rpi,
}
known = build_known(inputs)

# ---------------- Output ----------------
st.markdown("---")
st.subheader("🩺 Differential & Recommended Workup")

if mcv_cat is None:
    st.info(
        "Select an MCV category to generate the differential. "
        "Blank numeric fields are treated as **unknown (not 0)**."
    )
else:
    st.markdown(f"**Marrow response:** {marrow_response}")

    # Teaching Mode: Decision tree (narrowing)
    if teaching_mode:
        with st.expander("🧠 Decision tree (narrows as you enter data)", expanded=True):
            st.graphviz_chart(decision_tree_dot(mcv_cat, marrow_response, known, inputs))

    # Severity / triage prompts (informational, primary care framing)
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
                rule="Ferritin < 30 → depleted iron stores likely.",
                what_changes="If ferritin is normal/high but TSAT is low, consider inflammation/functional iron deficiency.",
            )
        elif ferritin is not None and ferritin >= 100 and transferrin_sat is not None and transferrin_sat < 20:
            add_item(
                dx,
                "Anemia of chronic inflammation with functional iron deficiency",
                "Ferritin may be normal/high with low TSAT in inflammatory states.",
                ["CRP/ESR (if inflammatory disease suspected)", "Review chronic inflammatory/infectious disease history"],
                rule="Ferritin ≥ 100 + TSAT < 20% can fit functional iron deficiency (context-dependent).",
                what_changes="If ferritin is low instead, iron deficiency becomes more likely.",
            )
        else:
            add_item(
                dx,
                "Thalassemia trait / hemoglobinopathy",
                "Microcytosis without clear low ferritin may suggest thal trait or mixed etiologies.",
                ["CBC indices review (RBC count, RDW)", "Peripheral smear", "Hemoglobin electrophoresis"],
                rule="Microcytosis not explained by iron deficiency → consider hemoglobinopathy evaluation.",
                what_changes="If ferritin is clearly low, prioritize iron deficiency pathway first.",
            )

    # Normocytic
    if mcv_cat == "Normocytic (80–100)":
        if marrow_response in ("Appropriate (RPI ≥2)", "Appropriate/High retic"):
            add_item(
                dx,
                "Blood loss (acute or occult)",
                "Appropriate/High retic suggests response to loss (or recovery phase).",
                ["Assess bleeding history", "Consider iron studies if not done", "Stool testing/GI evaluation when appropriate"],
                rule="RPI ≥ 2 (or high retic) suggests marrow response consistent with loss/hemolysis.",
                what_changes="If retic/RPI is low, shift toward underproduction causes.",
            )
            add_item(
                dx,
                "Hemolysis",
                "Appropriate/High retic can be seen in hemolysis; confirm with labs and smear.",
                ["Hemolysis panel (LDH, haptoglobin, bilirubin) if not done", "Peripheral smear", "DAT/Coombs if suspected AIHA"],
                rule="High retic with anemia → confirm hemolysis with LDH/haptoglobin/bili + smear.",
                what_changes="If hemolysis markers are normal and bleeding is unlikely, reconsider underproduction or mixed etiologies.",
            )
        else:
            add_item(
                dx,
                "Anemia of chronic inflammation",
                "Common hypoproliferative normocytic pattern in chronic disease.",
                ["CRP/ESR if clinically indicated", "Complete iron studies if missing", "Review chronic disease burden"],
                rule="Normocytic + low retic/RPI → underproduction pattern; chronic disease is common.",
                what_changes="If RPI is high, prioritize blood loss/hemolysis branches.",
            )
            if egfr is not None and egfr < 60:
                add_item(
                    dx,
                    "Anemia associated with CKD",
                    "CKD can cause hypoproliferative normocytic anemia; likelihood increases as eGFR declines.",
                    ["Confirm iron status (ferritin, TSAT)", "Assess for other contributors (B12/folate, bleeding)"],
                    rule="Lower eGFR increases likelihood of CKD-related underproduction.",
                    what_changes="If eGFR is normal, deprioritize CKD as primary driver.",
                )
            add_item(
                dx,
                "Bone marrow underproduction (consider if persistent or with other cytopenias)",
                "Low retic/other cytopenias can suggest marrow process or suppression.",
                ["Peripheral smear", "Repeat CBC trend", "Consider hematology referral if unexplained or if other cytopenias present"],
                rule="Low retic + (other cytopenias or abnormal smear) → consider marrow process.",
                what_changes="If isolated anemia with clear deficiency/bleeding source, marrow workup may be unnecessary.",
            )

    # Macrocytic
    if mcv_cat == "Macrocytic (>100)":
        if b12 is not None and b12 < 200:
            add_item(
                dx,
                "Vitamin B12 deficiency",
                "Low B12 supports megaloblastic anemia.",
                ["MMA ± homocysteine if borderline", "Assess diet/malabsorption risks", "Consider IF antibody if pernicious anemia suspected"],
                rule="B12 < 200 is a common low threshold (lab-specific).",
                what_changes="If B12 is borderline (e.g., 200–300), MMA can clarify functional deficiency.",
            )
        if folate is not None and folate < 4:
            add_item(
                dx,
                "Folate deficiency",
                "Low folate supports megaloblastic anemia.",
                ["Assess nutrition/alcohol use", "Review folate-antagonist meds/exposures"],
                rule="Low folate supports megaloblastic etiology.",
                what_changes="If folate is normal and macrocytosis persists, evaluate non-megaloblastic causes.",
            )
        if (b12 is None or b12 >= 200) and (folate is None or folate >= 4):
            add_item(
                dx,
                "Non-megaloblastic macrocytosis (alcohol, liver disease, hypothyroid, meds, marrow disorders)",
                "Macrocytosis without clear B12/folate deficiency suggests alternative etiologies.",
                ["TSH (if not done)", "LFTs", "Peripheral smear", "Consider hematology referral if persistent/unexplained"],
                rule="Macrocytosis with normal B12/folate → broaden to non-megaloblastic causes.",
                what_changes="If B12/folate later come back low, return to megaloblastic pathway.",
            )

    # Hemolysis triad (only if selected and consistent)
    if ldh == "High" and haptoglobin == "Low" and indirect_bili == "High":
        add_item(
            dx,
            "Hemolysis (supported by labs)",
            "LDH high + haptoglobin low + indirect bilirubin high is a classic hemolysis pattern.",
            ["Peripheral smear (schistocytes/spherocytes)", "DAT/Coombs", "Retic absolute count", "Consider G6PD if indicated"],
            rule="LDH↑ + hapto↓ + indirect bili↑ → hemolysis pattern.",
            what_changes="Smear/DAT helps distinguish microangiopathy vs AIHA vs other causes.",
        )

    # Hypothyroid (note: this won’t fire for low TSH)
    if tsh is not None and tsh > 5:
        add_item(
            dx,
            "Hypothyroidism-associated anemia",
            "Elevated TSH can contribute to normocytic/macrocytic anemia.",
            ["Repeat TSH/FT4 if needed", "Evaluate other causes in parallel (iron/B12/folate)"],
            rule="TSH elevated can be associated with anemia (mechanisms vary).",
            what_changes="If TSH is low or normal, do not attribute anemia to hypothyroidism.",
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

    dx_unique = dedupe_by_title(dx)

    if not dx_unique:
        st.info("Add more data to generate a differential.")
    else:
        # Less busy: show titles; details in expander unless Teaching Mode + show_all_details
        for i, item in enumerate(dx_unique[:10], start=1):
            title_line = f"{i}. {item['title']}"
            if not teaching_mode and not show_all_details:
                with st.expander(title_line, expanded=False):
                    if item["workup"]:
                        st.markdown("**Suggested next workup:**")
                        for w in item["workup"]:
                            w2 = suppress_or_annotate_workup_line(w, known, inputs, teaching=False)
                            if w2:
                                st.markdown(f"- {w2}")
            else:
                expanded_default = True if show_all_details else False
                with st.expander(title_line, expanded=expanded_default):
                    if item["rationale"]:
                        st.markdown(f"**Why:** {item['rationale']}")
                    if teaching_mode:
                        if item.get("rule"):
                            st.markdown(f"**Rule triggered:** {item['rule']}")
                        if item.get("what_changes"):
                            st.markdown(f"**What would change this:** {item['what_changes']}")
                    if item["workup"]:
                        st.markdown("**Suggested next workup:**")
                        for w in item["workup"]:
                            w2 = suppress_or_annotate_workup_line(w, known, inputs, teaching=teaching_mode)
                            if w2:
                                st.markdown(f"- {w2}")

    # Hematology referral guidance (primary care framing)
    st.markdown("---")
    st.subheader("📣 When to consider Hematology referral")

    referral_reasons = []

    if hb is not None and hb < 7 and (symptomatic_any in ("Yes", "Unknown") or high_risk_symptoms in ("Yes", "Unknown")):
        referral_reasons.append("Severe anemia with symptoms/high-risk features (coordinate urgent evaluation; hematology input may be appropriate).")

    if other_cytopenias in ("Yes", "Unknown"):
        referral_reasons.append("Anemia with other cytopenias (WBC/platelets low) or pancytopenia.")
    if smear_abnormal in ("Yes", "Unknown"):
        referral_reasons.append("Abnormal smear (e.g., blasts, schistocytes, marked dysplasia) or concerning morphology.")
    if (ldh == "High" and haptoglobin == "Low") or (indirect_bili == "High" and ldh == "High"):
        referral_reasons.append("Suspected hemolysis (especially if unexplained, severe, or with abnormal smear).")

    if mcv_cat == "Microcytic (<80)" and iron_done in (None, "No"):
        referral_reasons.append("Microcytic anemia with missing iron studies or unclear etiology after initial evaluation.")
    if mcv_cat == "Macrocytic (>100)" and vit_done in (None, "No"):
        referral_reasons.append("Macrocytic anemia without B12/folate evaluation or persistent macrocytosis without clear cause.")

    if referral_reasons:
        for r in referral_reasons[:8]:
            st.markdown(f"- {r}")
    else:
        st.caption("No specific referral triggers detected from entered data (limited by missing inputs).")

# Baseline items footer (now filtered so it doesn't tell you to check what you already entered)
st.markdown("---")
st.subheader("Baseline items to consider (if not already available)")

baseline = [
    "Repeat CBC with indices + RDW",
    "Peripheral smear review",
    "Reticulocyte % and/or absolute retic count",
    "Iron studies (ferritin, iron, TIBC, TSAT)",
    "B12 and folate",
    "TSH",
    "eGFR/creatinine",
    "Hemolysis markers (LDH, haptoglobin, indirect bilirubin)",
]

for b in baseline:
    b2 = suppress_or_annotate_workup_line(b, known, inputs, teaching=teaching_mode)
    if b2:
        st.markdown(f"- {b2}")

st.markdown("---")
st.caption("Created by Manal Ahmidouch – GMA Clinic • Med-Ed Track • For Educational Use Only")
