import re
import streamlit as st

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


# =========================
# Helpers
# =========================
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
    if x in (None, "", "Select...", "Select…"):
        return None
    return x


def titlecase_first(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return s
    return s[0].upper() + s[1:]


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
        x = (x or "").strip()
        if x and x not in seen:
            out.append(x)
            seen.add(x)
    return out


# =========================
# “Already entered” tracking
# =========================
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
    known["iron_any"] = known["ferritin"] or known["tsat"]
    known["hemo_any"] = known["ldh"] or known["haptoglobin"] or known["indirect_bili"]
    known["retic_any"] = known["rpi"] or known["retic_pct"] or known["retic_qual"]
    known["vits_any"] = known["b12"] or known["folate"]
    return known


def already_entered_label(key: str, inputs: dict):
    if key == "tsh":
        return f"Already entered: TSH = {fmt(inputs['tsh'], 2)}"
    if key == "egfr":
        return f"Already entered: eGFR = {fmt(inputs['egfr'], 0)}"
    if key == "ferritin":
        return f"Already entered: Ferritin = {fmt(inputs['ferritin'], 0)}"
    if key == "tsat":
        return f"Already entered: TSAT = {fmt(inputs['tsat'], 0, '%')}"
    if key == "b12":
        return f"Already entered: B12 = {fmt(inputs['b12'], 0)}"
    if key == "folate":
        return f"Already entered: Folate = {fmt(inputs['folate'], 1)}"
    if key == "ldh":
        return f"Already entered: LDH = {inputs['ldh']}"
    if key == "haptoglobin":
        return f"Already entered: Haptoglobin = {inputs['haptoglobin']}"
    if key == "indirect_bili":
        return f"Already entered: Indirect bilirubin = {inputs['indirect_bili']}"
    if key == "retic_any":
        if inputs["rpi"] is not None:
            return f"Already entered: RPI = {fmt(inputs['rpi'], 2)}"
        if inputs["retic_pct"] is not None:
            return f"Already entered: Retic % = {fmt(inputs['retic_pct'], 2, '%')}"
        if inputs["retic_qual"] is not None:
            return f"Already entered: Retic = {inputs['retic_qual']}"
        return "Already entered: Reticulocyte data available"
    return "Already entered."


# =========================
# Suggestion expansion/filtering (hide items already entered)
# =========================
def expand_and_filter_suggestion(line: str, known: dict, inputs: dict, teaching: bool):
    if not line:
        return []
    s = line.strip()

    # Actions should not be suppressed as "already entered"
    if s.lower().startswith("action:"):
        core = s.split(":", 1)[1].strip() if ":" in s else s
        return [titlecase_first(core)]

    # --- Iron studies bundle ---
    if re.search(r"\biron studies\b|\bTIBC\b|\bTSAT\b|\bferritin\b", s, flags=re.I):
        if re.search(r"\biron studies\b", s, flags=re.I):
            missing = []
            if not known.get("ferritin", False):
                missing.append("Ferritin")
            if not known.get("tsat", False):
                missing.append("Transferrin saturation (TSAT)")
            if missing:
                return missing
            if teaching:
                parts = []
                if inputs.get("ferritin") is not None:
                    parts.append(already_entered_label("ferritin", inputs))
                if inputs.get("tsat") is not None:
                    parts.append(already_entered_label("tsat", inputs))
                return parts if parts else ["Already entered: Iron studies available"]
            return []

        if re.search(r"\bferritin\b", s, flags=re.I) and not re.search(r"\bTSAT\b|\btransferrin\b", s, flags=re.I):
            if known.get("ferritin", False):
                return [already_entered_label("ferritin", inputs)] if teaching else []
            return ["Ferritin"]

        if re.search(r"\bTSAT\b|\btransferrin saturation\b", s, flags=re.I) and not re.search(r"\bferritin\b", s, flags=re.I):
            if known.get("tsat", False):
                return [already_entered_label("tsat", inputs)] if teaching else []
            return ["Transferrin saturation (TSAT)"]

        return [s]

    # --- B12/Folate bundle ---
    if re.search(r"\bB12\b|\bvitamin b12\b|\bfolate\b", s, flags=re.I):
        mentions_b12 = bool(re.search(r"\bB12\b|\bvitamin b12\b", s, flags=re.I))
        mentions_folate = bool(re.search(r"\bfolate\b", s, flags=re.I))

        if mentions_b12 and mentions_folate:
            missing = []
            if not known.get("b12", False):
                missing.append("Vitamin B12")
            if not known.get("folate", False):
                missing.append("Folate")
            if missing:
                return missing
            return (
                [already_entered_label("b12", inputs), already_entered_label("folate", inputs)]
                if teaching
                else []
            )

        if mentions_b12 and not mentions_folate:
            if known.get("b12", False):
                return [already_entered_label("b12", inputs)] if teaching else []
            return ["Vitamin B12"]

        if mentions_folate and not mentions_b12:
            if known.get("folate", False):
                return [already_entered_label("folate", inputs)] if teaching else []
            return ["Folate"]

        return [s]

    # --- Hemolysis markers bundle ---
    if re.search(
        r"\bhemolysis markers\b|\bhemolysis panel\b|\bLDH\b|\bhaptoglobin\b|\bindirect\b|\bbilirubin\b",
        s,
        flags=re.I,
    ):
        if re.search(r"\bhemolysis markers\b|\bhemolysis panel\b", s, flags=re.I):
            missing = []
            if not known.get("ldh", False):
                missing.append("LDH")
            if not known.get("haptoglobin", False):
                missing.append("Haptoglobin")
            if not known.get("indirect_bili", False):
                missing.append("Indirect bilirubin")
            if missing:
                return missing
            if teaching:
                parts = []
                if inputs.get("ldh") is not None:
                    parts.append(already_entered_label("ldh", inputs))
                if inputs.get("haptoglobin") is not None:
                    parts.append(already_entered_label("haptoglobin", inputs))
                if inputs.get("indirect_bili") is not None:
                    parts.append(already_entered_label("indirect_bili", inputs))
                return parts if parts else ["Already entered: Hemolysis markers available"]
            return []

        if re.search(r"\bLDH\b", s, flags=re.I):
            if known.get("ldh", False):
                return [already_entered_label("ldh", inputs)] if teaching else []
            return ["LDH"]

        if re.search(r"\bhaptoglobin\b", s, flags=re.I):
            if known.get("haptoglobin", False):
                return [already_entered_label("haptoglobin", inputs)] if teaching else []
            return ["Haptoglobin"]

        if re.search(r"\bindirect\b|\bbilirubin\b", s, flags=re.I):
            if known.get("indirect_bili", False):
                return [already_entered_label("indirect_bili", inputs)] if teaching else []
            return ["Indirect bilirubin"]

        return [s]

    # --- Retic/RPI ---
    if re.search(r"\bretic\b|\breticulocyte\b|\bRPI\b", s, flags=re.I):
        if known.get("retic_any", False):
            return [already_entered_label("retic_any", inputs)] if teaching else []
        return ["Reticulocyte count / RPI"]

    # --- TSH ---
    if re.search(r"\bTSH\b", s, flags=re.I):
        if known.get("tsh", False):
            return [already_entered_label("tsh", inputs)] if teaching else []
        return ["TSH"]

    # --- eGFR/Cr ---
    if re.search(r"\beGFR\b|\bGFR\b|\bcreatinine\b", s, flags=re.I):
        if known.get("egfr", False):
            return [already_entered_label("egfr", inputs)] if teaching else []
        return ["eGFR/creatinine"]

    return [s]


def expand_filter_list(lines, known, inputs, teaching):
    out = []
    for line in lines:
        out.extend(expand_and_filter_suggestion(line, known, inputs, teaching))
    return dedupe_lines(out)


# =========================
# Completeness indicator (badge only, no fraction)
# =========================
def completeness_badge(known: dict):
    groups = {
        "Iron studies": known.get("iron_any", False),
        "Retic/RPI": known.get("retic_any", False),
        "B12/Folate": known.get("vits_any", False),
        "Hemolysis markers": known.get("hemo_any", False),
        "TSH or eGFR": known.get("tsh", False) or known.get("egfr", False),
    }
    n_have = sum(1 for v in groups.values() if v)

    if n_have <= 1:
        return "Low", "#dc2626"     # red
    if n_have <= 3:
        return "Medium", "#f59e0b"  # amber
    return "High", "#16a34a"       # green


def pill(text, color_hex):
    safe = str(text).replace("<", "&lt;").replace(">", "&gt;")
    return f"""
    <span style="
        display:inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        background: {color_hex};
        color: white;
        font-size: 0.9rem;
        line-height: 1.2;
        ">
        {safe}
    </span>
    """


# =========================
# Teaching: Next-most-informative + breadcrumb
# =========================
def next_most_informative(mcv_cat, marrow_response, known):
    if mcv_cat == "Microcytic (<80)":
        if not known["iron_any"]:
            return ["Iron studies (Ferritin, TSAT)"]
        return ["Action: assess bleeding source risk (GI/GYN) as appropriate"]
    if mcv_cat == "Normocytic (80–100)":
        if not known["retic_any"]:
            return ["Reticulocyte count / RPI"]
        if marrow_response in ("Appropriate (RPI ≥2)", "Appropriate/High retic") and not known["hemo_any"]:
            return ["Hemolysis markers (LDH, haptoglobin, indirect bilirubin)", "Peripheral smear review"]
        return ["Action: review chronic disease/CKD contribution; trend CBC"]
    if mcv_cat == "Macrocytic (>100)":
        if not (known["b12"] and known["folate"]):
            return ["B12 and folate"]
        if not known["tsh"]:
            return ["TSH"]
        return ["Action: review meds/alcohol; consider LFTs + smear; refer if persistent/unexplained"]
    return ["Select an MCV category"]


def breadcrumb_path(mcv_cat, marrow_response, known, inputs):
    if mcv_cat is None:
        return "Start -> Select MCV"
    if mcv_cat == "Microcytic (<80)":
        if not known["iron_any"]:
            return "Start -> Microcytic -> (Need iron studies)"
        if inputs["ferritin"] is not None and inputs["ferritin"] < 30:
            return "Start -> Microcytic -> Iron deficiency pattern"
        return "Start -> Microcytic -> Iron deficiency vs inflammation vs thalassemia"
    if mcv_cat == "Normocytic (80–100)":
        if not known["retic_any"]:
            return "Start -> Normocytic -> (Need retic/RPI)"
        if marrow_response in ("Appropriate (RPI ≥2)", "Appropriate/High retic"):
            if not known["hemo_any"]:
                return "Start -> Normocytic -> Appropriate retic -> (Need hemolysis markers/smear)"
            return "Start -> Normocytic -> Appropriate retic -> Blood loss vs hemolysis"
        return "Start -> Normocytic -> Inadequate retic -> Underproduction"
    if mcv_cat == "Macrocytic (>100)":
        if not (known["b12"] and known["folate"]):
            return "Start -> Macrocytic -> (Need B12/folate)"
        return "Start -> Macrocytic -> B12/folate not low -> Broaden causes"
    return "Start"


# =========================
# Decision tree (Graphviz)
# =========================
def decision_tree_dot(mcv_cat, marrow_response, known):
    def node(label, active=False, dim=False):
        style = 'shape="box", style="rounded'
        style += ',bold"' if active else '"'
        color = ' color="gray" fontcolor="gray"' if dim else ""
        safe_label = str(label).replace('"', "'")
        safe_label = safe_label.replace("\n", "\\n")
        return f'[{style}{color} label="{safe_label}"];'

    def status(label, ok):
        return f"{label}: {'✅' if ok else '❓'}"

    micro = mcv_cat == "Microcytic (<80)"
    normo = mcv_cat == "Normocytic (80–100)"
    macro = mcv_cat == "Macrocytic (>100)"
    mcv_chosen = mcv_cat is not None

    dim_micro = mcv_chosen and not micro
    dim_normo = mcv_chosen and not normo
    dim_macro = mcv_chosen and not macro

    mcv_label_value = mcv_cat if mcv_cat is not None else "Select..."
    mcv_node_label = f"MCV: {mcv_label_value}"

    nxt = next_most_informative(mcv_cat, marrow_response, known)
    nxt_label = "NEXT MOST INFORMATIVE:\n" + "\n".join(nxt)

    dot = [
        "digraph G {",
        "rankdir=TB;",
        "splines=false;",
        "nodesep=0.25;",
        "ranksep=0.3;",
        'node [fontname="Helvetica"];',
    ]

    dot.append(f'Start {node("Start", active=True)}')
    dot.append(f"MCV {node(mcv_node_label, active=mcv_chosen)}")
    dot.append("Start -> MCV;")

    dot.append(f'Micro {node("Microcytic", active=micro, dim=dim_micro)}')
    dot.append(f'Normo {node("Normocytic", active=normo, dim=dim_normo)}')
    dot.append(f'Macro {node("Macrocytic", active=macro, dim=dim_macro)}')
    dot.append("MCV -> Micro; MCV -> Normo; MCV -> Macro;")

    iron_label = "\n".join(
        [
            status("Iron studies", known["iron_any"]),
            status("Ferritin", known["ferritin"]),
            status("TSAT", known["tsat"]),
        ]
    )
    dot.append(f"Iron {node(iron_label, active=(micro and known['iron_any']), dim=dim_micro)}")
    dot.append("Micro -> Iron;")

    retic_label = "\n".join([status("Retic/RPI", known["retic_any"]), f"Marrow: {marrow_response}"])
    dot.append(f"Retic {node(retic_label, active=(normo and known['retic_any']), dim=dim_normo)}")
    dot.append("Normo -> Retic;")

    hemo_label = "\n".join(
        [
            status("Hemolysis markers", known["hemo_any"]),
            status("LDH", known["ldh"]),
            status("Haptoglobin", known["haptoglobin"]),
            status("Indirect bili", known["indirect_bili"]),
        ]
    )
    dot.append(f"Hemo {node(hemo_label, active=(normo and known['hemo_any']), dim=dim_normo)}")
    dot.append("Retic -> Hemo;")

    vits_label = "\n".join(
        [
            status("B12/Folate", known["vits_any"]),
            status("B12", known["b12"]),
            status("Folate", known["folate"]),
        ]
    )
    dot.append(f"Vits {node(vits_label, active=(macro and known['vits_any']), dim=dim_macro)}")
    dot.append("Macro -> Vits;")

    other_label = "\n".join([status("TSH", known["tsh"]), "Consider LFTs/smear/meds"])
    dot.append(f"Other {node(other_label, active=macro, dim=dim_macro)}")
    dot.append("Vits -> Other;")

    dot.append(f"Next {node(nxt_label, active=True)}")

    if micro:
        dot.append("Iron -> Next;")
    elif normo:
        dot.append("Hemo -> Next;")
    elif macro:
        dot.append("Other -> Next;")
    else:
        dot.append("MCV -> Next;")

    dot.append("}")
    return "\n".join(dot)


# ============================================================
# UI: Inputs (no Step labels)
# ============================================================

st.header("Symptoms & severity")
colS1, colS2 = st.columns(2)
with colS1:
    symptomatic_any = selected(
        st.selectbox(
            "Is the patient symptomatic from anemia?",
            ["Select...", "Yes", "No", "Unknown"],
            index=0,
            help="Examples: dyspnea, fatigue limiting function, dizziness, chest pain, syncope.",
        )
    )
    high_risk_symptoms = selected(
        st.selectbox(
            "Any high-risk symptoms/signs?",
            ["Select...", "Yes", "No", "Unknown"],
            index=0,
            help="Examples: chest pain/ischemia, dyspnea at rest, syncope, hemodynamic instability, active bleeding.",
        )
    )
with colS2:
    active_bleeding = selected(
        st.selectbox(
            "Concern for active/ongoing bleeding?",
            ["Select...", "Yes", "No", "Unknown"],
            index=0,
        )
    )
    cvd = selected(
        st.selectbox(
            "Significant cardiovascular disease (CAD/HF) present?",
            ["Select...", "Yes", "No", "Unknown"],
            index=0,
        )
    )

st.header("CBC basics")
colA, colB = st.columns(2)
with colA:
    hb = to_float(st.text_input("Hemoglobin (g/dL)", value="", placeholder="leave blank if unknown"))
    hct = to_float(st.text_input("Hematocrit (%)", value="", placeholder="leave blank if unknown"))
with colB:
    mcv_cat = selected(
        st.selectbox(
            "MCV category",
            ["Select...", "Microcytic (<80)", "Normocytic (80–100)", "Macrocytic (>100)"],
            index=0,
            help="Main branching step for anemia evaluation.",
        )
    )
    rdw = selected(st.selectbox("RDW", ["Select...", "Normal", "High", "Unknown"], index=0))

other_cytopenias = None
rapid_onset = None
smear_abnormal = None
with st.expander("CBC context (optional)", expanded=False):
    colC1, colC2, colC3 = st.columns(3)
    with colC1:
        other_cytopenias = selected(
            st.selectbox(
                "Other cytopenias (WBC or platelets low)?",
                ["Select...", "Yes", "No", "Unknown"],
                index=0,
            )
        )
    with colC2:
        rapid_onset = selected(
            st.selectbox(
                "Rapid onset / acute Hb drop suspected?",
                ["Select...", "Yes", "No", "Unknown"],
                index=0,
            )
        )
    with colC3:
        smear_abnormal = selected(
            st.selectbox(
                "Peripheral smear abnormal (if known)?",
                ["Select...", "Yes", "No", "Unknown"],
                index=0,
            )
        )

# Retic/RPI
retic_qual = None
retic_pct = None
rpi = None
mf = None
corrected_retic = None

st.subheader("Reticulocytes")
expand_retic = (mcv_cat == "Normocytic (80–100)")
with st.expander("Reticulocyte count / RPI ", expanded=expand_retic):
    retic_mode = st.radio(
        "Reticulocyte input",
        ["Qualitative (Low/Normal/High)", "Numeric (%)"],
        horizontal=True,
        index=0,
    )

    if retic_mode == "Qualitative (Low/Normal/High)":
        retic_qual = selected(st.selectbox("Reticulocyte count", ["Select...", "Low", "Normal", "High"], index=0))
    else:
        retic_pct = to_float(st.text_input("Reticulocyte %", value="", placeholder="leave blank if unknown"))

    st.markdown("**Reticulocyte Index (Corrected retic) & RPI**")
    expected_hct_input = to_float(st.text_input("Expected Hematocrit (%)", value="", placeholder="40"))
    expected_hct = expected_hct_input if expected_hct_input is not None else 40.0

    mf = maturation_factor(hct)
    if retic_pct is not None and hct is not None and expected_hct and expected_hct != 0:
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

    interp_lines = []
    if rpi is not None:
        if rpi < 2:
            interp_lines.append("**RPI < 2:** underproduction physiology (hypoproliferative anemia).")
            interp_lines.append("Common buckets: iron deficiency/functional iron deficiency, inflammation, CKD, marrow suppression, endocrine (e.g., hypothyroidism).")
        else:
            interp_lines.append("**RPI ≥ 2:** appropriate marrow response.")
            interp_lines.append("Common buckets: blood loss (acute/occult) or hemolysis (confirm with markers + smear).")
    elif retic_qual is not None:
        if retic_qual == "High":
            interp_lines.append("**High retic:** suggests appropriate marrow response (blood loss/hemolysis physiology).")
        elif retic_qual == "Low":
            interp_lines.append("**Low retic:** suggests underproduction physiology.")
        elif retic_qual == "Normal":
            interp_lines.append("**Normal retic:** interpret in context of anemia severity; may be inappropriately low if Hb is significantly reduced.")
    else:
        interp_lines.append("Enter retic (or retic %) to interpret marrow response.")
    st.info("\n\n".join(interp_lines))

# Marrow response label
marrow_response = "Unknown"
if rpi is not None:
    marrow_response = "Appropriate (RPI ≥2)" if rpi >= 2 else "Inadequate (RPI <2)"
elif retic_qual is not None:
    if retic_qual == "High":
        marrow_response = "Appropriate/High retic"
    elif retic_qual == "Low":
        marrow_response = "Inadequate/Low retic"

st.header("Key labs (enter what you have)")

ferritin = None
transferrin_sat = None
with st.expander("Iron studies", expanded=(mcv_cat == "Microcytic (<80)")):
    colI1, colI2 = st.columns(2)
    with colI1:
        ferritin = to_float(st.text_input("Ferritin (ng/mL)", value="", placeholder="leave blank if unknown"))
    with colI2:
        transferrin_sat = to_float(st.text_input("Transferrin Saturation (%)", value="", placeholder="leave blank if unknown"))

b12 = None
folate = None
with st.expander("B12 / Folate", expanded=(mcv_cat == "Macrocytic (>100)")):
    colV1, colV2 = st.columns(2)
    with colV1:
        b12 = to_float(st.text_input("Vitamin B12 (pg/mL)", value="", placeholder="leave blank if unknown"))
    with colV2:
        folate = to_float(st.text_input("Folate (ng/mL)", value="", placeholder="leave blank if unknown"))

ldh = None
haptoglobin = None
indirect_bili = None
expand_hemo = marrow_response in ("Appropriate (RPI ≥2)", "Appropriate/High retic")
with st.expander("Hemolysis markers", expanded=expand_hemo):
    colH1, colH2, colH3 = st.columns(3)
    with colH1:
        ldh = selected(st.selectbox("LDH", ["Select...", "Normal", "High", "Unknown"], index=0))
    with colH2:
        haptoglobin = selected(st.selectbox("Haptoglobin", ["Select...", "Normal", "Low", "Unknown"], index=0))
    with colH3:
        indirect_bili = selected(st.selectbox("Indirect Bilirubin", ["Select...", "Normal", "High", "Unknown"], index=0))

tsh = None
egfr = None
with st.expander("Other contributors (TSH / kidney)", expanded=(mcv_cat in ("Macrocytic (>100)", "Normocytic (80–100)"))):
    colO1, colO2 = st.columns(2)
    with colO1:
        tsh = to_float(st.text_input("TSH (μIU/mL)", value="", placeholder="leave blank if unknown"))
    with colO2:
        egfr = to_float(st.text_input("eGFR (mL/min/1.73m²)", value="", placeholder="leave blank if unknown"))

exposures = []
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
    )

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

# Teaching sidebar decision tree
if teaching_mode:
    with st.sidebar:
        st.subheader("🧠 Live decision tree")
        st.caption(f"Path: {breadcrumb_path(mcv_cat, marrow_response, known, inputs)}")
        st.graphviz_chart(decision_tree_dot(mcv_cat, marrow_response, known))
        st.caption("Updates as you enter data.")


# ============================================================
# OUTPUTS
# ============================================================
st.markdown("---")
st.header("POC Summary")

if mcv_cat is None:
    st.info("Select an MCV category above to generate the POC summary and differential.")
else:
    st.markdown(f"**MCV category:** {mcv_cat}  \n**Marrow response:** {marrow_response}")

    # =========================================================
    # Differential build (UPDATED: B12/Folate are GLOBAL)
    # =========================================================
    dx = []

    # -------------------------
    # MCV-SPECIFIC DIFFERENTIALS
    # -------------------------
    if mcv_cat == "Microcytic (<80)":
        if ferritin is not None and ferritin < 30:
            add_item(
                dx,
                "Iron deficiency anemia",
                "Low ferritin supports depleted iron stores.",
                [
                    "Action: assess source of blood loss (GI/menstrual)",
                    "Action: consider GI evaluation when appropriate (age/risk-based)",
                    "Action: consider celiac testing if indicated",
                ],
                priority=10,
            )
        elif ferritin is not None and ferritin >= 100 and transferrin_sat is not None and transferrin_sat < 20:
            add_item(
                dx,
                "Anemia of chronic inflammation with functional iron deficiency",
                "Ferritin may be normal/high with low TSAT in inflammatory states.",
                [
                    "Action: review chronic inflammatory/infectious disease history",
                    "CRP/ESR (if inflammatory disease suspected)",
                ],
                priority=20,
            )
        else:
            add_item(
                dx,
                "Thalassemia trait / hemoglobinopathy",
                "Microcytosis without clear low ferritin may suggest thal trait or mixed etiologies.",
                [
                    "Action: review CBC indices (RBC count, RDW)",
                    "Peripheral smear review",
                    "Hemoglobin electrophoresis",
                ],
                priority=30,
            )

    if mcv_cat == "Normocytic (80–100)":
        if marrow_response in ("Appropriate (RPI ≥2)", "Appropriate/High retic"):
            add_item(
                dx,
                "Blood loss (acute or occult)",
                "Appropriate/high retic suggests response to loss (or recovery phase).",
                [
                    "Action: assess bleeding history",
                    "Iron studies (Ferritin, TSAT)",
                    "Action: consider stool testing/GI evaluation when appropriate",
                ],
                priority=15,
            )
            add_item(
                dx,
                "Hemolysis",
                "Appropriate/high retic can be seen in hemolysis; confirm with markers and smear.",
                [
                    "Hemolysis markers (LDH, haptoglobin, indirect bilirubin)",
                    "Peripheral smear review",
                    "DAT/Coombs (if suspected AIHA)",
                ],
                priority=18,
            )
        else:
            add_item(
                dx,
                "Anemia of chronic inflammation",
                "Common hypoproliferative normocytic pattern in chronic disease.",
                [
                    "Action: review chronic disease burden",
                    "Iron studies (Ferritin, TSAT)",
                    "CRP/ESR (if clinically indicated)",
                ],
                priority=20,
            )
            if egfr is not None and egfr < 60:
                add_item(
                    dx,
                    "Anemia associated with CKD",
                    "CKD can cause hypoproliferative normocytic anemia; likelihood increases as eGFR declines.",
                    [
                        "Iron studies (Ferritin, TSAT)",
                        "B12 and folate",
                        "Action: assess for bleeding/iron loss as appropriate",
                    ],
                    priority=22,
                )
            add_item(
                dx,
                "Bone marrow process / underproduction (consider if persistent or with other cytopenias)",
                "Low retic with other cytopenias or abnormal smear can suggest marrow process/suppression.",
                [
                    "Peripheral smear review",
                    "Action: trend CBC",
                    "Action: consider hematology referral if unexplained or with other cytopenias",
                ],
                priority=28,
            )

    if mcv_cat == "Macrocytic (>100)":
        # B12 and folate deficiency diagnoses are GLOBAL (below).
        # This block focuses on secondary causes when B12/folate are not low.
        if (b12 is None or b12 >= 200) and (folate is None or folate >= 4):
            add_item(
                dx,
                "Macrocytosis with B12/folate not low (consider alcohol/liver/thyroid/meds; marrow disorder if persistent)",
                "When B12/folate are not low, consider secondary causes; persistent unexplained macrocytosis—especially with cytopenias or dysplasia—warrants hematology evaluation.",
                [
                    "TSH",
                    "Action: consider LFTs",
                    "Peripheral smear review",
                    "Action: review meds/alcohol; consider hematology referral if persistent/unexplained",
                ],
                priority=25,
            )

    # -------------------------
    # GLOBAL RULES (NOT GATED BY MCV)
    # Mixed deficiencies can normalize or microcytize MCV.
    # -------------------------
    if b12 is not None and b12 < 200:
        add_item(
            dx,
            "Vitamin B12 deficiency",
            "Low B12 supports a megaloblastic process; MCV may be normal or low if concurrent iron deficiency or mixed etiologies.",
            [
                "MMA +/- homocysteine (if borderline)",
                "Action: assess diet/malabsorption risks",
                "Intrinsic factor antibody (if pernicious anemia suspected)",
            ],
            priority=12,
        )

    if folate is not None and folate < 4:
        add_item(
            dx,
            "Folate deficiency",
            "Low folate supports a megaloblastic process; MCV may be normal or low if concurrent iron deficiency or mixed etiologies.",
            [
                "Action: assess nutrition/alcohol use",
                "Action: review folate-antagonist meds/exposures",
            ],
            priority=15,
        )

    # -------------------------
    # OTHER EXISTING RULES (UNCHANGED)
    # -------------------------
    if ldh == "High" and haptoglobin == "Low" and indirect_bili == "High":
        add_item(
            dx,
            "Hemolysis (supported by markers)",
            "LDH high + haptoglobin low + indirect bilirubin high is a classic hemolysis pattern.",
            [
                "Peripheral smear review",
                "DAT/Coombs",
                "Reticulocyte count / RPI",
                "Action: consider G6PD if indicated",
            ],
            priority=8,
        )

    if tsh is not None and tsh > 5:
        add_item(
            dx,
            "Hypothyroidism-associated anemia",
            "Elevated TSH can contribute to normocytic/macrocytic anemia.",
            [
                "Action: repeat TSH/FT4 if needed",
                "Iron studies (Ferritin, TSAT)",
                "B12 and folate",
            ],
            priority=35,
        )

    if "NSAIDs / aspirin (chronic)" in exposures:
        add_item(
            dx,
            "Medication-associated occult GI blood loss (NSAIDs/ASA)",
            "Chronic NSAID/ASA use can contribute to ulcer/gastritis-related blood loss.",
            [
                "Action: assess GI symptoms",
                "Iron studies (Ferritin, TSAT)",
                "Action: review need for NSAID/ASA",
            ],
            priority=40,
        )

    if "Anticoagulant/antiplatelet use" in exposures:
        add_item(
            dx,
            "Bleeding risk contribution (anticoagulant/antiplatelet)",
            "These agents can increase bleeding risk and unmask occult sources.",
            ["Action: review medication indications", "Action: assess bleeding history"],
            priority=42,
        )

    if "PPI (long-term)" in exposures or "Metformin (long-term)" in exposures:
        add_item(
            dx,
            "Medication-associated B12 deficiency risk (PPI/metformin)",
            "Long-term PPI/metformin may reduce B12 absorption in some patients.",
            ["B12 and folate", "MMA +/- homocysteine (if borderline)", "Action: assess neuropathy/glossitis"],
            priority=40,
        )

    if "Alcohol use (heavy)" in exposures:
        add_item(
            dx,
            "Alcohol-related macrocytosis / nutritional deficiency",
            "Alcohol can cause macrocytosis and contribute to folate deficiency.",
            ["Action: consider LFTs", "B12 and folate", "Action: consider counseling/support resources"],
            priority=45,
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
            [
                "Action: review timing vs anemia onset",
                "Action: trend CBC",
                "Action: consider hematology referral if severe/persistent or with other cytopenias",
            ],
            priority=38,
        )

    dx_sorted = sorted(dx, key=lambda x: x.get("priority", 50))
    dx_unique = dedupe_by_title(dx_sorted)

    # ---- Data completeness ----
    st.markdown("#### Data completeness")
    level_txt, level_color = completeness_badge(known)
    st.markdown(pill(level_txt, level_color), unsafe_allow_html=True)
    st.caption("Completeness reflects whether key lab groups were entered")

    # ---- Next steps (POC) ----
    st.markdown("#### Next steps (POC)")
    base_next = next_most_informative(mcv_cat, marrow_response, known)

    high_yield_essentials = [
        "Peripheral smear review",
        "Reticulocyte count / RPI",
        "Iron studies (Ferritin, TSAT)",
        "B12 and folate",
        "Hemolysis markers (LDH, haptoglobin, indirect bilirubin)",
        "TSH",
        "eGFR/creatinine",
    ]

    steps = base_next + high_yield_essentials
    steps_filtered = expand_filter_list(steps, known, inputs, teaching=False)

    tests = []
    actions = []
    for s in steps_filtered:
        s_norm = titlecase_first(s)
        if any(k in s_norm.lower() for k in ["assess", "review", "consider", "trend", "counsel", "history", "refer", "evaluation", "coordinate"]):
            actions.append(s_norm)
        else:
            tests.append(s_norm)

    tests = dedupe_lines(tests)[:3]
    actions = dedupe_lines(actions)[:3]

    colN1, colN2 = st.columns(2)
    with colN1:
        st.markdown(pill("Do next tests", "#2563eb"), unsafe_allow_html=True)
        if tests:
            for t in tests:
                st.markdown(f"- {t}")
        else:
            st.caption("No additional tests suggested based on entered data (or already entered).")

    with colN2:
        st.markdown(pill("Do next actions", "#7c3aed"), unsafe_allow_html=True)
        if actions:
            for a in actions:
                st.markdown(f"- {a}")
        else:
            st.caption("No additional actions suggested based on entered data.")

    # ---- Most likely etiologies ----
    st.markdown("#### Most likely etiologies (based on entered data)")
    if not dx_unique:
        st.info("Enter more data to generate a ranked differential.")
    else:
        top = dx_unique[:3]
        if len(top) == 1:
            st.markdown(f"**{top[0]['title']}**")
        else:
            for i, item in enumerate(top, 1):
                st.markdown(f"**{i}. {item['title']}**")

    # ---- Details ----
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
                workup_lines = expand_filter_list(item.get("workup", []), known, inputs, teaching=teaching_mode)
                if workup_lines:
                    st.markdown("**Suggested next workup:**")
                    for w in workup_lines:
                        st.markdown(f"- {titlecase_first(w)}")

    st.markdown("---")
    with st.expander("📣 When to consider Hematology referral", expanded=False):
        referral_reasons = []
        if hb is not None and hb < 7 and (symptomatic_any in ("Yes", "Unknown") or high_risk_symptoms in ("Yes", "Unknown")):
            referral_reasons.append("Severe anemia with symptoms/high-risk features (coordinate urgent evaluation; hematology input may be appropriate).")
        if other_cytopenias in ("Yes", "Unknown"):
            referral_reasons.append("Anemia with other cytopenias (WBC/platelets low) or pancytopenia.")
        if smear_abnormal in ("Yes", "Unknown"):
            referral_reasons.append("Abnormal smear (e.g., blasts, schistocytes, dysplasia) or concerning morphology.")
        if (ldh == "High" and haptoglobin == "Low") or (indirect_bili == "High" and ldh == "High"):
            referral_reasons.append("Suspected hemolysis (especially if unexplained, severe, or with abnormal smear).")
        if mcv_cat == "Microcytic (<80)" and not known["iron_any"]:
            referral_reasons.append("Microcytic anemia with missing iron studies or unclear etiology after initial evaluation.")
        if mcv_cat == "Macrocytic (>100)" and not (known["b12"] and known["folate"]):
            referral_reasons.append("Macrocytic anemia without B12/folate evaluation or persistent macrocytosis without clear cause.")
        if mcv_cat == "Macrocytic (>100)" and (known["b12"] and known["folate"]) and (other_cytopenias in ("Yes", "Unknown") or smear_abnormal in ("Yes", "Unknown")):
            referral_reasons.append("Macrocytosis with cytopenias or abnormal smear: consider marrow disorder; hematology evaluation is appropriate.")
        if referral_reasons:
            for r in referral_reasons[:10]:
                st.markdown(f"- {r}")
        else:
            st.caption("No specific referral triggers detected from entered data (limited by missing inputs).")

st.markdown("---")
st.caption("Created by Manal Ahmidouch – GMA Clinic • Med-Ed Track • For Educational Use Only")