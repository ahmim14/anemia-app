import html
from typing import Any

import streamlit as st


st.set_page_config(
    page_title="AnemiaDx",
    page_icon="🩸",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ============================================================
# STYLING
# ============================================================
st.markdown(
    """
    <style>
        .block-container {
            max-width: 1050px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        [data-testid="stSidebar"] {
            background: #f8fafc;
            border-right: 1px solid #e2e8f0;
        }

        [data-testid="stSidebar"] * {
            color: #0f172a;
        }

        .sidebar-title {
            color: #0f172a !important;
            font-size: 1.3rem;
            font-weight: 850;
            margin: 0.2rem 0 0.9rem 0;
        }

        .app-header {
            position: relative;
            overflow: hidden;
            padding: 1.8rem 1.9rem;
            margin-bottom: 0.8rem;
            border-radius: 22px;
            border: 1px solid rgba(239, 68, 68, 0.28);
            background:
                radial-gradient(circle at 92% 10%, rgba(239, 68, 68, 0.24), transparent 34%),
                radial-gradient(circle at 8% 90%, rgba(127, 29, 29, 0.18), transparent 38%),
                linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(30, 41, 59, 0.96));
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.24);
        }

        .app-title {
            position: relative;
            z-index: 1;
            font-size: clamp(3.3rem, 7vw, 5.2rem);
            font-weight: 950;
            letter-spacing: -0.075em;
            line-height: 0.95;
            margin: 0;
            padding-right: 0.15em;
            background: linear-gradient(90deg, #fecaca 0%, #ef4444 38%, #dc2626 68%, #991b1b 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            filter: drop-shadow(0 5px 18px rgba(220, 38, 38, 0.22));
        }

        .app-subtitle {
            position: relative;
            z-index: 1;
            color: #e2e8f0 !important;
            font-size: 1.08rem;
            line-height: 1.55;
            margin: 0.75rem 0 0.25rem 0;
            max-width: 760px;
        }

        .build-label {
            position: relative;
            z-index: 1;
            display: inline-block;
            margin-top: 0.65rem;
            padding: 5px 10px;
            border-radius: 999px;
            border: 1px solid rgba(254, 202, 202, 0.28);
            background: rgba(127, 29, 29, 0.35);
            color: #fecaca !important;
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }

        .next-card {
            padding: 1rem 1.05rem;
            border-radius: 16px;
            border: 1px solid #991b1b;
            background: linear-gradient(135deg, #991b1b, #450a0a);
            box-shadow: 0 8px 22px rgba(127, 29, 29, 0.18);
            margin: 0.25rem 0 1.25rem 0;
        }

        .next-card-label {
            color: #fecaca !important;
            font-size: 0.72rem;
            font-weight: 850;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }

        .next-card-value {
            color: #ffffff !important;
            font-size: 1.02rem;
            font-weight: 800;
            line-height: 1.45;
            margin-top: 0.35rem;
        }

        .summary-card {
            padding: 1.15rem 1.25rem;
            border: 1px solid #334155;
            border-radius: 17px;
            background: rgba(15, 23, 42, 0.38);
            margin: 0.7rem 0;
        }

        .summary-label {
            color: #94a3b8;
            font-size: 0.75rem;
            font-weight: 850;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }

        .summary-value {
            color: #f8fafc;
            font-size: 1.08rem;
            font-weight: 750;
            line-height: 1.55;
        }

        .iron-pattern {
            padding: 0.95rem 1.05rem;
            margin: 0.65rem 0;
            border-radius: 14px;
            border-left: 5px solid #b91c1c;
            background: rgba(185, 28, 28, 0.10);
        }

        .iron-pattern-title {
            font-weight: 850;
            margin-bottom: 0.25rem;
        }

        .mixed-card {
            padding: 0.95rem 1.05rem;
            border-radius: 14px;
            border: 1px solid #d97706;
            background: rgba(245, 158, 11, 0.11);
            margin: 0.65rem 0;
        }

        .etiology-card {
            padding: 1rem 1.05rem;
            margin: 0.75rem 0 0.35rem 0;
            border-radius: 16px;
            border: 1px solid #475569;
            background: #111827;
        }

        .etiology-title {
            color: #f8fafc !important;
            font-size: 1.04rem;
            font-weight: 850;
            line-height: 1.4;
        }

        .evidence-chip {
            display: inline-block;
            padding: 5px 10px;
            margin: 5px 6px 0 0;
            border-radius: 999px;
            background: #e2e8f0 !important;
            border: 1px solid #94a3b8;
            color: #0f172a !important;
            font-size: 0.78rem;
            font-weight: 750;
        }

        .confidence-strong,
        .confidence-supported,
        .confidence-possible {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 850;
            white-space: nowrap;
        }

        .confidence-strong { background: #dcfce7; color: #166534 !important; }
        .confidence-supported { background: #dbeafe; color: #1d4ed8 !important; }
        .confidence-possible { background: #fef3c7; color: #92400e !important; }

        div[data-testid="stExpander"] { border-radius: 14px; }
        div[data-testid="stMetric"] {
            border: 1px solid rgba(148, 163, 184, 0.25);
            padding: 0.75rem;
            border-radius: 12px;
        }
        div.stButton > button { border-radius: 11px; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================
def to_float(value: str | None) -> float | None:
    cleaned = (value or "").strip()
    if cleaned == "":
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def fmt(value: Any, digits: int = 1, suffix: str = "") -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value):.{digits}f}{suffix}"
    except (TypeError, ValueError):
        return f"{value}{suffix}"


def selected(value: str | None) -> str | None:
    return None if value in (None, "", "Select...", "Select…") else value


def known_choice(value: str | None) -> bool:
    return value not in (None, "Unknown")


def safe_text(value: Any) -> str:
    return html.escape(str(value))


def dedupe_lines(lines: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for line in lines:
        cleaned = (line or "").strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)
    return result


def clean_evidence(values: list[Any]) -> list[str]:
    """Remove empty or unknown values before rendering support bubbles."""
    cleaned: list[str] = []
    for value in values:
        text = str(value).strip()
        if not text:
            continue
        if "unknown" in text.lower():
            continue
        if text in {"None", "—"}:
            continue
        cleaned.append(text)
    return dedupe_lines(cleaned)


def add_dx(
    items: list[dict[str, Any]],
    title: str,
    rationale: str,
    evidence: list[Any] | None = None,
    workup: list[str] | None = None,
    confidence: str = "Possible",
    priority: int = 50,
) -> None:
    items.append(
        {
            "title": title,
            "rationale": rationale,
            "evidence": clean_evidence(evidence or []),
            "workup": workup or [],
            "confidence": confidence,
            "priority": priority,
        }
    )


def dedupe_dx(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        if item["title"] not in seen:
            seen.add(item["title"])
            result.append(item)
    return result


def maturation_factor(hct: float | None) -> float | None:
    if hct is None:
        return None
    if hct >= 40:
        return 1.0
    if hct >= 30:
        return 1.5
    if hct >= 20:
        return 2.0
    return 2.5


def field_style(label: str, status: str) -> str:
    palette = {
        "abnormal": ("#dc2626", "rgba(220, 38, 38, 0.18)"),
        "borderline": ("#d97706", "rgba(245, 158, 11, 0.18)"),
        "normal": ("#16a34a", "rgba(34, 197, 94, 0.14)"),
    }
    if status not in palette:
        return ""
    border, background = palette[status]
    return (
        f'input[aria-label="{label}"] {{'
        f'background: {background} !important;'
        f'border: 2px solid {border} !important;'
        f'box-shadow: 0 0 0 1px {border}33 !important;'
        f'}}'
    )


def inject_input_highlights(
    hb: float | None,
    sex: str | None,
    ferritin: float | None,
    tsat: float | None,
    b12: float | None,
    folate: float | None,
    tsh: float | None,
    egfr: float | None,
) -> None:
    rules: list[str] = []

    if hb is not None and sex is not None:
        low_hb = (sex == "Female" and hb < 12) or (sex == "Male" and hb < 13)
        rules.append(field_style("Hemoglobin (g/dL)", "abnormal" if low_hb else "normal"))

    if ferritin is not None:
        status = "abnormal" if ferritin < 30 else "borderline" if ferritin < 100 else "normal"
        rules.append(field_style("Ferritin (ng/mL)", status))

    if tsat is not None:
        rules.append(field_style("Transferrin Saturation (%)", "abnormal" if tsat < 20 else "normal"))

    if b12 is not None:
        status = "abnormal" if b12 < 200 else "borderline" if b12 < 300 else "normal"
        rules.append(field_style("Vitamin B12 (pg/mL)", status))

    if folate is not None:
        rules.append(field_style("Folate (ng/mL)", "abnormal" if folate < 4 else "normal"))

    if tsh is not None:
        rules.append(field_style("TSH (μIU/mL)", "abnormal" if tsh > 5 or tsh < 0.4 else "normal"))

    if egfr is not None:
        status = "abnormal" if egfr < 60 else "borderline" if egfr < 90 else "normal"
        rules.append(field_style("eGFR (mL/min/1.73m²)", status))

    if rules:
        st.markdown("<style>" + "".join(rules) + "</style>", unsafe_allow_html=True)


def build_known(inputs: dict[str, Any]) -> dict[str, bool]:
    known = {
        "ferritin": inputs["ferritin"] is not None,
        "tsat": inputs["tsat"] is not None,
        "b12": inputs["b12"] is not None,
        "folate": inputs["folate"] is not None,
        "tsh": inputs["tsh"] is not None,
        "egfr": inputs["egfr"] is not None,
        "ldh": known_choice(inputs["ldh"]),
        "haptoglobin": known_choice(inputs["haptoglobin"]),
        "indirect_bili": known_choice(inputs["indirect_bili"]),
        "retic_pct": inputs["retic_pct"] is not None,
        "retic_qual": known_choice(inputs["retic_qual"]),
        "rpi": inputs["rpi"] is not None,
        "smear": known_choice(inputs["smear_abnormal"]),
    }
    known["iron_complete"] = known["ferritin"] and known["tsat"]
    known["vits_complete"] = known["b12"] and known["folate"]
    known["hemo_complete"] = known["ldh"] and known["haptoglobin"] and known["indirect_bili"]
    known["retic_any"] = known["retic_pct"] or known["retic_qual"] or known["rpi"]
    return known


def interpret_iron_pattern(ferritin: float | None, tsat: float | None) -> dict[str, str] | None:
    if ferritin is None and tsat is None:
        return None
    if ferritin is not None and ferritin < 30:
        if tsat is not None and tsat < 20:
            return {
                "title": "Absolute iron deficiency pattern",
                "description": "Low ferritin with low transferrin saturation strongly supports depleted iron stores.",
            }
        return {
            "title": "Iron deficiency pattern",
            "description": "Ferritin below 30 ng/mL supports depleted iron stores, even when MCV is normal.",
        }
    if ferritin is not None and ferritin >= 100 and tsat is not None and tsat < 20:
        return {
            "title": "Functional iron deficiency pattern",
            "description": "Low transferrin saturation with preserved or elevated ferritin may occur with inflammation or chronic disease.",
        }
    if ferritin is not None and 30 <= ferritin < 100 and tsat is not None and tsat < 20:
        return {
            "title": "Possible iron deficiency or mixed inflammatory pattern",
            "description": "Borderline ferritin with low transferrin saturation may represent iron deficiency, inflammation, or both.",
        }
    if ferritin is not None and ferritin >= 100 and tsat is not None and tsat >= 20:
        return {
            "title": "Iron deficiency not supported by entered studies",
            "description": "The entered ferritin and transferrin saturation do not show a typical iron-deficiency pattern.",
        }
    return {
        "title": "Incomplete iron-study pattern",
        "description": "Enter both ferritin and transferrin saturation for a more specific interpretation.",
    }


def next_most_informative(
    mcv_cat: str | None,
    marrow_response: str,
    known: dict[str, bool],
    smear_abnormal: str | None,
) -> list[str]:
    if mcv_cat == "Microcytic (<80)":
        return ["Complete iron studies with ferritin and TSAT"] if not known["iron_complete"] else ["Assess bleeding source risk as clinically appropriate"]
    if mcv_cat == "Normocytic (80–100)":
        if not known["retic_any"]:
            return ["Reticulocyte count or RPI"]
        if marrow_response in ("Appropriate response", "Appropriate/high reticulocyte response"):
            missing: list[str] = []
            if not known["hemo_complete"]:
                missing.append("Complete hemolysis markers")
            if not known["smear"]:
                missing.append("Peripheral smear review")
            return missing or ["Differentiate blood loss from hemolysis"]
        return ["Evaluate iron status, kidney function, inflammation, and marrow suppression"]
    if mcv_cat == "Macrocytic (>100)":
        if not known["vits_complete"]:
            return ["Vitamin B12 and folate"]
        if not known["tsh"]:
            return ["TSH"]
        if smear_abnormal is None:
            return ["Peripheral smear result"]
        return ["Review medications, alcohol exposure, liver disease, and marrow causes"]
    return ["Select an MCV category"]


def progressive_tree_dot(
    mcv_cat: str | None,
    marrow_response: str,
    known: dict[str, bool],
    iron_pattern: dict[str, str] | None,
) -> str:
    nodes = [("Start", "Start")]
    if mcv_cat is None:
        nodes.append(("MCV", "Select MCV"))
    else:
        nodes.append(("MCV", mcv_cat))
        if mcv_cat == "Microcytic (<80)":
            nodes.append(("Path", "Microcytic pathway"))
            nodes.append(("Current", "Complete iron studies" if not known["iron_complete"] else iron_pattern["title"] if iron_pattern else "Assess iron pattern"))
        elif mcv_cat == "Normocytic (80–100)":
            nodes.append(("Path", "Normocytic pathway"))
            if not known["retic_any"]:
                nodes.append(("Current", "Obtain reticulocyte response"))
            else:
                nodes.append(("Retic", marrow_response))
                if marrow_response in ("Appropriate response", "Appropriate/high reticulocyte response"):
                    nodes.append(("Current", "Complete hemolysis evaluation" if not known["hemo_complete"] else "Blood loss vs hemolysis"))
                else:
                    nodes.append(("Current", "Underproduction evaluation"))
        elif mcv_cat == "Macrocytic (>100)":
            nodes.append(("Path", "Macrocytic pathway"))
            if not known["vits_complete"]:
                nodes.append(("Current", "Check B12 and folate"))
            elif not known["tsh"]:
                nodes.append(("Current", "Check TSH"))
            else:
                nodes.append(("Current", "Review liver, medications, alcohol, and marrow causes"))

    dot = [
        "digraph G {",
        "rankdir=TB;",
        "splines=polyline;",
        "nodesep=0.35;",
        "ranksep=0.45;",
        'graph [bgcolor="transparent", margin=0.05];',
        'node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=12, color="#15803d", fontcolor="#111827", fillcolor="#ecfdf5", penwidth=1.4, margin="0.18,0.13"];',
        'edge [color="#94a3b8", penwidth=1.5, arrowsize=0.8];',
    ]
    for node_id, label in nodes:
        escaped = label.replace('"', "'").replace("\n", "\\n")
        dot.append(f'{node_id} [label="{escaped}"];')
    for index in range(len(nodes) - 1):
        dot.append(f"{nodes[index][0]} -> {nodes[index + 1][0]};")
    dot.append("}")
    return "\n".join(dot)


def filter_suggestions(lines: list[str], known: dict[str, bool]) -> list[str]:
    filtered: list[str] = []
    for line in lines:
        lower = line.lower()
        if "peripheral smear" in lower and known["smear"]:
            continue
        if ("reticulocyte" in lower or "rpi" in lower) and known["retic_any"]:
            continue
        if ("ferritin" in lower or "tsat" in lower or "iron studies" in lower) and known["iron_complete"]:
            continue
        if ("b12" in lower or "folate" in lower) and known["vits_complete"]:
            continue
        if "tsh" in lower and known["tsh"]:
            continue
        if ("egfr" in lower or "creatinine" in lower) and known["egfr"]:
            continue
        if ("hemolysis markers" in lower or "ldh" in lower or "haptoglobin" in lower or "indirect bilirubin" in lower) and known["hemo_complete"]:
            continue
        filtered.append(line)
    return dedupe_lines(filtered)


# ============================================================
# HEADER + ROBUST RESET
# ============================================================
st.markdown(
    """
    <div class="app-header">
        <div class="app-title">AnemiaDx</div>
        <div class="app-subtitle">A stepwise approach to anemia evaluation, differential diagnosis, and resident education.</div>
        <div class="build-label">Clinical reasoning assistant</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Educational decision support only — not a substitute for clinical judgment.")

reset_col, _ = st.columns([1.5, 4])
with reset_col:
    if st.button("↻ Start new evaluation", use_container_width=True, key="reset_button"):
        st.session_state.clear()
        st.rerun()


# ============================================================
# INPUTS
# ============================================================
toggle_col_1, toggle_col_2 = st.columns([2, 1])
with toggle_col_1:
    teaching_mode = st.toggle("Teaching Mode (live tree + reasoning)", value=False, key="teaching_mode")
with toggle_col_2:
    show_all_details = st.toggle("Expand diagnosis details", value=False, key="show_all_details") if teaching_mode else False

st.header("Symptoms & severity")
left, right = st.columns(2)
with left:
    symptomatic_any = selected(st.selectbox("Is the patient symptomatic from anemia?", ["Select...", "Yes", "No", "Unknown"], key="symptomatic_any"))
    high_risk_symptoms = selected(st.selectbox("Any high-risk symptoms/signs?", ["Select...", "Yes", "No", "Unknown"], key="high_risk_symptoms"))
with right:
    active_bleeding = selected(st.selectbox("Concern for active/ongoing bleeding?", ["Select...", "Yes", "No", "Unknown"], key="active_bleeding"))
    cvd = selected(st.selectbox("Significant cardiovascular disease (CAD/HF) present?", ["Select...", "Yes", "No", "Unknown"], key="cvd"))

st.header("CBC basics")
left, right = st.columns(2)
with left:
    hb = to_float(st.text_input("Hemoglobin (g/dL)", placeholder="leave blank if unknown", key="hb"))
    hct = to_float(st.text_input("Hematocrit (%)", placeholder="leave blank if unknown", key="hct"))
with right:
    sex = selected(st.selectbox("Sex", ["Select...", "Female", "Male"], key="sex"))
    mcv_cat = selected(st.selectbox("MCV category", ["Select...", "Microcytic (<80)", "Normocytic (80–100)", "Macrocytic (>100)"], key="mcv_cat"))
    rdw = selected(st.selectbox("RDW", ["Select...", "Normal", "High", "Unknown"], key="rdw"))

other_cytopenias = None
rapid_onset = None
smear_abnormal = None
with st.expander("CBC context (optional)", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        other_cytopenias = selected(st.selectbox("Other cytopenias?", ["Select...", "Yes", "No", "Unknown"], key="other_cytopenias"))
    with c2:
        rapid_onset = selected(st.selectbox("Rapid onset or acute Hb drop?", ["Select...", "Yes", "No", "Unknown"], key="rapid_onset"))
    with c3:
        smear_abnormal = selected(st.selectbox("Peripheral smear abnormal?", ["Select...", "Yes", "No", "Unknown"], key="smear_abnormal"))

st.subheader("Reticulocytes")
retic_qual = None
retic_pct = None
rpi = None
corrected_retic = None
mf = None
with st.expander("Reticulocyte count / RPI", expanded=(mcv_cat == "Normocytic (80–100)")):
    retic_mode = st.radio("Reticulocyte input", ["Qualitative", "Numeric (%)"], horizontal=True, key="retic_mode")
    if retic_mode == "Qualitative":
        retic_qual = selected(st.selectbox("Reticulocyte count", ["Select...", "Low", "Normal", "High"], key="retic_qual"))
    else:
        retic_pct = to_float(st.text_input("Reticulocyte %", placeholder="leave blank if unknown", key="retic_pct"))
    expected_hct_input = to_float(st.text_input("Expected Hematocrit (%)", placeholder="40", key="expected_hct"))
    expected_hct = expected_hct_input if expected_hct_input is not None else 40.0
    mf = maturation_factor(hct)
    if retic_pct is not None and hct is not None and expected_hct > 0:
        corrected_retic = retic_pct * (hct / expected_hct)
        if mf:
            rpi = corrected_retic / mf
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Corrected retic", fmt(corrected_retic, 2, "%"))
    with m2:
        st.metric("Maturation factor", fmt(mf, 1))
    with m3:
        st.metric("RPI", fmt(rpi, 2))

marrow_response = "Unknown"
if rpi is not None:
    marrow_response = "Appropriate response" if rpi >= 2 else "Inadequate response"
elif retic_qual == "High":
    marrow_response = "Appropriate/high reticulocyte response"
elif retic_qual == "Low":
    marrow_response = "Inadequate/low reticulocyte response"

st.header("Key labs")
with st.expander("Iron studies", expanded=(mcv_cat == "Microcytic (<80)")):
    c1, c2 = st.columns(2)
    with c1:
        ferritin = to_float(st.text_input("Ferritin (ng/mL)", placeholder="leave blank if unknown", key="ferritin"))
    with c2:
        tsat = to_float(st.text_input("Transferrin Saturation (%)", placeholder="leave blank if unknown", key="tsat"))

with st.expander("Vitamin B12 / folate", expanded=(mcv_cat == "Macrocytic (>100)")):
    c1, c2 = st.columns(2)
    with c1:
        b12 = to_float(st.text_input("Vitamin B12 (pg/mL)", placeholder="leave blank if unknown", key="b12"))
    with c2:
        folate = to_float(st.text_input("Folate (ng/mL)", placeholder="leave blank if unknown", key="folate"))

with st.expander("Hemolysis markers", expanded=marrow_response in ("Appropriate response", "Appropriate/high reticulocyte response")):
    c1, c2, c3 = st.columns(3)
    with c1:
        ldh = selected(st.selectbox("LDH", ["Select...", "Normal", "High", "Unknown"], key="ldh"))
    with c2:
        haptoglobin = selected(st.selectbox("Haptoglobin", ["Select...", "Normal", "Low", "Unknown"], key="haptoglobin"))
    with c3:
        indirect_bili = selected(st.selectbox("Indirect bilirubin", ["Select...", "Normal", "High", "Unknown"], key="indirect_bili"))

with st.expander("Other contributors", expanded=mcv_cat in ("Normocytic (80–100)", "Macrocytic (>100)")):
    c1, c2 = st.columns(2)
    with c1:
        tsh = to_float(st.text_input("TSH (μIU/mL)", placeholder="leave blank if unknown", key="tsh"))
    with c2:
        egfr = to_float(st.text_input("eGFR (mL/min/1.73m²)", placeholder="leave blank if unknown", key="egfr"))

with st.expander("High-yield medications and exposures", expanded=False):
    exposures = st.multiselect(
        "Select any that apply",
        [
            "NSAIDs / aspirin (chronic)",
            "Anticoagulant/antiplatelet use",
            "PPI (long-term)",
            "Metformin (long-term)",
            "Alcohol use (heavy)",
            "Chemotherapy / antimetabolites",
            "Hydroxyurea",
            "Folate-antagonist medication",
            "Linezolid",
            "Valproate",
            "Marrow-toxic antiviral",
            "Recent transfusion (last 3 months)",
        ],
        key="exposures",
    )

inject_input_highlights(hb, sex, ferritin, tsat, b12, folate, tsh, egfr)

inputs = {
    "ferritin": ferritin,
    "tsat": tsat,
    "b12": b12,
    "folate": folate,
    "tsh": tsh,
    "egfr": egfr,
    "ldh": ldh,
    "haptoglobin": haptoglobin,
    "indirect_bili": indirect_bili,
    "retic_pct": retic_pct,
    "retic_qual": retic_qual,
    "rpi": rpi,
    "smear_abnormal": smear_abnormal,
}
known = build_known(inputs)
iron_pattern = interpret_iron_pattern(ferritin, tsat)

if teaching_mode:
    with st.sidebar:
        st.markdown('<div class="sidebar-title">Live reasoning map</div>', unsafe_allow_html=True)
        next_items = next_most_informative(mcv_cat, marrow_response, known, smear_abnormal)
        st.markdown(
            '<div class="next-card"><div class="next-card-label">Next most informative</div>'
            f'<div class="next-card-value">{"<br>".join(safe_text(item) for item in next_items)}</div></div>',
            unsafe_allow_html=True,
        )
        st.graphviz_chart(progressive_tree_dot(mcv_cat, marrow_response, known, iron_pattern), use_container_width=True)
        st.caption("Only the active clinical pathway is displayed.")


# ============================================================
# CLINICAL SUMMARY
# ============================================================
st.markdown("---")
st.header("Clinical summary")

if mcv_cat is None:
    st.info("Select an MCV category to generate the clinical impression and ranked differential.")
else:
    no_anemia = False
    if hb is not None and sex is not None:
        no_anemia = (sex == "Female" and hb >= 12) or (sex == "Male" and hb >= 13)

    if no_anemia:
        st.success("No anemia is detected using the entered hemoglobin and sex-specific threshold.")
    else:
        dx: list[dict[str, Any]] = []

        if mcv_cat == "Microcytic (<80)":
            if ferritin is not None and ferritin >= 100 and tsat is not None and tsat < 20:
                add_dx(
                    dx,
                    "Anemia of chronic inflammation with functional iron deficiency",
                    "Low iron availability with preserved or elevated ferritin may reflect inflammation-mediated iron restriction.",
                    [f"Ferritin {fmt(ferritin, 0)} ng/mL", f"TSAT {fmt(tsat, 0, '%')}", "Microcytosis"],
                    ["Review chronic inflammatory or infectious conditions", "Consider CRP or ESR when clinically indicated"],
                    "Supported",
                    15,
                )
            elif not (ferritin is not None and ferritin < 30):
                evidence = ["Microcytosis"]
                if ferritin is not None:
                    evidence.append(f"Ferritin {fmt(ferritin, 0)} ng/mL")
                add_dx(
                    dx,
                    "Thalassemia trait / hemoglobinopathy",
                    "Microcytosis without clearly depleted iron stores raises consideration of thalassemia trait or another hemoglobinopathy.",
                    evidence,
                    ["Review RBC count and RDW", "Hemoglobin electrophoresis", "Peripheral smear review if not already available"],
                    "Possible",
                    35,
                )

        elif mcv_cat == "Normocytic (80–100)":
            if marrow_response in ("Appropriate response", "Appropriate/high reticulocyte response"):
                add_dx(dx, "Blood loss", "An appropriate marrow response can occur after acute or ongoing blood loss.", ["Normocytic anemia", marrow_response], ["Assess overt and occult bleeding history", "Evaluate GI or gynecologic sources as appropriate"], "Supported", 20)
                add_dx(dx, "Hemolysis", "An appropriate reticulocyte response may reflect increased red-cell destruction.", ["Normocytic anemia", marrow_response], ["Complete hemolysis markers", "DAT when immune hemolysis is suspected", "Peripheral smear review if not already available"], "Possible", 25)
            else:
                add_dx(dx, "Anemia of chronic inflammation", "A normocytic anemia with an inadequate or unknown marrow response commonly occurs with chronic disease.", ["Normocytic anemia", marrow_response], ["Review chronic inflammatory disease burden", "Complete iron studies", "Consider inflammatory markers when indicated"], "Possible", 30)
                if egfr is not None and egfr < 60:
                    add_dx(dx, "Anemia associated with chronic kidney disease", "Reduced kidney function may cause a hypoproliferative normocytic anemia.", [f"eGFR {fmt(egfr, 0)}", "Normocytic anemia"], ["Confirm iron sufficiency", "Review kidney-disease severity and trend"], "Supported", 18)
                if other_cytopenias == "Yes" or smear_abnormal == "Yes" or marrow_response in ("Inadequate response", "Inadequate/low reticulocyte response"):
                    evidence = ["Underproduction pattern"]
                    if other_cytopenias == "Yes":
                        evidence.append("Additional cytopenias")
                    if smear_abnormal == "Yes":
                        evidence.append("Abnormal smear")
                    add_dx(dx, "Bone marrow process or marrow suppression", "An inadequate marrow response, other cytopenias, or abnormal morphology may indicate marrow pathology or medication-related suppression.", evidence, ["Trend complete blood count", "Review medication and exposure history", "Consider hematology evaluation if unexplained"], "Supported" if other_cytopenias == "Yes" or smear_abnormal == "Yes" else "Possible", 22)

        elif mcv_cat == "Macrocytic (>100)":
            if (b12 is None or b12 >= 200) and (folate is None or folate >= 4):
                evidence = ["Macrocytosis"]
                if b12 is not None:
                    evidence.append(f"B12 {fmt(b12, 0)} pg/mL")
                if folate is not None:
                    evidence.append(f"Folate {fmt(folate, 1)} ng/mL")
                add_dx(dx, "Non-megaloblastic macrocytosis or marrow disorder", "When B12 and folate are not low, consider alcohol, liver disease, hypothyroidism, medication effects, reticulocytosis, or marrow pathology.", evidence, ["Review medications and alcohol exposure", "Consider liver testing", "Check TSH if not already entered", "Consider hematology evaluation if persistent or unexplained"], "Possible", 30)

        if ferritin is not None and ferritin < 30:
            evidence = [f"Ferritin {fmt(ferritin, 0)} ng/mL", f"MCV: {mcv_cat.split(' ')[0]}"]
            if tsat is not None:
                evidence.append(f"TSAT {fmt(tsat, 0, '%')}")
            add_dx(dx, "Iron deficiency anemia", "Low ferritin supports depleted iron stores. Iron deficiency may remain normocytic early or when mixed with another process.", evidence, ["Assess GI and menstrual blood loss as appropriate", "Consider malabsorption or celiac disease when indicated", "Treat iron deficiency and monitor hematologic response"], "Strongly supported" if tsat is not None and tsat < 20 else "Supported", 5)

        if b12 is not None and b12 < 200:
            add_dx(dx, "Vitamin B12 deficiency", "A low vitamin B12 level supports a megaloblastic process, although MCV may be normal or low in mixed anemia.", [f"B12 {fmt(b12, 0)} pg/mL", f"MCV: {mcv_cat.split(' ')[0]}"], ["Assess dietary and malabsorption risk", "Consider intrinsic-factor antibody testing", "Consider MMA when the result or clinical context is uncertain"], "Strongly supported", 7)
        elif b12 is not None and 200 <= b12 < 300:
            add_dx(dx, "Borderline vitamin B12 status", "Borderline vitamin B12 may warrant biochemical confirmation when symptoms or macrocytosis are present.", [f"B12 {fmt(b12, 0)} pg/mL"], ["Consider methylmalonic acid", "Assess dietary and malabsorption risk"], "Possible", 28)

        if folate is not None and folate < 4:
            add_dx(dx, "Folate deficiency", "A low folate level supports a megaloblastic process.", [f"Folate {fmt(folate, 1)} ng/mL"], ["Assess nutrition and alcohol exposure", "Review folate-antagonist medications"], "Strongly supported", 8)

        hemolysis_pattern = ldh == "High" and haptoglobin == "Low" and indirect_bili == "High"
        if hemolysis_pattern:
            add_dx(dx, "Hemolysis", "High LDH, low haptoglobin, and elevated indirect bilirubin form a classic biochemical hemolysis pattern.", ["High LDH", "Low haptoglobin", "High indirect bilirubin"], ["DAT when immune hemolysis is suspected", "Review peripheral smear findings", "Consider G6PD testing when clinically indicated"], "Strongly supported", 4)

        if tsh is not None and tsh > 5:
            add_dx(dx, "Hypothyroidism-associated anemia", "An elevated TSH may contribute to normocytic or macrocytic anemia.", [f"TSH {fmt(tsh, 2)} μIU/mL"], ["Review free T4", "Address thyroid dysfunction as clinically appropriate"], "Supported", 24)

        if smear_abnormal == "Yes":
            add_dx(dx, "Abnormal peripheral smear requiring directed evaluation", "The smear is already known to be abnormal. Evaluation should be guided by the specific morphology rather than repeating a generic smear recommendation.", ["Abnormal smear documented"], ["Identify the reported morphology", "Correlate morphology with CBC, reticulocytes, and hemolysis markers", "Consider hematology input for blasts, schistocytes, or dysplasia"], "Supported", 3)

        dx = dedupe_dx(sorted(dx, key=lambda item: item["priority"]))

        mixed_findings: list[str] = []
        if mcv_cat == "Normocytic (80–100)" and ferritin is not None and ferritin < 30:
            mixed_findings.append("Normal MCV does not exclude iron deficiency; this may represent early iron deficiency or a mixed anemia.")
        if rdw == "High" and mcv_cat == "Normocytic (80–100)":
            mixed_findings.append("High RDW with a normal MCV may reflect competing microcytic and macrocytic processes.")
        if mcv_cat == "Microcytic (<80)" and ((b12 is not None and b12 < 200) or (folate is not None and folate < 4)):
            mixed_findings.append("Vitamin deficiency with microcytosis suggests a possible mixed anemia in which a microcytic process masks macrocytosis.")
        if "Recent transfusion (last 3 months)" in exposures:
            mixed_findings.append("Recent transfusion may alter MCV and RDW, reducing the reliability of morphology-based classification.")

        morphology = mcv_cat.split(" ")[0].lower()
        physiology = ""
        if marrow_response in ("Appropriate response", "Appropriate/high reticulocyte response"):
            physiology = " with an appropriate marrow response"
        elif marrow_response in ("Inadequate response", "Inadequate/low reticulocyte response"):
            physiology = " with an inadequate marrow response"

        if dx:
            top_titles = [item["title"] for item in dx[:2]]
            clinical_impression = (
                f"{morphology.capitalize()} anemia{physiology}; {top_titles[0]} is the leading consideration."
                if len(top_titles) == 1
                else f"{morphology.capitalize()} anemia{physiology}; leading considerations are {top_titles[0]} and {top_titles[1]}."
            )
        else:
            clinical_impression = f"{morphology.capitalize()} anemia{physiology}; additional laboratory data are needed to identify the leading etiology."

        st.markdown('<div class="summary-card"><div class="summary-label">Clinical impression</div>' f'<div class="summary-value">{safe_text(clinical_impression)}</div></div>', unsafe_allow_html=True)

        if iron_pattern is not None:
            st.markdown('<div class="iron-pattern"><div class="iron-pattern-title">' f'{safe_text(iron_pattern["title"])}</div><div>{safe_text(iron_pattern["description"])}</div></div>', unsafe_allow_html=True)

        if mixed_findings:
            mixed_html = "".join(f"<li>{safe_text(item)}</li>" for item in mixed_findings)
            st.markdown('<div class="mixed-card"><strong>Mixed or potentially masked anemia pattern</strong>' f'<ul style="margin-top:0.5rem; margin-bottom:0;">{mixed_html}</ul></div>', unsafe_allow_html=True)

        completed_groups = sum([known["iron_complete"], known["retic_any"], known["vits_complete"], known["hemo_complete"], known["tsh"] or known["egfr"]])
        completeness, color = ("Low", "#dc2626") if completed_groups <= 1 else ("Moderate", "#d97706") if completed_groups <= 3 else ("High", "#16a34a")
        st.markdown("#### Data completeness")
        st.markdown(f'<span style="display:inline-block;padding:5px 11px;border-radius:999px;background:{color};color:#fff;font-size:.82rem;font-weight:800;">{completeness}</span>', unsafe_allow_html=True)

        st.markdown("#### Recommended next steps")
        base_steps = next_most_informative(mcv_cat, marrow_response, known, smear_abnormal)
        general_steps = ["Peripheral smear review", "Reticulocyte count or RPI", "Complete iron studies with ferritin and TSAT", "Vitamin B12 and folate", "Complete hemolysis markers", "TSH", "eGFR or creatinine"]
        filtered_steps = filter_suggestions(base_steps + general_steps, known)
        tests: list[str] = []
        actions: list[str] = []
        for step in filtered_steps:
            if any(term in step.lower() for term in ("assess", "review", "evaluate", "differentiate", "consider", "monitor", "trend")):
                actions.append(step)
            else:
                tests.append(step)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Next tests**")
            for item in dedupe_lines(tests)[:3]:
                st.markdown(f"- {item}")
        with c2:
            st.markdown("**Next clinical actions**")
            for item in dedupe_lines(actions)[:3]:
                st.markdown(f"- {item}")

        st.header("Most likely etiologies")
        if not dx:
            st.info("Enter additional data to generate a ranked differential.")
        else:
            for index, item in enumerate(dx[:3], start=1):
                confidence_class = "confidence-strong" if item["confidence"] == "Strongly supported" else "confidence-supported" if item["confidence"] == "Supported" else "confidence-possible"
                evidence_html = "".join(f'<span class="evidence-chip">{safe_text(evidence)}</span>' for evidence in clean_evidence(item["evidence"]))
                card_html = (
                    '<div class="etiology-card">'
                    '<div style="display:flex;justify-content:space-between;gap:1rem;align-items:flex-start;">'
                    f'<div class="etiology-title">{index}. {safe_text(item["title"])}</div>'
                    f'<span class="{confidence_class}">{safe_text(item["confidence"])}</span>'
                    '</div>'
                    f'<div style="margin-top:.55rem;">{evidence_html}</div>'
                    '</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)
                with st.expander("Why this diagnosis and suggested workup", expanded=show_all_details):
                    st.markdown(f"**Why it was selected:** {item['rationale']}")
                    filtered_workup = filter_suggestions(item["workup"], known)
                    if filtered_workup:
                        st.markdown("**Suggested next workup:**")
                        for workup_item in filtered_workup:
                            st.markdown(f"- {workup_item}")
                    else:
                        st.caption("No additional workup is suggested based on the information already entered.")

        st.markdown("---")
        with st.expander("When to consider Hematology referral", expanded=False):
            referral_reasons: list[str] = []
            if hb is not None and hb < 7 and (symptomatic_any in ("Yes", "Unknown") or high_risk_symptoms in ("Yes", "Unknown")):
                referral_reasons.append("Severe anemia with symptoms or high-risk features.")
            if other_cytopenias == "Yes":
                referral_reasons.append("Anemia with another cytopenia or pancytopenia.")
            if smear_abnormal == "Yes":
                referral_reasons.append("Abnormal peripheral smear, especially blasts, schistocytes, dysplasia, or other concerning morphology.")
            if hemolysis_pattern:
                referral_reasons.append("Biochemical evidence of hemolysis that is severe, unexplained, or associated with abnormal morphology.")
            if referral_reasons:
                for reason in dedupe_lines(referral_reasons):
                    st.markdown(f"- {reason}")
            else:
                st.caption("No specific referral trigger was identified from the entered data. Clinical judgment still applies.")

st.markdown("---")
st.caption("AnemiaDx • Created by Manal Ahmidouch • GMA Clinic / Medical Education • Educational use only")
