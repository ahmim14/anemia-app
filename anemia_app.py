import re
import streamlit as st

# ---------------- Page config ----------------
st.set_page_config(page_title="Anemia Evaluation Tool", layout="centered")

st.title("🩸 Anemia Evaluation Assistant")
st.markdown(
    "A stepwise tool to support anemia workup in primary care. "
    "**Educational use only.**"
)

# ---------------- Mode toggles ----------------
colM1, colM2 = st.columns([2, 1])
with colM1:
    teaching_mode = st.toggle("Teaching Mode (live tree + reasoning)", value=False)
with colM2:
    show_all_details = st.toggle("Show all details", value=False) if teaching_mode else False

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

def fmt(x, digits=2, suffix=""):
    if x is None:
        return "—"
    try:
        return f"{x:.{digits}f}{suffix}"
    except Exception:
        return f"{x}{suffix}"

def selected(x: str):
    """Return None if user hasn't selected a real option yet."""
    if x in (None, "", "Select…"):
        return None
    return x

def maturation_factor(hct):
    """
    Teaching table:
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

def add_item(lst, title, rationale="", workup=None, rule="", what_changes="", priority=50):
    lst.append(
        {
            "title": title,
            "rationale": rationale,
            "workup": workup or [],
            "rule": rule,
            "what_changes": what_changes,
            "priority": priority,
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

def dedupe_lines(lines):
    seen = set()
    out = []
    for x in lines:
        if x and x not in seen:
            out.append(x)
            seen.add(x)
    return out

# ---------------- “Already entered” tracking ----------------
def build_known(inputs: dict):
    known = {
        "tsh": inputs["tsh"] is not None,
        "egfr": inputs["egfr"] is not None,
        "ferritin": inputs["ferritin"] is not None,
        "tsat": inputs["tsat"] is not None,
        "b12": inputs["b12"] is not None,
        "folate": inputs["folate"] is not None,
        "ldh": inputs["ldh"] is not None,
        "haptoglobin": inputs["haptoglobin"] is not None,
        "indirect_bili": inputs["indirect_bili"] is not None,
        "retic_pct": inputs["retic_pct"] is not None,
        "retic_qual": inputs["retic_qual"] is not None,
        "rpi": inputs["rpi"] is not None,
    }
    # concept-level flags (what you actually want for filtering)
    known["iron_any"] = known["ferritin"] or known["tsat"]
    known["hemo_any"] = known["ldh"] or known["haptoglobin"] or known["indirect_bili"]
    known["retic_any"] = known["rpi"] or known["retic_pct"] or known["retic_qual"]
    known["vits_any"] = known["b12"] or known["folate"]
    return known

WORKUP_PATTERNS = [
    (re.compile(r"\bTSH\b", re.I), "tsh"),
    (re.compile(r"\beGFR\b|\bGFR\b|\bcreatinine\b", re.I), "egfr"),
    (re.compile(r"\bFerritin\b", re.I), "ferritin"),
    (re.compile(r"\bTSAT\b|\bTransferrin Saturation\b", re.I), "tsat"),
    (re.compile(r"\bIron studies\b|\bTIBC\b|\biron\b", re.I), "iron_any"),
    (re.compile(r"\bB12\b|\bVitamin B12\b", re.I), "b12"),
    (re.compile(r"\bFolate\b", re.I), "folate"),
    (re.compile(r"\bLDH\b", re.I), "ldh"),
    (re.compile(r"\bHaptoglobin\b", re.I), "haptoglobin"),
    (re.compile(r"\bIndirect Bilirubin\b|\bIndirect bili\b", re.I), "indirect_bili"),
    (re.compile(r"\bHemolysis panel\b|\bhemolysis markers\b", re.I), "hemo_any"),
    (re.compile(r"\bRetic\b|\bReticulocyte\b|\bRPI\b", re.I), "retic_any"),
]

def already_entered_label(key: str, inputs: dict):
    # lab-specific pretty labels for Teaching Mode
    if key == "tsh":
        return f"Already entered: TSH = {fmt(inputs['tsh'], 2)}"
    if key == "egfr":
        return f"Already entered: eGFR = {fmt(inputs['egfr'], 0)}"
    if key == "ferritin":
        return f"Already entered: Ferritin = {fmt(inputs['ferritin'], 0)}"
    if key == "tsat":
        return f"Already entered: TSAT = {fmt(inputs['tsat'], 0, '%')}"
    if key == "iron_any":
        parts = []
        if inputs["ferritin"] is not None:
            parts.append(f"Ferritin {fmt(inputs['ferritin'], 0)}")
        if inputs["tsat"] is not None:
            parts.append(f"TSAT {fmt(inputs['tsat'], 0, '%')}")
        joined = " • ".join(parts) if parts else "Iron studies available"
        return f"Already entered: {joined}"
    if key == "b12":
        return f"Already entered: B12 = {fmt(inputs['b12'], 0)}"
    if key == "folate":
        return f"Already entered: Folate = {fmt(inputs['folate'], 1)}"
    if key == "hemo_any":
        parts = []
        if inputs["ldh"] is not None:
            parts.append(f"LDH {inputs['ldh']}")
        if inputs["haptoglobin"] is not None:
            parts.append(f"Haptoglobin {inputs['haptoglobin']}")
        if inputs["indirect_bili"] is not None:
            parts.append(f"Indirect bili {inputs['indirect_bili']}")
        joined = " • ".join(parts) if parts else "Hemolysis markers available"
        return f"Already entered: {joined}"
    if key == "retic_any":
        if inputs["rpi"] is not None:
            return f"Already entered: RPI = {fmt(inputs['rpi'], 2)}"
        if inputs["retic_pct"] is not None:
            return f"Already entered: Retic % = {fmt(inputs['retic_pct'], 2, '%')}"
        if inputs["retic_qual"] is not None:
            return f"Already entered: Retic = {inputs['retic_qual']}"
        return "Already entered: Reticulocyte data available"
    return "Already entered."

def suppress_or_annotate_workup_line(line: str, known: dict, inputs: dict, teaching: bool):
    """
    - If the line asks for something already entered:
        - Clinician/POC view: hide it
        - Teaching view: replace with "Already entered: ..."
    """
    for pat, key in WORKUP_PATTERNS:
        if pat.search(line):
            if known.get(key, False):
                return already_entered_label(key, inputs) if teaching else None
            return line
    return line

# ---------------- Decision tree (Graphviz) ----------------
def decision_tree_dot(mcv_cat, marrow_response, known):
    def node_style(active=False):
        return 'shape="box", style="rounded,bold"' if active else 'shape="box", style="rounded"'

    def status_line(label, ok):
        return f"{label}: {'✅' if ok else '❓'}"

    micro = mcv_cat == "Microcytic (<80)"
    normo = mcv_cat == "Normocytic (80–100)"
    macro = mcv_cat == "Macrocytic (>100)"

    dot = [
        'digraph G {',
        'rankdir=TB;',
        'splines=false;',
        'nodesep=0.25;',
        'ranksep=0.3;',
    ]

    dot.append(f'Start [{node_style(True)} label="Start"];')
    dot.append(f'MCV [{node_style(mcv_cat is not None)} label="MCV: {mcv_cat or "Select…"}"];')
    dot.append('Start -> MCV;')

    dot.append(f'Micro [{node_style(micro)} label="Microcytic"];')
    dot.append(f'Normo [{node_style(normo)} label="Normocytic"];')
    dot.append(f'Macro [{node_style(macro)} label="Macrocytic"];')
    dot.append('MCV -> Micro; MCV -> Normo; MCV -> Macro;')

    # Micro branch
    dot.append(
        f'Iron [{node_style(micro and known.get("iron_any", False))} '
        f'label="{status_line("Iron studies", known.get("iron_any", False))}\\n'
        f'{status_line("Ferritin", known.get("ferritin", False))}\\n'
        f'{status_line("TSAT", known.get("tsat", False))}"];'
    )
    dot.append('Micro -> Iron;')

    # Normo branch
    dot.append(
        f'Retic [{node_style(normo and known.get("retic_any", False))} '
        f'label="{status_line("Retic/RPI", known.get("retic_any", False))}\\n'
        f'Marrow response: {marrow_response}"];'
    )
    dot.append('Normo -> Retic;')

    dot.append(
        f'Hemo [{node_style(normo and known.get("hemo_any", False))} '
        f'label="{status_line("Hemolysis markers", known.get("hemo_any", False))}\\n'
        f'{status_line("LDH", known.get("ldh", False))}\\n'
        f'{status_line("Haptoglobin", known.get("haptoglobin", False))}\\n'
        f'{status_line("Indirect bili", known.get("indirect_bili", False))}"];'
    )
    dot.append('Retic -> Hemo;')

    # Macro branch
    dot.append(
        f'Vits [{node_style(macro and known.get("vits_any", False))} '
        f'label="{status_line("B12/Folate", known.get("vits_any", False))}\\n'
        f'{status_line("B12", known.get("b12", False))}\\n'
        f'{status_line("Folate", known.get("folate", False))}"];'
    )
    dot.append('Macro -> Vits;')

    dot.append(
        f'Other [{node_style(macro)} '
        f'label="{status_line("TSH", known.get("tsh", False))}\\n'
        f'{status_line("Consider LFTs/smear/meds", True)}"];'
    )
    dot.append('Vits -> Other;')

    dot.append('}')
    return "\n".join(dot)

# ---------------- Step 0: Symptoms & Severity ----------------
st.header("Symptoms & Severity")
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
st.header("CBC Basics")
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
            help="This is the main branching step for anemia evaluation.",
        )
    )
    rdw = selected(
        st.selectbox(
            "RDW",
            ["Select…", "Normal", "High", "Unknown"],
            index=0,
            help="High RDW can support mixed/deficiency etiologies (context-dependent).",
        )
    )

# ✅ FIX: set defaults up front (expander code always runs, open or closed)
other_cytopenias = None
rapid_onset = None
smear_abnormal = None

with st.expander("CBC context (optional)", expanded=False):
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

# ---------------- Reticulocytes + RPI ----------------
st.subheader("Reticulocytes")
expand_retic = (mcv_cat == "Normocytic (80–100)")
with st.expander("Retic / RPI (key for normocytic anemia)", expanded=expand_retic):
    retic_mode = st.radio(
        "Reticulocyte input",
        ["Qualitative (Low/Normal/High)", "Numeric (%)"],
        horizontal=True,
        index=0,
        help="Retic/RPI helps separate underproduction vs hemolysis/bleeding physiology.",
    )

    retic_qual = None
    retic_pct = None

    if retic_mode == "Qualitative (Low/Normal/High)":
        retic_qual = selected(st.selectbox("Reticulocyte count", ["Select…", "Low", "Normal", "High"], index=0))
    else:
        retic_pct = to_float(st.text_input("Reticulocyte %", value="", placeholder="leave blank if unknown"))

    st.markdown("**Reticulocyte Index (Corrected Retic) & RPI**")
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
if "rpi" in locals() and rpi is not None:
    marrow_response = "Appropriate (RPI ≥2)" if rpi >= 2 else "Inadequate (RPI <2)"
elif "retic_qual" in locals() and retic_qual is not None:
    if retic_qual == "High":
        marrow_response = "Appropriate/High retic"
    elif retic_qual == "Low":
        marrow_response = "Inadequate/Low retic"

# ---------------- Labs: Iron / Vitamins / Hemolysis / Other ----------------
st.header("Key labs (enter what you have)")

with st.expander("Iron studies", expanded=(mcv_cat == "Microcytic (<80)")):
    ferritin = to_float(st.text_input("Ferritin (ng/mL)", value="", placeholder="leave blank if unknown"))
    transferrin_sat = to_float(st.text_input("Transferrin Saturation (%)", value="", placeholder="leave blank if unknown"))

with st.expander("B12 / Folate", expanded=(mcv_cat == "Macrocytic (>100)")):
    b12 = to_float(st.text_input("Vitamin B12 (pg/mL)", value="", placeholder="leave blank if unknown"))
    folate = to_float(st.text_input("Folate (ng/mL)", value="", placeholder="leave blank if unknown"))

expand_hemo = marrow_response in ("Appropriate (RPI ≥2)", "Appropriate/High retic")
with st.expander("Hemolysis markers", expanded=expand_hemo):
    colH1, colH2, colH3 = st.columns(3)
    with colH1:
        ldh = selected(st.selectbox("LDH", ["Select…", "Normal", "High", "Unknown"], index=0, help="Hemolysis pattern often: LDH ↑"))
    with colH2:
        haptoglobin = selected(st.selectbox("Haptoglobin", ["Select…", "Normal", "Low", "Unknown"], index=0, help="Hemolysis pattern often: haptoglobin ↓"))
    with colH3:
        indirect_bili = selected(st.selectbox("Indirect Bilirubin", ["Select…", "Normal", "High", "Unknown"], index=0, help="Hemolysis pattern often: indirect bili ↑"))

with st.expander("Other contributors (TSH / kidney)", expanded=(mcv_cat in ("Macrocytic (>100)", "Normocytic (80–100)"))):
    tsh = to_float(st.text_input("TSH (μIU/mL)", value="", placeholder="leave blank if unknown"))
    egfr = to_float(st.text_input("eGFR (mL/min/1.73m²)", value="", placeholder="leave blank if unknown"))

# ---------------- Meds/Exposures ----------------
with st.expander("High-yield medications / exposures (optional)", expanded=False):
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
        help="High-yield screen; does not replace a full medication review.",
    )

# ---------------- Collect inputs & compute known flags ----------------
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
    "retic_pct": locals().get("retic_pct", None),
    "retic_qual": locals().get("retic_qual", None),
    "rpi": locals().get("rpi", None),
}
known = build_known(inputs)

# ---------------- Sidebar live tree (Teaching Mode) ----------------
if teaching_mode:
    with st.sidebar:
        st.subheader("🧠 Live decision tree")
        st.graphviz_chart(decision_tree_dot(mcv_cat, marrow_response, known))
        st.caption("Updates as you enter data.")

# ---------------- Output ----------------
st.markdown("---")
st.header("POC Summary")

def next_most_informative(mcv_cat, marrow_response, known):
    """
    One high-yield next step that narrows the tree (and reduces busy output).
    Returns a single string (may be suppressed later if already entered).
    """
    if mcv_cat == "Microcytic (<80)":
        if not known["iron_any"]:
            return "Iron studies (Ferritin, TSAT)"
        return "Assess bleeding source risk; consider GI/gyne evaluation contextually"
    if mcv_cat == "Normocytic (80–100)":
        if not known["retic_any"]:
            return "Reticulocyte count / RPI"
        if marrow_response in ("Appropriate (RPI ≥2)", "Appropriate/High retic") and not known["hemo_any"]:
            return "Hemolysis markers (LDH, haptoglobin, indirect bilirubin) + peripheral smear"
        return "Trend CBC and review chronic disease/CKD contribution"
    if mcv_cat == "Macrocytic (>100)":
        if not (known["b12"] and known["folate"]):
            return "B12 and folate"
        if not known["tsh"]:
            return "TSH"
        return "Review meds/alcohol; consider LFTs + smear; refer if persistent/unexplained"
    return "Select an MCV category to start."

# If no MCV, stop early
if mcv_cat is None:
    st.info("Select an MCV category above to generate a point-of-care summary and differential.")
else:
    st.markdown(f"**Working category:** {mcv_cat}  \n**Marrow response:** {marrow_response}")

    # Triage prompts (only if triggered)
    triage_msgs = []
    if hb is not None:
        if hb < 6:
            triage_msgs.append("Hb < 6 g/dL: may warrant urgent evaluation depending on symptoms/comorbidities.")
        elif hb < 7:
            triage_msgs.append("Hb < 7 g/dL: transfusion is often considered in many settings, especially if symptomatic.")
        elif hb < 8 and cvd in ("Yes", "Unknown"):
            triage_msgs.append("Hb < 8 g/dL with cardiovascular disease/possible ischemic symptoms: clinicians may consider a higher transfusion threshold.")

    if high_risk_symptoms in ("Yes", "Unknown") or active_bleeding in ("Yes", "Unknown") or rapid_onset in ("Yes", "Unknown"):
        triage_msgs.append("High-risk features or possible acute process: consider prompt clinical evaluation (urgent care/ED depending on severity/context).")

    if egfr is not None and egfr < 30:
        triage_msgs.append("Advanced CKD (eGFR <30) reduces physiologic reserve; symptoms/trajectory often matter more than a single Hb cutoff.")

    if triage_msgs:
        st.warning("**Red flags / urgency (informational):**\n- " + "\n- ".join(triage_msgs))

    # Build differential
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
                priority=10,
            )
        elif ferritin is not None and ferritin >= 100 and transferrin_sat is not None and transferrin_sat < 20:
            add_item(
                dx,
                "Anemia of chronic inflammation with functional iron deficiency",
                "Ferritin may be normal/high with low TSAT in inflammatory states.",
                ["CRP/ESR (if inflammatory disease suspected)", "Review chronic inflammatory/infectious disease history"],
                rule="Ferritin ≥ 100 + TSAT < 20% can fit functional iron deficiency (context-dependent).",
                what_changes="If ferritin is low instead, iron deficiency becomes more likely.",
                priority=20,
            )
        else:
            add_item(
                dx,
                "Thalassemia trait / hemoglobinopathy",
                "Microcytosis without clear low ferritin may suggest thal trait or mixed etiologies.",
                ["CBC indices review (RBC count, RDW)", "Peripheral smear", "Hemoglobin electrophoresis"],
                rule="Microcytosis not explained by iron deficiency → consider hemoglobinopathy evaluation.",
                what_changes="If ferritin is clearly low, prioritize iron deficiency pathway first.",
                priority=30,
            )

    # Normocytic
    if mcv_cat == "Normocytic (80–100)":
        if marrow_response in ("Appropriate (RPI ≥2)", "Appropriate/High retic"):
            add_item(
                dx,
                "Blood loss (acute or occult)",
                "Appropriate/High retic suggests response to loss (or recovery phase).",
                ["Assess bleeding history", "Iron studies (Ferritin, TSAT)", "Stool testing/GI evaluation when appropriate"],
                rule="RPI ≥ 2 (or high retic) supports a response consistent with blood loss/hemolysis.",
                what_changes="If retic/RPI is low, shift toward underproduction causes.",
                priority=15,
            )
            add_item(
                dx,
                "Hemolysis",
                "Appropriate/High retic can be seen in hemolysis; confirm with labs and smear.",
                ["Hemolysis markers (LDH, haptoglobin, indirect bilirubin)", "Peripheral smear", "DAT/Coombs if suspected AIHA"],
                rule="High retic + anemia → evaluate for hemolysis with markers and smear.",
                what_changes="If hemolysis markers are normal and bleeding is unlikely, consider underproduction/mixed etiologies.",
                priority=18,
            )
        else:
            add_item(
                dx,
                "Anemia of chronic inflammation",
                "Common hypoproliferative normocytic pattern in chronic disease.",
                ["CRP/ESR if clinically indicated", "Iron studies (Ferritin, TSAT)", "Review chronic disease burden"],
                rule="Normocytic + low retic/RPI → underproduction pattern; chronic disease is common.",
                what_changes="If RPI is high, prioritize blood loss/hemolysis branches.",
                priority=20,
            )
            if egfr is not None and egfr < 60:
                add_item(
                    dx,
                    "Anemia associated with CKD",
                    "CKD can cause hypoproliferative normocytic anemia; likelihood increases as eGFR declines.",
                    ["Iron studies (Ferritin, TSAT)", "Evaluate other contributors (B12/folate, bleeding)"],
                    rule="Lower eGFR increases likelihood of CKD-related underproduction.",
                    what_changes="If eGFR is normal, deprioritize CKD as primary driver.",
                    priority=22,
                )
            add_item(
                dx,
                "Bone marrow underproduction (consider if persistent or with other cytopenias)",
                "Low retic/other cytopenias can suggest marrow process or suppression.",
                ["Peripheral smear", "Repeat CBC trend", "Consider hematology referral if unexplained or if other cytopenias present"],
                rule="Low retic + (other cytopenias or abnormal smear) → consider marrow process.",
                what_changes="If isolated anemia with clear deficiency/bleeding source, marrow workup may be unnecessary.",
                priority=28,
            )

    # Macrocytic
    if mcv_cat == "Macrocytic (>100)":
        if b12 is not None and b12 < 200:
            add_item(
                dx,
                "Vitamin B12 deficiency",
                "Low B12 supports megaloblastic anemia.",
                ["MMA ± homocysteine if borderline", "Assess diet/malabsorption risks", "Consider IF antibody if pernicious anemia suspected"],
                rule="B12 < 200 is a commonly used low threshold (lab-specific).",
                what_changes="If B12 is borderline (200–300), MMA can clarify functional deficiency.",
                priority=12,
            )
        if folate is not None and folate < 4:
            add_item(
                dx,
                "Folate deficiency",
                "Low folate supports megaloblastic anemia.",
                ["Assess nutrition/alcohol use", "Review folate-antagonist meds/exposures"],
                rule="Low folate supports megaloblastic etiology.",
                what_changes="If folate is normal and macrocytosis persists, evaluate non-megaloblastic causes.",
                priority=15,
            )
        if (b12 is None or b12 >= 200) and (folate is None or folate >= 4):
            add_item(
                dx,
                "Non-megaloblastic macrocytosis (alcohol, liver disease, hypothyroid, meds, marrow disorders)",
                "Macrocytosis without clear B12/folate deficiency suggests alternative etiologies.",
                ["TSH", "LFTs", "Peripheral smear", "Consider hematology referral if persistent/unexplained"],
                rule="Macrocytosis with normal B12/folate → broaden to non-megaloblastic causes.",
                what_changes="If B12/folate later come back low, return to megaloblastic pathway.",
                priority=25,
            )

    # Hemolysis triad
    if ldh == "High" and haptoglobin == "Low" and indirect_bili == "High":
        add_item(
            dx,
            "Hemolysis (supported by markers)",
            "LDH high + haptoglobin low + indirect bilirubin high is a classic hemolysis pattern.",
            ["Peripheral smear (schistocytes/spherocytes)", "DAT/Coombs", "Reticulocyte count / RPI", "Consider G6PD if indicated"],
            rule="LDH↑ + hapto↓ + indirect bili↑ → hemolysis pattern.",
            what_changes="Smear/DAT helps distinguish microangiopathy vs AIHA vs other causes.",
            priority=8,
        )

    # Hypothyroid (only if TSH high)
    if tsh is not None and tsh > 5:
        add_item(
            dx,
            "Hypothyroidism-associated anemia",
            "Elevated TSH can contribute to normocytic/macrocytic anemia.",
            ["Repeat TSH/FT4 if needed", "Evaluate other causes in parallel (iron/B12/folate)"],
            rule="TSH elevated can be associated with anemia (mechanisms vary).",
            what_changes="If TSH is low/normal, do not attribute anemia to hypothyroidism.",
            priority=35,
        )

    # Exposure-driven additions (POC-friendly)
    if "NSAIDs / aspirin (chronic)" in exposures:
        add_item(
            dx,
            "Medication-associated occult GI blood loss (NSAIDs/ASA)",
            "Chronic NSAID/ASA use can contribute to ulcer/gastritis-related blood loss.",
            ["Assess GI symptoms", "Iron studies (Ferritin, TSAT)", "Review need for NSAID/ASA"],
            priority=40,
        )
    if "PPI (long-term)" in exposures or "Metformin (long-term)" in exposures:
        add_item(
            dx,
            "Medication-associated B12 deficiency risk (PPI/metformin)",
            "Long-term PPI/metformin may reduce B12 absorption in some patients.",
            ["B12 and folate", "MMA if borderline", "Assess neuropathy/glossitis"],
            priority=40,
        )
    if "Alcohol use (heavy)" in exposures:
        add_item(
            dx,
            "Alcohol-related macrocytosis / nutritional deficiency",
            "Alcohol can cause macrocytosis and contribute to folate deficiency.",
            ["LFTs", "B12 and folate", "Consider counseling/support resources"],
            priority=45,
        )

    # Sort + dedupe
    dx_sorted = sorted(dx, key=lambda x: x.get("priority", 50))
    dx_unique = dedupe_by_title(dx_sorted)

    # ---- POC: Top etiologies ----
    top_dx = dx_unique[:3] if dx_unique else []

    colP1, colP2 = st.columns([1, 1])
    with colP1:
        st.subheader("Most likely etiologies (based on entered data)")
        if not top_dx:
            st.info("Enter more data to generate a ranked differential.")
        else:
            for i, item in enumerate(top_dx, 1):
                st.markdown(f"**{i}. {item['title']}**")

    # ---- POC: Next steps (filtered) ----
    with colP2:
        st.subheader("Next steps (POC)")
        steps = []

        # One “most informative next input”
        steps.append(next_most_informative(mcv_cat, marrow_response, known))

        # Add workup from top etiologies
        for item in top_dx:
            for w in item.get("workup", []):
                steps.append(w)

        # Filter out things already entered
        filtered_steps = []
        for s in steps:
            s2 = suppress_or_annotate_workup_line(s, known, inputs, teaching=False)
            if s2:
                filtered_steps.append(s2)

        filtered_steps = dedupe_lines(filtered_steps)[:6]  # cap to keep POC clean

        if filtered_steps:
            for s in filtered_steps:
                st.markdown(f"- {s}")
        else:
            st.caption("No additional steps suggested based on entered data (or inputs already provided).")

    # ---- Missing essentials (filtered) ----
    with st.expander("If not already available: missing essentials", expanded=False):
        essentials = [
            "Peripheral smear review",
            "Reticulocyte count / RPI",
            "Iron studies (Ferritin, TSAT)",
            "B12 and folate",
            "Hemolysis markers (LDH, haptoglobin, indirect bilirubin)",
            "TSH",
            "eGFR/creatinine",
        ]
        out_lines = []
        for e in essentials:
            e2 = suppress_or_annotate_workup_line(e, known, inputs, teaching=False)
            if e2:
                out_lines.append(e2)
        out_lines = dedupe_lines(out_lines)
        if out_lines:
            for e in out_lines:
                st.markdown(f"- {e}")
        else:
            st.caption("All core lab categories appear to be already entered (limited by non-lab inputs).")

    # ---------------- Detailed Differential ----------------
    st.markdown("---")
    st.header("Differential details")

    if not dx_unique:
        st.info("Add more data to generate a differential.")
    else:
        for i, item in enumerate(dx_unique[:10], start=1):
            title_line = f"{i}. {item['title']}"
            expanded_default = show_all_details if teaching_mode else False

            with st.expander(title_line, expanded=expanded_default):
                if item.get("rationale"):
                    st.markdown(f"**Why:** {item['rationale']}")

                if teaching_mode:
                    if item.get("rule"):
                        st.markdown(f"**Rule triggered:** {item['rule']}")
                    if item.get("what_changes"):
                        st.markdown(f"**What would change this:** {item['what_changes']}")

                # Workup, filtered/annotated
                workup_lines = []
                for w in item.get("workup", []):
                    w2 = suppress_or_annotate_workup_line(w, known, inputs, teaching=teaching_mode)
                    if w2:
                        workup_lines.append(w2)

                workup_lines = dedupe_lines(workup_lines)

                if workup_lines:
                    st.markdown("**Suggested next workup:**")
                    for w in workup_lines:
                        st.markdown(f"- {w}")

    # ---------------- Referral triggers (kept simple) ----------------
    st.markdown("---")
    with st.expander("📣 When to consider Hematology referral", expanded=False):
        referral_reasons = []

        if hb is not None and hb < 7 and (symptomatic_any in ("Yes", "Unknown") or high_risk_symptoms in ("Yes", "Unknown")):
            referral_reasons.append("Severe anemia with symptoms/high-risk features (coordinate urgent evaluation; hematology input may be appropriate).")

        if other_cytopenias in ("Yes", "Unknown"):
            referral_reasons.append("Anemia with other cytopenias (WBC/platelets low) or pancytopenia.")
        if smear_abnormal in ("Yes", "Unknown"):
            referral_reasons.append("Abnormal smear (e.g., blasts, schistocytes, marked dysplasia) or concerning morphology.")
        if (ldh == "High" and haptoglobin == "Low") or (indirect_bili == "High" and ldh == "High"):
            referral_reasons.append("Suspected hemolysis (especially if unexplained, severe, or with abnormal smear).")

        if mcv_cat == "Microcytic (<80)" and not known["iron_any"]:
            referral_reasons.append("Microcytic anemia with missing iron studies or unclear etiology after initial evaluation.")
        if mcv_cat == "Macrocytic (>100)" and not (known["b12"] and known["folate"]):
            referral_reasons.append("Macrocytic anemia without B12/folate evaluation or persistent macrocytosis without clear cause.")

        if referral_reasons:
            for r in referral_reasons[:10]:
                st.markdown(f"- {r}")
        else:
            st.caption("No specific referral triggers detected from entered data (limited by missing inputs).")

st.markdown("---")
st.caption("Created by Manal Ahmidouch – GMA Clinic • Med-Ed Track • For Educational Use Only")
