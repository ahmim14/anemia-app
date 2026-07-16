import html

import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================
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

        /* Sidebar */
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

        /* App header */
        .app-header {
            position: relative;
            overflow: hidden;
            padding: 1.8rem 1.9rem;
            margin-bottom: 0.8rem;
            border-radius: 22px;
            border: 1px solid rgba(239, 68, 68, 0.28);
            background:
                radial-gradient(
                    circle at 92% 10%,
                    rgba(239, 68, 68, 0.24),
                    transparent 34%
                ),
                radial-gradient(
                    circle at 8% 90%,
                    rgba(127, 29, 29, 0.18),
                    transparent 38%
                ),
                linear-gradient(
                    135deg,
                    rgba(15, 23, 42, 0.98),
                    rgba(30, 41, 59, 0.96)
                );
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
            background: linear-gradient(
                90deg,
                #fecaca 0%,
                #ef4444 38%,
                #dc2626 68%,
                #991b1b 100%
            );
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

        /* Sidebar recommendation */
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

        /* Clinical impression */
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

        /* Iron interpretation */
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

        /* Mixed anemia */
        .mixed-card {
            padding: 0.95rem 1.05rem;
            border-radius: 14px;
            border: 1px solid #d97706;
            background: rgba(245, 158, 11, 0.11);
            margin: 0.65rem 0;
        }

        /* Etiology cards */
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

        .confidence-strong {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            background: #dcfce7;
            color: #166534 !important;
            font-size: 0.78rem;
            font-weight: 850;
            white-space: nowrap;
        }

        .confidence-supported {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            background: #dbeafe;
            color: #1d4ed8 !important;
            font-size: 0.78rem;
            font-weight: 850;
            white-space: nowrap;
        }

        .confidence-possible {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            background: #fef3c7;
            color: #92400e !important;
            font-size: 0.78rem;
            font-weight: 850;
            white-space: nowrap;
        }

        div[data-testid="stExpander"] {
            border-radius: 14px;
        }

        div[data-testid="stMetric"] {
            border: 1px solid rgba(148, 163, 184, 0.25);
            padding: 0.75rem;
            border-radius: 12px;
        }

        div.stButton > button {
            border-radius: 11px;
            font-weight: 700;
        }

        @media (max-width: 640px) {
            .app-header {
                padding: 1.4rem 1.25rem;
            }

            .app-title {
                font-size: 3.1rem;
            }

            .app-subtitle {
                font-size: 0.98rem;
            }
        }

        @media (prefers-color-scheme: light) {
            .summary-card {
                background: #f8fafc;
                border-color: #cbd5e1;
            }

            .summary-value {
                color: #0f172a;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# RESET
# ============================================================
def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.rerun()


# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
    <div class="app-header">
        <div class="app-title">AnemiaDx</div>
        <div class="app-subtitle">
            A stepwise approach to anemia evaluation, differential diagnosis,
            and resident education.
        </div>
        <div class="build-label">Clinical reasoning assistant</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Educational decision support only — not a substitute for clinical judgment."
)

reset_col, _ = st.columns([1.5, 4])

with reset_col:
    st.button(
        "↻ Start new evaluation",
        on_click=reset_app,
        use_container_width=True,
    )


# ============================================================
# HELPERS
# ============================================================
def to_float(value):
    value = (value or "").strip()

    if value == "":
        return None

    try:
        return float(value)
    except ValueError:
        return None


def fmt(value, digits=1, suffix=""):
    if value is None:
        return "—"

    try:
        return f"{value:.{digits}f}{suffix}"
    except (TypeError, ValueError):
        return f"{value}{suffix}"


def selected(value):
    if value in (None, "", "Select...", "Select…"):
        return None

    return value


def known_choice(value):
    return value not in (None, "Unknown")


def safe_text(value):
    return html.escape(str(value))


def dedupe_lines(lines):
    seen = set()
    output = []

    for line in lines:
        cleaned = (line or "").strip()

        if cleaned and cleaned not in seen:
            output.append(cleaned)
            seen.add(cleaned)

    return output


def add_dx(
    items,
    title,
    rationale,
    evidence=None,
    workup=None,
    confidence="Possible",
    priority=50,
):
    items.append(
        {
            "title": title,
            "rationale": rationale,
            "evidence": evidence or [],
            "workup": workup or [],
            "confidence": confidence,
            "priority": priority,
        }
    )


def dedupe_dx(items):
    seen = set()
    output = []

    for item in items:
        if item["title"] not in seen:
            output.append(item)
            seen.add(item["title"])

    return output


def maturation_factor(hct):
    if hct is None:
        return None

    if hct >= 40:
        return 1.0

    if hct >= 30:
        return 1.5

    if hct >= 20:
        return 2.0

    return 2.5


# ============================================================
# INPUT HIGHLIGHTING
# ============================================================
def field_style(label, status):
    palette = {
        "abnormal": {
            "border": "#dc2626",
            "background": "rgba(220, 38, 38, 0.18)",
        },
        "borderline": {
            "border": "#d97706",
            "background": "rgba(245, 158, 11, 0.18)",
        },
        "normal": {
            "border": "#16a34a",
            "background": "rgba(34, 197, 94, 0.14)",
        },
    }

    if status not in palette:
        return ""

    border = palette[status]["border"]
    background = palette[status]["background"]

    return f"""
        input[aria-label="{label}"] {{
            background: {background} !important;
            border: 2px solid {border} !important;
            box-shadow: 0 0 0 1px {border}33 !important;
        }}
    """


def inject_input_highlights(
    hb,
    sex,
    ferritin,
    tsat,
    b12,
    folate,
    tsh,
    egfr,
):
    rules = []

    if hb is not None and sex is not None:
        low_hb = (
            (sex == "Female" and hb < 12)
            or (sex == "Male" and hb < 13)
        )

        rules.append(
            field_style(
                "Hemoglobin (g/dL)",
                "abnormal" if low_hb else "normal",
            )
        )

    if ferritin is not None:
        if ferritin < 30:
            status = "abnormal"
        elif ferritin < 100:
            status = "borderline"
        else:
            status = "normal"

        rules.append(field_style("Ferritin (ng/mL)", status))

    if tsat is not None:
        rules.append(
            field_style(
                "Transferrin Saturation (%)",
                "abnormal" if tsat < 20 else "normal",
            )
        )

    if b12 is not None:
        if b12 < 200:
            status = "abnormal"
        elif b12 < 300:
            status = "borderline"
        else:
            status = "normal"

        rules.append(field_style("Vitamin B12 (pg/mL)", status))

    if folate is not None:
        rules.append(
            field_style(
                "Folate (ng/mL)",
                "abnormal" if folate < 4 else "normal",
            )
        )

    if tsh is not None:
        status = "abnormal" if tsh > 5 or tsh < 0.4 else "normal"
        rules.append(field_style("TSH (μIU/mL)", status))

    if egfr is not None:
        if egfr < 60:
            status = "abnormal"
        elif egfr < 90:
            status = "borderline"
        else:
            status = "normal"

        rules.append(
            field_style(
                "eGFR (mL/min/1.73m²)",
                status,
            )
        )

    if rules:
        st.markdown(
            "<style>" + "".join(rules) + "</style>",
            unsafe_allow_html=True,
        )


# ============================================================
# DATA COMPLETENESS
# ============================================================
def build_known(inputs):
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

    known["hemo_complete"] = (
        known["ldh"]
        and known["haptoglobin"]
        and known["indirect_bili"]
    )

    known["retic_any"] = (
        known["retic_pct"]
        or known["retic_qual"]
        or known["rpi"]
    )

    return known


# ============================================================
# IRON INTERPRETATION
# ============================================================
def interpret_iron_pattern(ferritin, tsat):
    if ferritin is None and tsat is None:
        return None

    if ferritin is not None and ferritin < 30:
        if tsat is not None and tsat < 20:
            return {
                "title": "Absolute iron deficiency pattern",
                "description": (
                    "Low ferritin with low transferrin saturation strongly "
                    "supports depleted iron stores."
                ),
            }

        return {
            "title": "Iron deficiency pattern",
            "description": (
                "Ferritin below 30 ng/mL supports depleted iron stores, "
                "even when MCV is normal."
            ),
        }

    if (
        ferritin is not None
        and ferritin >= 100
        and tsat is not None
        and tsat < 20
    ):
        return {
            "title": "Functional iron deficiency pattern",
            "description": (
                "Low transferrin saturation with preserved or elevated "
                "ferritin may occur with inflammation or chronic disease."
            ),
        }

    if (
        ferritin is not None
        and 30 <= ferritin < 100
        and tsat is not None
        and tsat < 20
    ):
        return {
            "title": "Possible iron deficiency or mixed inflammatory pattern",
            "description": (
                "Borderline ferritin with low transferrin saturation may "
                "represent iron deficiency, inflammation, or both."
            ),
        }

    if (
        ferritin is not None
        and ferritin >= 100
        and tsat is not None
        and tsat >= 20
    ):
        return {
            "title": "Iron deficiency not supported by entered studies",
            "description": (
                "The entered ferritin and transferrin saturation do not "
                "show a typical iron-deficiency pattern."
            ),
        }

    return {
        "title": "Incomplete iron-study pattern",
        "description": (
            "Enter both ferritin and transferrin saturation for a more "
            "specific interpretation."
        ),
    }


# ============================================================
# NEXT MOST INFORMATIVE
# ============================================================
def next_most_informative(
    mcv_cat,
    marrow_response,
    known,
    smear_abnormal,
):
    if mcv_cat == "Microcytic (<80)":
        if not known["iron_complete"]:
            return ["Complete iron studies with ferritin and TSAT"]

        return ["Assess bleeding source risk as clinically appropriate"]

    if mcv_cat == "Normocytic (80–100)":
        if not known["retic_any"]:
            return ["Reticulocyte count or RPI"]

        if marrow_response in (
            "Appropriate response",
            "Appropriate/high reticulocyte response",
        ):
            missing = []

            if not known["hemo_complete"]:
                missing.append("Complete hemolysis markers")

            if not known["smear"]:
                missing.append("Peripheral smear review")

            if missing:
                return missing

            return ["Differentiate blood loss from hemolysis"]

        return [
            "Evaluate iron status, kidney function, inflammation, and marrow suppression"
        ]

    if mcv_cat == "Macrocytic (>100)":
        if not known["vits_complete"]:
            return ["Vitamin B12 and folate"]

        if not known["tsh"]:
            return ["TSH"]

        if smear_abnormal is None:
            return ["Peripheral smear result"]

        return [
            "Review medications, alcohol exposure, liver disease, and marrow causes"
        ]

    return ["Select an MCV category"]


# ============================================================
# PROGRESSIVE REASONING MAP
# ============================================================
def progressive_tree_dot(
    mcv_cat,
    marrow_response,
    known,
    iron_pattern,
):
    nodes = [("Start", "Start")]

    if mcv_cat is None:
        nodes.append(("MCV", "Select MCV"))

    else:
        nodes.append(("MCV", mcv_cat))

        if mcv_cat == "Microcytic (<80)":
            nodes.append(("Path", "Microcytic pathway"))

            if not known["iron_complete"]:
                nodes.append(("Current", "Complete iron studies"))
            elif iron_pattern:
                nodes.append(("Current", iron_pattern["title"]))

        elif mcv_cat == "Normocytic (80–100)":
            nodes.append(("Path", "Normocytic pathway"))

            if not known["retic_any"]:
                nodes.append(("Current", "Obtain reticulocyte response"))
            else:
                nodes.append(("Retic", marrow_response))

                if marrow_response in (
                    "Appropriate response",
                    "Appropriate/high reticulocyte response",
                ):
                    if not known["hemo_complete"]:
                        nodes.append(
                            ("Current", "Complete hemolysis evaluation")
                        )
                    else:
                        nodes.append(
                            ("Current", "Blood loss vs hemolysis")
                        )
                else:
                    nodes.append(
                        ("Current", "Underproduction evaluation")
                    )

        elif mcv_cat == "Macrocytic (>100)":
            nodes.append(("Path", "Macrocytic pathway"))

            if not known["vits_complete"]:
                nodes.append(("Current", "Check B12 and folate"))
            elif not known["tsh"]:
                nodes.append(("Current", "Check TSH"))
            else:
                nodes.append(
                    (
                        "Current",
                        "Review liver, medications, alcohol, and marrow causes",
                    )
                )

    dot = [
        "digraph G {",
        "rankdir=TB;",
        "splines=polyline;",
        "nodesep=0.35;",
        "ranksep=0.45;",
        'graph [bgcolor="transparent", margin=0.05];',
        (
            'node [shape=box, style="rounded,filled", '
            'fontname="Helvetica", fontsize=12, '
            'color="#15803d", fontcolor="#111827", '
            'fillcolor="#ecfdf5", penwidth=1.4, '
            'margin="0.18,0.13"];'
        ),
        'edge [color="#94a3b8", penwidth=1.5, arrowsize=0.8];',
    ]

    for node_id, label in nodes:
        escaped = label.replace('"', "'").replace("\n", "\\n")
        dot.append(f'{node_id} [label="{escaped}"];')

    for index in range(len(nodes) - 1):
        dot.append(
            f"{nodes[index][0]} -> {nodes[index + 1][0]};"
        )

    dot.append("}")

    return "\n".join(dot)


# ============================================================
# FILTER ALREADY COMPLETED TESTS
# ============================================================
def filter_suggestions(lines, known):
    filtered = []

    for line in lines:
        lower = line.lower()

        if "peripheral smear" in lower and known["smear"]:
            continue

        if (
            ("reticulocyte" in lower or "rpi" in lower)
            and known["retic_any"]
        ):
            continue

        if (
            (
                "ferritin" in lower
                or "tsat" in lower
                or "iron studies" in lower
            )
            and known["iron_complete"]
        ):
            continue

        if (
            ("b12" in lower or "folate" in lower)
            and known["vits_complete"]
        ):
            continue

        if "tsh" in lower and known["tsh"]:
            continue

        if (
            ("egfr" in lower or "creatinine" in lower)
            and known["egfr"]
        ):
            continue

        if (
            (
                "hemolysis markers" in lower
                or "ldh" in lower
                or "haptoglobin" in lower
                or "indirect bilirubin" in lower
            )
            and known["hemo_complete"]
        ):
            continue

        filtered.append(line)

    return dedupe_lines(filtered)


# ============================================================
# MODE TOGGLES
# ============================================================
toggle_col_1, toggle_col_2 = st.columns([2, 1])

with toggle_col_1:
    teaching_mode = st.toggle(
        "Teaching Mode (live tree + reasoning)",
        value=False,
        key="teaching_mode",
    )

with toggle_col_2:
    show_all_details = (
        st.toggle(
            "Expand diagnosis details",
            value=False,
            key="show_all_details",
        )
        if teaching_mode
        else False
    )


# ============================================================
# SYMPTOMS
# ============================================================
st.header("Symptoms & severity")

symptom_col_1, symptom_col_2 = st.columns(2)

with symptom_col_1:
    symptomatic_any = selected(
        st.selectbox(
            "Is the patient symptomatic from anemia?",
            ["Select...", "Yes", "No", "Unknown"],
            help=(
                "Examples include dyspnea, fatigue limiting function, "
                "dizziness, chest pain, or syncope."
            ),
            key="symptomatic_any",
        )
    )

    high_risk_symptoms = selected(
        st.selectbox(
            "Any high-risk symptoms/signs?",
            ["Select...", "Yes", "No", "Unknown"],
            help=(
                "Examples include chest pain, dyspnea at rest, syncope, "
                "hemodynamic instability, or active bleeding."
            ),
            key="high_risk_symptoms",
        )
    )

with symptom_col_2:
    active_bleeding = selected(
        st.selectbox(
            "Concern for active/ongoing bleeding?",
            ["Select...", "Yes", "No", "Unknown"],
            key="active_bleeding",
        )
    )

    cvd = selected(
        st.selectbox(
            "Significant cardiovascular disease (CAD/HF) present?",
            ["Select...", "Yes", "No", "Unknown"],
            key="cvd",
        )
    )


# ============================================================
# CBC
# ============================================================
st.header("CBC basics")

cbc_col_1, cbc_col_2 = st.columns(2)

with cbc_col_1:
    hb = to_float(
        st.text_input(
            "Hemoglobin (g/dL)",
            placeholder="leave blank if unknown",
            key="hb",
        )
    )

    hct = to_float(
        st.text_input(
            "Hematocrit (%)",
            placeholder="leave blank if unknown",
            key="hct",
        )
    )

with cbc_col_2:
    sex = selected(
        st.selectbox(
            "Sex",
            ["Select...", "Female", "Male"],
            key="sex",
        )
    )

    mcv_cat = selected(
        st.selectbox(
            "MCV category",
            [
                "Select...",
                "Microcytic (<80)",
                "Normocytic (80–100)",
                "Macrocytic (>100)",
            ],
            help="The primary branch for the anemia evaluation.",
            key="mcv_cat",
        )
    )

    rdw = selected(
        st.selectbox(
            "RDW",
            ["Select...", "Normal", "High", "Unknown"],
            key="rdw",
        )
    )


other_cytopenias = None
rapid_onset = None
smear_abnormal = None

with st.expander("CBC context (optional)", expanded=False):
    context_col_1, context_col_2, context_col_3 = st.columns(3)

    with context_col_1:
        other_cytopenias = selected(
            st.selectbox(
                "Other cytopenias?",
                ["Select...", "Yes", "No", "Unknown"],
                help="Low white blood cell or platelet count.",
                key="other_cytopenias",
            )
        )

    with context_col_2:
        rapid_onset = selected(
            st.selectbox(
                "Rapid onset or acute Hb drop?",
                ["Select...", "Yes", "No", "Unknown"],
                key="rapid_onset",
            )
        )

    with context_col_3:
        smear_abnormal = selected(
            st.selectbox(
                "Peripheral smear abnormal?",
                ["Select...", "Yes", "No", "Unknown"],
                key="smear_abnormal",
            )
        )


# ============================================================
# RETICULOCYTES
# ============================================================
st.subheader("Reticulocytes")

retic_qual = None
retic_pct = None
rpi = None
corrected_retic = None
mf = None

with st.expander(
    "Reticulocyte count / RPI",
    expanded=(mcv_cat == "Normocytic (80–100)"),
):
    retic_mode = st.radio(
        "Reticulocyte input",
        ["Qualitative", "Numeric (%)"],
        horizontal=True,
        key="retic_mode",
    )

    if retic_mode == "Qualitative":
        retic_qual = selected(
            st.selectbox(
                "Reticulocyte count",
                ["Select...", "Low", "Normal", "High"],
                key="retic_qual",
            )
        )

    else:
        retic_pct = to_float(
            st.text_input(
                "Reticulocyte %",
                placeholder="leave blank if unknown",
                key="retic_pct",
            )
        )

    expected_hct_input = to_float(
        st.text_input(
            "Expected Hematocrit (%)",
            placeholder="40",
            key="expected_hct",
        )
    )

    expected_hct = (
        expected_hct_input
        if expected_hct_input is not None
        else 40.0
    )

    mf = maturation_factor(hct)

    if (
        retic_pct is not None
        and hct is not None
        and expected_hct > 0
    ):
        corrected_retic = retic_pct * (hct / expected_hct)

        if mf:
            rpi = corrected_retic / mf

    metric_col_1, metric_col_2, metric_col_3 = st.columns(3)

    with metric_col_1:
        st.metric("Corrected retic", fmt(corrected_retic, 2, "%"))

    with metric_col_2:
        st.metric("Maturation factor", fmt(mf, 1))

    with metric_col_3:
        st.metric("RPI", fmt(rpi, 2))

    if rpi is not None:
        if rpi < 2:
            st.info(
                "**RPI < 2:** inadequate marrow response, supporting "
                "underproduction physiology."
            )
        else:
            st.info(
                "**RPI ≥ 2:** appropriate marrow response, supporting "
                "blood loss, hemolysis, or recovery."
            )

    elif retic_qual == "High":
        st.info(
            "**High reticulocyte count:** suggests an appropriate "
            "marrow response."
        )

    elif retic_qual == "Low":
        st.info(
            "**Low reticulocyte count:** suggests underproduction physiology."
        )

    elif retic_qual == "Normal":
        st.info(
            "A normal reticulocyte count may still be inappropriately low "
            "when significant anemia is present."
        )

    else:
        st.caption(
            "Enter reticulocyte data to assess the marrow response."
        )


marrow_response = "Unknown"

if rpi is not None:
    marrow_response = (
        "Appropriate response"
        if rpi >= 2
        else "Inadequate response"
    )

elif retic_qual == "High":
    marrow_response = "Appropriate/high reticulocyte response"

elif retic_qual == "Low":
    marrow_response = "Inadequate/low reticulocyte response"


# ============================================================
# KEY LABS
# ============================================================
st.header("Key labs")

ferritin = None
tsat = None

with st.expander(
    "Iron studies",
    expanded=(mcv_cat == "Microcytic (<80)"),
):
    iron_col_1, iron_col_2 = st.columns(2)

    with iron_col_1:
        ferritin = to_float(
            st.text_input(
                "Ferritin (ng/mL)",
                placeholder="leave blank if unknown",
                key="ferritin",
            )
        )

    with iron_col_2:
        tsat = to_float(
            st.text_input(
                "Transferrin Saturation (%)",
                placeholder="leave blank if unknown",
                key="tsat",
            )
        )


b12 = None
folate = None

with st.expander(
    "Vitamin B12 / folate",
    expanded=(mcv_cat == "Macrocytic (>100)"),
):
    vitamin_col_1, vitamin_col_2 = st.columns(2)

    with vitamin_col_1:
        b12 = to_float(
            st.text_input(
                "Vitamin B12 (pg/mL)",
                placeholder="leave blank if unknown",
                key="b12",
            )
        )

    with vitamin_col_2:
        folate = to_float(
            st.text_input(
                "Folate (ng/mL)",
                placeholder="leave blank if unknown",
                key="folate",
            )
        )


ldh = None
haptoglobin = None
indirect_bili = None

with st.expander(
    "Hemolysis markers",
    expanded=marrow_response in (
        "Appropriate response",
        "Appropriate/high reticulocyte response",
    ),
):
    hemo_col_1, hemo_col_2, hemo_col_3 = st.columns(3)

    with hemo_col_1:
        ldh = selected(
            st.selectbox(
                "LDH",
                ["Select...", "Normal", "High", "Unknown"],
                key="ldh",
            )
        )

    with hemo_col_2:
        haptoglobin = selected(
            st.selectbox(
                "Haptoglobin",
                ["Select...", "Normal", "Low", "Unknown"],
                key="haptoglobin",
            )
        )

    with hemo_col_3:
        indirect_bili = selected(
            st.selectbox(
                "Indirect bilirubin",
                ["Select...", "Normal", "High", "Unknown"],
                key="indirect_bili",
            )
        )


tsh = None
egfr = None

with st.expander(
    "Other contributors",
    expanded=mcv_cat in (
        "Normocytic (80–100)",
        "Macrocytic (>100)",
    ),
):
    other_col_1, other_col_2 = st.columns(2)

    with other_col_1:
        tsh = to_float(
            st.text_input(
                "TSH (μIU/mL)",
                placeholder="leave blank if unknown",
                key="tsh",
            )
        )

    with other_col_2:
        egfr = to_float(
            st.text_input(
                "eGFR (mL/min/1.73m²)",
                placeholder="leave blank if unknown",
                key="egfr",
            )
        )


with st.expander(
    "High-yield medications and exposures",
    expanded=False,
):
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


inject_input_highlights(
    hb=hb,
    sex=sex,
    ferritin=ferritin,
    tsat=tsat,
    b12=b12,
    folate=folate,
    tsh=tsh,
    egfr=egfr,
)


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

iron_pattern = interpret_iron_pattern(
    ferritin=ferritin,
    tsat=tsat,
)


# ============================================================
# TEACHING SIDEBAR
# ============================================================
if teaching_mode:
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-title">Live reasoning map</div>',
            unsafe_allow_html=True,
        )

        next_items = next_most_informative(
            mcv_cat=mcv_cat,
            marrow_response=marrow_response,
            known=known,
            smear_abnormal=smear_abnormal,
        )

        next_text = "<br>".join(
            safe_text(item)
            for item in next_items
        )

        st.markdown(
            (
                '<div class="next-card">'
                '<div class="next-card-label">'
                'Next most informative'
                "</div>"
                '<div class="next-card-value">'
                f"{next_text}"
                "</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        st.graphviz_chart(
            progressive_tree_dot(
                mcv_cat=mcv_cat,
                marrow_response=marrow_response,
                known=known,
                iron_pattern=iron_pattern,
            ),
            use_container_width=True,
        )

        st.caption(
            "Only the active clinical pathway is displayed."
        )


# ============================================================
# CLINICAL SUMMARY
# ============================================================
st.markdown("---")
st.header("Clinical summary")

if mcv_cat is None:
    st.info(
        "Select an MCV category to generate the clinical impression "
        "and ranked differential."
    )

else:
    no_anemia = False

    if hb is not None and sex is not None:
        no_anemia = (
            (sex == "Female" and hb >= 12)
            or (sex == "Male" and hb >= 13)
        )

    if no_anemia:
        st.success(
            "No anemia is detected using the entered hemoglobin "
            "and sex-specific threshold."
        )

        st.caption(
            "Consider non-anemia causes of symptoms or repeat testing "
            "when clinically appropriate."
        )

    else:
        dx = []

        # Microcytic
        if mcv_cat == "Microcytic (<80)":
            if (
                ferritin is not None
                and ferritin >= 100
                and tsat is not None
                and tsat < 20
            ):
                add_dx(
                    dx,
                    title=(
                        "Anemia of chronic inflammation with "
                        "functional iron deficiency"
                    ),
                    rationale=(
                        "Low iron availability with preserved or elevated "
                        "ferritin may reflect inflammation-mediated iron restriction."
                    ),
                    evidence=[
                        f"Ferritin {fmt(ferritin, 0)} ng/mL",
                        f"TSAT {fmt(tsat, 0, '%')}",
                        "Microcytosis",
                    ],
                    workup=[
                        "Review chronic inflammatory or infectious conditions",
                        "Consider CRP or ESR when clinically indicated",
                    ],
                    confidence="Supported",
                    priority=15,
                )

            elif not (
                ferritin is not None
                and ferritin < 30
            ):
                evidence = ["Microcytosis"]

                if ferritin is not None:
                    evidence.append(
                        f"Ferritin {fmt(ferritin, 0)} ng/mL"
                    )

                add_dx(
                    dx,
                    title="Thalassemia trait / hemoglobinopathy",
                    rationale=(
                        "Microcytosis without clearly depleted iron stores "
                        "raises consideration of thalassemia trait or another "
                        "hemoglobinopathy."
                    ),
                    evidence=evidence,
                    workup=[
                        "Review RBC count and RDW",
                        "Hemoglobin electrophoresis",
                        "Peripheral smear review if not already available",
                    ],
                    confidence="Possible",
                    priority=35,
                )

        # Normocytic
        elif mcv_cat == "Normocytic (80–100)":
            if marrow_response in (
                "Appropriate response",
                "Appropriate/high reticulocyte response",
            ):
                add_dx(
                    dx,
                    title="Blood loss",
                    rationale=(
                        "An appropriate marrow response can occur after "
                        "acute or ongoing blood loss."
                    ),
                    evidence=[
                        "Normocytic anemia",
                        marrow_response,
                    ],
                    workup=[
                        "Assess overt and occult bleeding history",
                        "Evaluate GI or gynecologic sources as appropriate",
                    ],
                    confidence="Supported",
                    priority=20,
                )

                add_dx(
                    dx,
                    title="Hemolysis",
                    rationale=(
                        "An appropriate reticulocyte response may reflect "
                        "increased red-cell destruction."
                    ),
                    evidence=[
                        "Normocytic anemia",
                        marrow_response,
                    ],
                    workup=[
                        "Complete hemolysis markers",
                        "DAT when immune hemolysis is suspected",
                        "Peripheral smear review if not already available",
                    ],
                    confidence="Possible",
                    priority=25,
                )

            else:
                add_dx(
                    dx,
                    title="Anemia of chronic inflammation",
                    rationale=(
                        "A normocytic anemia with an inadequate or unknown "
                        "marrow response commonly occurs with chronic disease."
                    ),
                    evidence=[
                        "Normocytic anemia",
                        marrow_response,
                    ],
                    workup=[
                        "Review chronic inflammatory disease burden",
                        "Complete iron studies",
                        "Consider inflammatory markers when indicated",
                    ],
                    confidence="Possible",
                    priority=30,
                )

                if egfr is not None and egfr < 60:
                    add_dx(
                        dx,
                        title="Anemia associated with chronic kidney disease",
                        rationale=(
                            "Reduced kidney function may cause a "
                            "hypoproliferative normocytic anemia."
                        ),
                        evidence=[
                            f"eGFR {fmt(egfr, 0)}",
                            "Normocytic anemia",
                        ],
                        workup=[
                            "Confirm iron sufficiency",
                            "Review kidney-disease severity and trend",
                        ],
                        confidence="Supported",
                        priority=18,
                    )

                if (
                    other_cytopenias == "Yes"
                    or smear_abnormal == "Yes"
                    or marrow_response in (
                        "Inadequate response",
                        "Inadequate/low reticulocyte response",
                    )
                ):
                    evidence = ["Underproduction pattern"]

                    if other_cytopenias == "Yes":
                        evidence.append("Additional cytopenias")

                    if smear_abnormal == "Yes":
                        evidence.append("Abnormal smear")

                    add_dx(
                        dx,
                        title="Bone marrow process or marrow suppression",
                        rationale=(
                            "An inadequate marrow response, other cytopenias, "
                            "or abnormal morphology may indicate marrow pathology "
                            "or medication-related suppression."
                        ),
                        evidence=evidence,
                        workup=[
                            "Trend complete blood count",
                            "Review medication and exposure history",
                            "Consider hematology evaluation if unexplained",
                        ],
                        confidence=(
                            "Supported"
                            if (
                                other_cytopenias == "Yes"
                                or smear_abnormal == "Yes"
                            )
                            else "Possible"
                        ),
                        priority=22,
                    )

        # Macrocytic
        elif mcv_cat == "Macrocytic (>100)":
            if (
                (b12 is None or b12 >= 200)
                and (folate is None or folate >= 4)
            ):
                evidence = ["Macrocytosis"]

                if b12 is not None:
                    evidence.append(
                        f"B12 {fmt(b12, 0)} pg/mL"
                    )

                if folate is not None:
                    evidence.append(
                        f"Folate {fmt(folate, 1)} ng/mL"
                    )

                add_dx(
                    dx,
                    title="Non-megaloblastic macrocytosis or marrow disorder",
                    rationale=(
                        "When B12 and folate are not low, consider alcohol, "
                        "liver disease, hypothyroidism, medication effects, "
                        "reticulocytosis, or marrow pathology."
                    ),
                    evidence=evidence,
                    workup=[
                        "Review medications and alcohol exposure",
                        "Consider liver testing",
                        "Check TSH if not already entered",
                        "Consider hematology evaluation if persistent or unexplained",
                    ],
                    confidence="Possible",
                    priority=30,
                )

        # Global iron deficiency
        if ferritin is not None and ferritin < 30:
            evidence = [
                f"Ferritin {fmt(ferritin, 0)} ng/mL",
                f"MCV: {mcv_cat.split(' ')[0]}",
            ]

            if tsat is not None:
                evidence.append(
                    f"TSAT {fmt(tsat, 0, '%')}"
                )

            add_dx(
                dx,
                title="Iron deficiency anemia",
                rationale=(
                    "Low ferritin supports depleted iron stores. Iron "
                    "deficiency may remain normocytic early or when mixed "
                    "with another process."
                ),
                evidence=evidence,
                workup=[
                    "Assess GI and menstrual blood loss as appropriate",
                    "Consider malabsorption or celiac disease when indicated",
                    "Treat iron deficiency and monitor hematologic response",
                ],
                confidence=(
                    "Strongly supported"
                    if tsat is not None and tsat < 20
                    else "Supported"
                ),
                priority=5,
            )

        # B12
        if b12 is not None and b12 < 200:
            add_dx(
                dx,
                title="Vitamin B12 deficiency",
                rationale=(
                    "A low vitamin B12 level supports a megaloblastic "
                    "process, although MCV may be normal or low in mixed anemia."
                ),
                evidence=[
                    f"B12 {fmt(b12, 0)} pg/mL",
                    f"MCV: {mcv_cat.split(' ')[0]}",
                ],
                workup=[
                    "Assess dietary and malabsorption risk",
                    "Consider intrinsic-factor antibody testing",
                    "Consider MMA when the result or clinical context is uncertain",
                ],
                confidence="Strongly supported",
                priority=7,
            )

        elif b12 is not None and 200 <= b12 < 300:
            add_dx(
                dx,
                title="Borderline vitamin B12 status",
                rationale=(
                    "Borderline vitamin B12 may warrant biochemical "
                    "confirmation when symptoms or macrocytosis are present."
                ),
                evidence=[
                    f"B12 {fmt(b12, 0)} pg/mL",
                ],
                workup=[
                    "Consider methylmalonic acid",
                    "Assess dietary and malabsorption risk",
                ],
                confidence="Possible",
                priority=28,
            )

        # Folate
        if folate is not None and folate < 4:
            add_dx(
                dx,
                title="Folate deficiency",
                rationale=(
                    "A low folate level supports a megaloblastic process."
                ),
                evidence=[
                    f"Folate {fmt(folate, 1)} ng/mL",
                ],
                workup=[
                    "Assess nutrition and alcohol exposure",
                    "Review folate-antagonist medications",
                ],
                confidence="Strongly supported",
                priority=8,
            )

        # Hemolysis
        hemolysis_pattern = (
            ldh == "High"
            and haptoglobin == "Low"
            and indirect_bili == "High"
        )

        if hemolysis_pattern:
            add_dx(
                dx,
                title="Hemolysis",
                rationale=(
                    "High LDH, low haptoglobin, and elevated indirect "
                    "bilirubin form a classic biochemical hemolysis pattern."
                ),
                evidence=[
                    "High LDH",
                    "Low haptoglobin",
                    "High indirect bilirubin",
                ],
                workup=[
                    "DAT when immune hemolysis is suspected",
                    "Review peripheral smear findings",
                    "Consider G6PD testing when clinically indicated",
                ],
                confidence="Strongly supported",
                priority=4,
            )

        # Thyroid
        if tsh is not None and tsh > 5:
            add_dx(
                dx,
                title="Hypothyroidism-associated anemia",
                rationale=(
                    "An elevated TSH may contribute to normocytic or "
                    "macrocytic anemia."
                ),
                evidence=[
                    f"TSH {fmt(tsh, 2)} μIU/mL",
                ],
                workup=[
                    "Review free T4",
                    "Address thyroid dysfunction as clinically appropriate",
                ],
                confidence="Supported",
                priority=24,
            )

        # Smear
        if smear_abnormal == "Yes":
            add_dx(
                dx,
                title="Abnormal peripheral smear requiring directed evaluation",
                rationale=(
                    "The smear is already known to be abnormal. Evaluation "
                    "should be guided by the specific morphology rather than "
                    "repeating a generic smear recommendation."
                ),
                evidence=["Abnormal smear documented"],
                workup=[
                    "Identify the reported morphology",
                    "Correlate morphology with CBC, reticulocytes, and hemolysis markers",
                    "Consider hematology input for blasts, schistocytes, or dysplasia",
                ],
                confidence="Supported",
                priority=3,
            )

        # Medications/exposures
        if "NSAIDs / aspirin (chronic)" in exposures:
            add_dx(
                dx,
                title="Medication-associated occult gastrointestinal blood loss",
                rationale=(
                    "Chronic NSAID or aspirin use may contribute to "
                    "gastritis, ulceration, and occult blood loss."
                ),
                evidence=["Chronic NSAID or aspirin exposure"],
                workup=[
                    "Assess gastrointestinal symptoms",
                    "Review medication indication and alternatives",
                ],
                confidence="Possible",
                priority=42,
            )

        if "Anticoagulant/antiplatelet use" in exposures:
            add_dx(
                dx,
                title="Bleeding-risk contribution from antithrombotic therapy",
                rationale=(
                    "Anticoagulants and antiplatelet medications may worsen "
                    "bleeding or reveal an occult bleeding source."
                ),
                evidence=["Antithrombotic exposure"],
                workup=[
                    "Review medication indication",
                    "Assess overt and occult bleeding",
                ],
                confidence="Possible",
                priority=45,
            )

        if (
            "PPI (long-term)" in exposures
            or "Metformin (long-term)" in exposures
        ):
            add_dx(
                dx,
                title="Medication-associated vitamin B12 deficiency risk",
                rationale=(
                    "Long-term proton-pump inhibitor or metformin use may "
                    "reduce vitamin B12 absorption."
                ),
                evidence=[
                    "Long-term PPI or metformin exposure",
                ],
                workup=[
                    "Check vitamin B12 if not already entered",
                    "Assess neurologic or mucosal symptoms",
                ],
                confidence="Possible",
                priority=46,
            )

        if "Alcohol use (heavy)" in exposures:
            add_dx(
                dx,
                title="Alcohol-associated macrocytosis or nutritional deficiency",
                rationale=(
                    "Heavy alcohol use may cause macrocytosis and increase "
                    "risk of folate deficiency or liver disease."
                ),
                evidence=["Heavy alcohol exposure"],
                workup=[
                    "Review liver tests",
                    "Assess B12 and folate",
                    "Offer counseling or treatment resources when appropriate",
                ],
                confidence="Possible",
                priority=40,
            )

        marrow_toxic_exposures = {
            "Chemotherapy / antimetabolites",
            "Hydroxyurea",
            "Folate-antagonist medication",
            "Linezolid",
            "Valproate",
            "Marrow-toxic antiviral",
        }

        if any(
            exposure in marrow_toxic_exposures
            for exposure in exposures
        ):
            add_dx(
                dx,
                title="Medication-associated marrow suppression or macrocytosis",
                rationale=(
                    "Several entered medications may suppress marrow activity "
                    "or cause macrocytosis."
                ),
                evidence=["Potentially marrow-toxic medication"],
                workup=[
                    "Review timing relative to anemia onset",
                    "Trend complete blood count",
                    "Consider hematology evaluation if severe or persistent",
                ],
                confidence="Possible",
                priority=38,
            )

        dx = dedupe_dx(
            sorted(
                dx,
                key=lambda item: item["priority"],
            )
        )

        # Mixed-anemia recognition
        mixed_findings = []

        if (
            mcv_cat == "Normocytic (80–100)"
            and ferritin is not None
            and ferritin < 30
        ):
            mixed_findings.append(
                "Normal MCV does not exclude iron deficiency; this may "
                "represent early iron deficiency or a mixed anemia."
            )

        if (
            rdw == "High"
            and mcv_cat == "Normocytic (80–100)"
        ):
            mixed_findings.append(
                "High RDW with a normal MCV may reflect competing "
                "microcytic and macrocytic processes."
            )

        if (
            mcv_cat == "Microcytic (<80)"
            and (
                (b12 is not None and b12 < 200)
                or (folate is not None and folate < 4)
            )
        ):
            mixed_findings.append(
                "Vitamin deficiency with microcytosis suggests a possible "
                "mixed anemia in which a microcytic process masks macrocytosis."
            )

        if "Recent transfusion (last 3 months)" in exposures:
            mixed_findings.append(
                "Recent transfusion may alter MCV and RDW, reducing the "
                "reliability of morphology-based classification."
            )

        # Clinical impression
        morphology = mcv_cat.split(" ")[0].lower()
        physiology = ""

        if marrow_response in (
            "Appropriate response",
            "Appropriate/high reticulocyte response",
        ):
            physiology = " with an appropriate marrow response"

        elif marrow_response in (
            "Inadequate response",
            "Inadequate/low reticulocyte response",
        ):
            physiology = " with an inadequate marrow response"

        if dx:
            top_titles = [item["title"] for item in dx[:2]]

            if len(top_titles) == 1:
                clinical_impression = (
                    f"{morphology.capitalize()} anemia{physiology}; "
                    f"{top_titles[0]} is the leading consideration."
                )

            else:
                clinical_impression = (
                    f"{morphology.capitalize()} anemia{physiology}; "
                    f"leading considerations are {top_titles[0]} and "
                    f"{top_titles[1]}."
                )

        else:
            clinical_impression = (
                f"{morphology.capitalize()} anemia{physiology}; "
                "additional laboratory data are needed to identify "
                "the leading etiology."
            )

        st.markdown(
            (
                '<div class="summary-card">'
                '<div class="summary-label">Clinical impression</div>'
                '<div class="summary-value">'
                f"{safe_text(clinical_impression)}"
                "</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        # Iron pattern
        if iron_pattern is not None:
            st.markdown(
                (
                    '<div class="iron-pattern">'
                    '<div class="iron-pattern-title">'
                    f"{safe_text(iron_pattern['title'])}"
                    "</div>"
                    "<div>"
                    f"{safe_text(iron_pattern['description'])}"
                    "</div>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

        # Mixed pattern
        if mixed_findings:
            mixed_html = "".join(
                f"<li>{safe_text(item)}</li>"
                for item in mixed_findings
            )

            st.markdown(
                (
                    '<div class="mixed-card">'
                    "<strong>Mixed or potentially masked anemia pattern</strong>"
                    '<ul style="margin-top:0.5rem; margin-bottom:0;">'
                    f"{mixed_html}"
                    "</ul>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

        # Data completeness
        completed_groups = sum(
            [
                known["iron_complete"],
                known["retic_any"],
                known["vits_complete"],
                known["hemo_complete"],
                known["tsh"] or known["egfr"],
            ]
        )

        if completed_groups <= 1:
            completeness = "Low"
            completeness_color = "#dc2626"

        elif completed_groups <= 3:
            completeness = "Moderate"
            completeness_color = "#d97706"

        else:
            completeness = "High"
            completeness_color = "#16a34a"

        st.markdown("#### Data completeness")

        st.markdown(
            (
                '<span style="'
                "display:inline-block;"
                "padding:5px 11px;"
                "border-radius:999px;"
                f"background:{completeness_color};"
                "color:#ffffff;"
                "font-size:0.82rem;"
                "font-weight:800;"
                '">'
                f"{completeness}"
                "</span>"
            ),
            unsafe_allow_html=True,
        )

        st.caption(
            "Completeness reflects whether major diagnostic laboratory "
            "groups have been entered."
        )

        # Recommended next steps
        st.markdown("#### Recommended next steps")

        base_steps = next_most_informative(
            mcv_cat=mcv_cat,
            marrow_response=marrow_response,
            known=known,
            smear_abnormal=smear_abnormal,
        )

        general_steps = [
            "Peripheral smear review",
            "Reticulocyte count or RPI",
            "Complete iron studies with ferritin and TSAT",
            "Vitamin B12 and folate",
            "Complete hemolysis markers",
            "TSH",
            "eGFR or creatinine",
        ]

        filtered_steps = filter_suggestions(
            base_steps + general_steps,
            known,
        )

        tests = []
        actions = []

        action_terms = (
            "assess",
            "review",
            "evaluate",
            "differentiate",
            "consider",
            "monitor",
            "trend",
        )

        for step in filtered_steps:
            if any(
                term in step.lower()
                for term in action_terms
            ):
                actions.append(step)
            else:
                tests.append(step)

        tests = dedupe_lines(tests)[:3]
        actions = dedupe_lines(actions)[:3]

        next_col_1, next_col_2 = st.columns(2)

        with next_col_1:
            st.markdown("**Next tests**")

            if tests:
                for test in tests:
                    st.markdown(f"- {test}")
            else:
                st.caption(
                    "No additional high-priority tests identified."
                )

        with next_col_2:
            st.markdown("**Next clinical actions**")

            if actions:
                for action in actions:
                    st.markdown(f"- {action}")
            else:
                st.caption(
                    "No additional high-priority clinical actions identified."
                )

        # ========================================================
        # MOST LIKELY ETIOLOGIES + DETAILS IN ONE PLACE
        # ========================================================
        st.header("Most likely etiologies")

        if not dx:
            st.info(
                "Enter additional data to generate a ranked differential."
            )

        else:
            for index, item in enumerate(dx[:3], start=1):
                if item["confidence"] == "Strongly supported":
                    confidence_class = "confidence-strong"

                elif item["confidence"] == "Supported":
                    confidence_class = "confidence-supported"

                else:
                    confidence_class = "confidence-possible"

                evidence_html = "".join(
                    f'<span class="evidence-chip">{safe_text(evidence)}</span>'
                    for evidence in item["evidence"]
                )

                card_html = (
                    '<div class="etiology-card">'
                    '<div style="display:flex;'
                    'justify-content:space-between;'
                    'gap:1rem;'
                    'align-items:flex-start;">'
                    '<div class="etiology-title">'
                    f'{index}. {safe_text(item["title"])}'
                    "</div>"
                    f'<span class="{confidence_class}">'
                    f'{safe_text(item["confidence"])}'
                    "</span>"
                    "</div>"
                    '<div style="margin-top:0.55rem;">'
                    f"{evidence_html}"
                    "</div>"
                    "</div>"
                )

                st.markdown(
                    card_html,
                    unsafe_allow_html=True,
                )

                with st.expander(
                    "Why this diagnosis and suggested workup",
                    expanded=show_all_details,
                ):
                    st.markdown(
                        f"**Why it was selected:** {item['rationale']}"
                    )

                    filtered_workup = filter_suggestions(
                        item["workup"],
                        known,
                    )

                    if filtered_workup:
                        st.markdown("**Suggested next workup:**")

                        for workup_item in filtered_workup:
                            st.markdown(f"- {workup_item}")

                    else:
                        st.caption(
                            "No additional workup is suggested based on "
                            "the information already entered."
                        )

        # Hematology referral
        st.markdown("---")

        with st.expander(
            "When to consider Hematology referral",
            expanded=False,
        ):
            referral_reasons = []

            if (
                hb is not None
                and hb < 7
                and (
                    symptomatic_any in ("Yes", "Unknown")
                    or high_risk_symptoms in ("Yes", "Unknown")
                )
            ):
                referral_reasons.append(
                    "Severe anemia with symptoms or high-risk features."
                )

            if other_cytopenias == "Yes":
                referral_reasons.append(
                    "Anemia with another cytopenia or pancytopenia."
                )

            if smear_abnormal == "Yes":
                referral_reasons.append(
                    "Abnormal peripheral smear, especially blasts, "
                    "schistocytes, dysplasia, or other concerning morphology."
                )

            if hemolysis_pattern:
                referral_reasons.append(
                    "Biochemical evidence of hemolysis that is severe, "
                    "unexplained, or associated with abnormal morphology."
                )

            if (
                mcv_cat == "Macrocytic (>100)"
                and known["vits_complete"]
                and (
                    other_cytopenias == "Yes"
                    or smear_abnormal == "Yes"
                )
            ):
                referral_reasons.append(
                    "Macrocytosis with cytopenias or abnormal morphology "
                    "despite completed vitamin evaluation."
                )

            if (
                marrow_response in (
                    "Inadequate response",
                    "Inadequate/low reticulocyte response",
                )
                and other_cytopenias == "Yes"
            ):
                referral_reasons.append(
                    "Underproduction anemia with additional cytopenias."
                )

            if referral_reasons:
                for reason in dedupe_lines(referral_reasons):
                    st.markdown(f"- {reason}")

            else:
                st.caption(
                    "No specific referral trigger was identified from "
                    "the entered data. Clinical judgment still applies."
                )


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption(
    "AnemiaDx • Created by Manal Ahmidouch • "
    "GMA Clinic / Medical Education • Educational use only"
)
