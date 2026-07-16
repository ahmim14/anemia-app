import re
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="AnemiaDx",
    page_icon="🩸",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container {max-width: 980px; padding-top: 2rem; padding-bottom: 3rem;}
        [data-testid="stSidebar"] {background: #f8fafc;}
        .anemiadx-hero {
            padding: 0.2rem 0 1rem 0;
            border-bottom: 1px solid rgba(148, 163, 184, 0.35);
            margin-bottom: 0.8rem;
        }
        .anemiadx-eyebrow {
            font-size: 0.72rem; font-weight: 800; letter-spacing: 0.12em;
            color: #b91c1c; margin: 0 0 0.25rem 0;
        }
        .anemiadx-title {font-size: 2.35rem; font-weight: 800; letter-spacing: -0.04em; margin: 0; line-height: 1.05;}
        .anemiadx-subtitle {font-size: 1rem; color: #64748b; margin: 0.45rem 0 0 0; max-width: 48rem;}
        .anemiadx-version {font-size: 0.72rem; color: #94a3b8; margin-top: 0.45rem;}
        .next-card {
            padding: 1rem 1.05rem;
            border-radius: 14px;
            border: 1px solid #991b1b;
            background: linear-gradient(135deg, #7f1d1d, #450a0a);
            box-shadow: 0 8px 24px rgba(127, 29, 29, 0.18);
            margin: 0.45rem 0 1rem 0;
        }
        .next-card-label {font-size: 0.7rem; font-weight: 800; letter-spacing: 0.11em; color: #fecaca;}
        .next-card-value {font-size: 1.02rem; font-weight: 750; color: #ffffff; margin-top: 0.3rem; line-height: 1.35;}
        div[data-testid="stExpander"] {border-radius: 14px;}
        div[data-testid="stMetric"] {border: 1px solid rgba(49,51,63,.10); padding: .75rem; border-radius: 12px;}
    </style>
    <div class="anemiadx-hero">
        <p class="anemiadx-eyebrow">CLINICAL REASONING TOOL</p>
        <p class="anemiadx-title">AnemiaDx</p>
        <p class="anemiadx-subtitle">A stepwise approach to anemia evaluation, differential diagnosis, and resident education.</p>
        <p class="anemiadx-version">Enhanced build · July 2026</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Educational decision support only — not a substitute for clinical judgment.")

reset_col, _ = st.columns([1, 4])
with reset_col:
    if st.button("↻ Start new evaluation", use_container_width=True):
        st.session_state.clear()
        st.rerun()

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


def add_item(lst, title, rationale="", workup=None, rule="", what_changes="", priority=50, evidence=None, confidence="Possible"):
    lst.append(
        {
            "title": title,
            "rationale": rationale,
            "workup": workup or [],
            "rule": rule,
            "what_changes": what_changes,
            "priority": priority,
            "evidence": evidence or [],
            "confidence": confidence,
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
def known_choice(value):
    """True only when a categorical result was actually provided."""
    return value not in (None, "Unknown")


def build_known(inputs: dict):
    known = {
        "tsh": inputs["tsh"] is not None,
        "egfr": inputs["egfr"] is not None,
        "ferritin": inputs["ferritin"] is not None,
        "tsat": inputs["tsat"] is not None,
        "b12": inputs["b12"] is not None,
        "folate": inputs["folate"] is not None,
        "ldh": known_choice(inputs["ldh"]),
        "haptoglobin": known_choice(inputs["haptoglobin"]),
        "indirect_bili": known_choice(inputs["indirect_bili"]),
        "retic_pct": inputs["retic_pct"] is not None,
        "retic_qual": known_choice(inputs["retic_qual"]),
        "rpi": inputs["rpi"] is not None,
        "smear": known_choice(inputs.get("smear_abnormal")),
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

    # --- Peripheral smear ---
    if re.search(r"\bperipheral smear\b|\bsmear review\b|\breview smear\b", s, flags=re.I):
        if known.get("smear", False):
            return []
        return ["Peripheral smear review"]

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
        return "Low", "#dc2626"  # red
    if n_have <= 3:
        return "Medium", "#f59e0b"  # amber
    return "High", "#16a34a"  # green


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


def confidence_style(level):
    return {
        "Strongly supported": ("#166534", "#dcfce7"),
        "Supported": ("#1d4ed8", "#dbeafe"),
        "Possible": ("#92400e", "#fef3c7"),
        "Insufficient data": ("#475569", "#e2e8f0"),
    }.get(level, ("#475569", "#e2e8f0"))


def evidence_chip(text):
    safe = str(text).replace("<", "&lt;").replace(">", "&gt;")
    return f'<span style="display:inline-block;padding:3px 8px;margin:2px 4px 2px 0;border-radius:999px;background:#f1f5f9;border:1px solid #cbd5e1;font-size:.78rem;">{safe}</span>'


def iron_pattern(ferritin, tsat):
    if ferritin is None and tsat is None:
        return None, "Insufficient data"
    if ferritin is not None and ferritin < 30:
        return "Absolute iron deficiency pattern", "Strongly supported"
    if ferritin is not None and ferritin >= 100 and tsat is not None and tsat < 20:
        return "Functional iron deficiency / inflammation pattern", "Supported"
    if ferritin is not None and 30 <= ferritin < 100 and tsat is not None and tsat < 20:
        return "Possible iron deficiency; ferritin may be equivocal", "Possible"
    if ferritin is not None and ferritin >= 100 and tsat is not None and tsat >= 20:
        return "Iron deficiency is less supported by current studies", "Possible"
    if tsat is not None and tsat < 20:
        return "Low iron availability; ferritin is needed to distinguish absolute from functional deficiency", "Possible"
    return "No clear iron-deficiency pattern from entered values", "Possible"


def mixed_pattern_flags(mcv_cat, rdw, ferritin, b12, folate, recent_transfusion):
    flags = []
    if mcv_cat == "Normocytic (80–100)" and ferritin is not None and ferritin < 30:
        flags.append("Normal MCV does not exclude early or mixed iron deficiency.")
    if mcv_cat == "Microcytic (<80)" and ((b12 is not None and b12 < 200) or (folate is not None and folate < 4)):
        flags.append("A vitamin deficiency is present despite microcytosis, suggesting a mixed process.")
    if mcv_cat == "Normocytic (80–100)" and rdw == "High":
        flags.append("High RDW with a normal MCV can reflect competing microcytic and macrocytic processes.")
    if recent_transfusion:
        flags.append("Recent transfusion can obscure the native MCV and RDW pattern.")
    return flags


def lab_rows(hb, ferritin, tsat, b12, folate, tsh, egfr, ldh, haptoglobin, indirect_bili, rpi):
    rows = []
    def add(test, value, interpretation, level):
        if value is not None:
            rows.append({"Test": test, "Result": value, "Interpretation": interpretation, "Flag": level})
    if hb is not None:
        add("Hemoglobin", f"{hb:.1f} g/dL", "Low if below sex-specific threshold", "Abnormal")
    if ferritin is not None:
        add("Ferritin", f"{ferritin:.0f} ng/mL", "Low" if ferritin < 30 else ("Borderline" if ferritin < 100 else "Not low"), "Abnormal" if ferritin < 30 else ("Borderline" if ferritin < 100 else "Normal"))
    if tsat is not None:
        add("TSAT", f"{tsat:.0f}%", "Low iron availability" if tsat < 20 else "Not low", "Abnormal" if tsat < 20 else "Normal")
    if b12 is not None:
        add("Vitamin B12", f"{b12:.0f} pg/mL", "Low" if b12 < 200 else ("Borderline" if b12 < 300 else "Not low"), "Abnormal" if b12 < 200 else ("Borderline" if b12 < 300 else "Normal"))
    if folate is not None:
        add("Folate", f"{folate:.1f} ng/mL", "Low" if folate < 4 else "Not low", "Abnormal" if folate < 4 else "Normal")
    if tsh is not None:
        add("TSH", f"{tsh:.2f} μIU/mL", "Elevated" if tsh > 5 else "Not elevated", "Abnormal" if tsh > 5 else "Normal")
    if egfr is not None:
        add("eGFR", f"{egfr:.0f} mL/min/1.73m²", "Reduced" if egfr < 60 else "Preserved", "Abnormal" if egfr < 60 else "Normal")
    if ldh not in (None, "Unknown"):
        add("LDH", ldh, "Hemolysis-supportive" if ldh == "High" else "Not elevated", "Abnormal" if ldh == "High" else "Normal")
    if haptoglobin not in (None, "Unknown"):
        add("Haptoglobin", haptoglobin, "Hemolysis-supportive" if haptoglobin == "Low" else "Not low", "Abnormal" if haptoglobin == "Low" else "Normal")
    if indirect_bili not in (None, "Unknown"):
        add("Indirect bilirubin", indirect_bili, "Hemolysis-supportive" if indirect_bili == "High" else "Not elevated", "Abnormal" if indirect_bili == "High" else "Normal")
    if rpi is not None:
        add("RPI", f"{rpi:.2f}", "Appropriate marrow response" if rpi >= 2 else "Inadequate marrow response", "Normal" if rpi >= 2 else "Abnormal")
    return rows


def clinical_impression(mcv_cat, marrow_response, dx_unique, mixed_flags):
    morphology = {
        "Microcytic (<80)": "Microcytic",
        "Normocytic (80–100)": "Normocytic",
        "Macrocytic (>100)": "Macrocytic",
    }.get(mcv_cat, "Anemia")
    marrow = ""
    if "Inadequate" in marrow_response:
        marrow = " hypoproliferative"
    elif "Appropriate" in marrow_response:
        marrow = " with an appropriate marrow response"
    if dx_unique:
        top_titles = [x["title"] for x in dx_unique[:2]]
        lead = top_titles[0]
        if len(top_titles) > 1:
            lead += f", with {top_titles[1].lower()} also contributing"
        sentence = f"{morphology}{marrow} anemia; {lead.lower()} is the leading interpretation."
    else:
        sentence = f"{morphology}{marrow} anemia with insufficient data to identify a leading etiology."
    if mixed_flags:
        sentence += " A mixed process may be present."
    return sentence


def generate_plan(impression, dx_unique, tests, actions):
    etiologies = ", ".join(item["title"] for item in dx_unique[:3]) if dx_unique else "etiology remains incompletely characterized"
    plan_parts = []
    if tests:
        plan_parts.append("Obtain " + ", ".join(tests) + ".")
    if actions:
        plan_parts.append("Actions: " + "; ".join(actions) + ".")
    if not plan_parts:
        plan_parts.append("Correlate with the clinical context and trend the CBC as appropriate.")
    return (
        f"Assessment: {impression}\n\n"
        f"Leading considerations: {etiologies}.\n\n"
        f"Plan: {' '.join(plan_parts)}"
    )


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
        if marrow_response in ("Appropriate (RPI ≥2)", "Appropriate/High retic"):
            missing = []
            if not known["hemo_any"]:
                missing.append("Hemolysis markers (LDH, haptoglobin, indirect bilirubin)")
            if not known.get("smear", False):
                missing.append("Peripheral smear review")
            if missing:
                return missing
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
    def node(label, active=False, complete=False):
        attrs = ['shape="box"', 'style="rounded,filled"']
        if active:
            attrs += ['fillcolor="#fee2e2"', 'color="#b91c1c"', 'penwidth="2.2"']
        elif complete:
            attrs += ['fillcolor="#ecfdf5"', 'color="#15803d"']
        else:
            attrs += ['fillcolor="#f8fafc"', 'color="#cbd5e1"', 'fontcolor="#64748b"']
        safe = str(label).replace('"', "'").replace("\n", "\\n")
        return f'[{", ".join(attrs)}, label="{safe}"];'

    dot = [
        "digraph G {",
        "rankdir=TB;",
        "splines=ortho;",
        "nodesep=0.25;",
        "ranksep=0.35;",
        'node [fontname="Helvetica"];',
        'edge [color="#94a3b8"];',
    ]
    dot.append(f'Start {node("Start", complete=True)}')
    mcv_label = mcv_cat if mcv_cat else "Select MCV"
    dot.append(f'MCV {node(mcv_label, active=mcv_cat is None, complete=mcv_cat is not None)}')
    dot.append("Start -> MCV;")

    if mcv_cat == "Microcytic (<80)":
        dot.append(f'Path {node("Microcytic pathway", complete=True)}')
        label = "Iron studies complete" if known["iron_any"] else "Next: ferritin + TSAT"
        dot.append(f'Current {node(label, active=not known["iron_any"], complete=known["iron_any"])}')
        dot.append("MCV -> Path -> Current;")
    elif mcv_cat == "Normocytic (80–100)":
        dot.append(f'Path {node("Normocytic pathway", complete=True)}')
        if not known["retic_any"]:
            label, done = "Next: reticulocyte count / RPI", False
        elif marrow_response in ("Appropriate (RPI ≥2)", "Appropriate/High retic") and not known["hemo_any"]:
            label, done = "Next: hemolysis markers", False
        else:
            label, done = "Core pathway complete", True
        dot.append(f'Current {node(label, active=not done, complete=done)}')
        dot.append("MCV -> Path -> Current;")
    elif mcv_cat == "Macrocytic (>100)":
        dot.append(f'Path {node("Macrocytic pathway", complete=True)}')
        if not (known["b12"] and known["folate"]):
            label, done = "Next: B12 + folate", False
        elif not known["tsh"]:
            label, done = "Next: TSH", False
        else:
            label, done = "Core pathway complete", True
        dot.append(f'Current {node(label, active=not done, complete=done)}')
        dot.append("MCV -> Path -> Current;")
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
    active_bleeding = selected(st.selectbox("Concern for active/ongoing bleeding?", ["Select...", "Yes", "No", "Unknown"], index=0))
    cvd = selected(st.selectbox("Significant cardiovascular disease (CAD/HF) present?", ["Select...", "Yes", "No", "Unknown"], index=0))

st.header("CBC basics")
colA, colB = st.columns(2)
with colA:
    hb = to_float(st.text_input("Hemoglobin (g/dL)", value="", placeholder="leave blank if unknown"))
    hct = to_float(st.text_input("Hematocrit (%)", value="", placeholder="leave blank if unknown"))
with colB:
    sex = selected(st.selectbox("Sex", ["Select...", "Female", "Male"], index=0))
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
        other_cytopenias = selected(st.selectbox("Other cytopenias (WBC or platelets low)?", ["Select...", "Yes", "No", "Unknown"], index=0))
    with colC2:
        rapid_onset = selected(st.selectbox("Rapid onset / acute Hb drop suspected?", ["Select...", "Yes", "No", "Unknown"], index=0))
    with colC3:
        smear_abnormal = selected(st.selectbox("Peripheral smear abnormal (if known)?", ["Select...", "Yes", "No", "Unknown"], index=0))

# Retic/RPI
retic_qual = None
retic_pct = None
rpi = None
mf = None
corrected_retic = None

st.subheader("Reticulocytes")
expand_retic = (mcv_cat == "Normocytic (80–100)")
with st.expander("Reticulocyte count / RPI ", expanded=expand_retic):
    retic_mode = st.radio("Reticulocyte input", ["Qualitative (Low/Normal/High)", "Numeric (%)"], horizontal=True, index=0)

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
    "smear_abnormal": smear_abnormal,
}
known = build_known(inputs)

# Teaching sidebar decision tree
if teaching_mode:
    with st.sidebar:
        st.subheader("🧠 Live reasoning map")
        next_items = next_most_informative(mcv_cat, marrow_response, known)
        next_text = "<br>".join(titlecase_first(x.replace("Action:", "").strip()) for x in next_items)
        st.markdown(
            f"""
            <div class="next-card">
                <div class="next-card-label">NEXT MOST INFORMATIVE</div>
                <div class="next-card-value">{next_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(f"Current path: {breadcrumb_path(mcv_cat, marrow_response, known, inputs)}")
        st.graphviz_chart(decision_tree_dot(mcv_cat, marrow_response, known), use_container_width=True)
        st.caption("The map updates as data are entered. The recommendation card is intentionally separate from the flow map.")


# ============================================================
# OUTPUTS
# ============================================================
st.markdown("---")
st.header("Clinical summary")

if mcv_cat is None:
    st.info("Select an MCV category above to generate the POC summary and differential.")
else:
    st.markdown(f"**MCV category:** {mcv_cat}  \n**Marrow response:** {marrow_response}")

    # -------------------------
    # Guardrail: NO ANEMIA (sex-specific Hb cutoffs)
    # Only applies if sex is selected.
    # -------------------------
    no_anemia = False
    if hb is not None and sex is not None:
        if sex == "Female" and hb >= 12:
            no_anemia = True
        elif sex == "Male" and hb >= 13:
            no_anemia = True

    if no_anemia:
        st.success("No anemia detected based on entered hemoglobin.")
        st.caption("If symptoms persist, consider non-anemia etiologies or repeat CBC if clinically indicated.")
        st.stop()

    # Differential build
    dx = []

    # -------------------------
    # MCV-SPECIFIC DIFFERENTIALS
    # -------------------------
    if mcv_cat == "Microcytic (<80)":
        # IDA is GLOBAL (below). Microcytic branch focuses on other patterns when not iron deficient.
        if ferritin is not None and ferritin >= 100 and transferrin_sat is not None and transferrin_sat < 20:
            add_item(
                dx,
                "Anemia of chronic inflammation with functional iron deficiency",
                "Ferritin may be normal/high with low TSAT in inflammatory states.",
                [
                    "Action: review chronic inflammatory/infectious disease history",
                    "CRP/ESR (if inflammatory disease suspected)",
                ],
                priority=20,
                evidence=[f"Ferritin {fmt(ferritin,0)}", f"TSAT {fmt(transferrin_sat,0,'%')}", "Microcytosis"],
                confidence="Supported",
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
                evidence=["Microcytosis", "Iron deficiency not clearly established"],
                confidence="Possible",
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
    # -------------------------
    # Iron deficiency: triggers even if MCV is normocytic (early IDA / mixed anemia)
    if ferritin is not None and ferritin < 30:
        add_item(
            dx,
            "Iron deficiency anemia",
            "Low ferritin supports depleted iron stores; can be normocytic early or with mixed etiologies.",
            [
                "Action: assess source of blood loss (GI/menstrual)",
                "Action: consider GI evaluation when appropriate (age/risk-based)",
                "Action: consider celiac testing if indicated",
            ],
            priority=9,
            evidence=[f"Ferritin {fmt(ferritin,0)} ng/mL", f"MCV: {mcv_cat.split()[0]}"] + ([f"TSAT {fmt(transferrin_sat,0,'%')}"] if transferrin_sat is not None else []),
            confidence="Strongly supported",
        )

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
            evidence=[f"B12 {fmt(b12,0)} pg/mL"],
            confidence="Strongly supported",
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
            evidence=[f"Folate {fmt(folate,1)} ng/mL"],
            confidence="Strongly supported",
        )

    # -------------------------
    # SMEAR FINDINGS
    # -------------------------
    if smear_abnormal == "Yes":
        add_item(
            dx,
            "Abnormal peripheral smear requiring morphology-directed evaluation",
            "An abnormal smear has already been documented, so the next step is to act on the specific morphology rather than repeat a generic smear recommendation.",
            [
                "Action: identify the reported morphology (e.g., schistocytes, blasts, spherocytes, dysplasia)",
                "Action: correlate the morphology with CBC, reticulocyte response, and hemolysis markers",
                "Action: consider urgent hematology input for blasts, schistocytes, or other high-risk findings",
            ],
            priority=6,
        )

    # -------------------------
    # OTHER EXISTING RULES
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
            evidence=["High LDH", "Low haptoglobin", "High indirect bilirubin"],
            confidence="Strongly supported",
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

    iron_interp, iron_confidence = iron_pattern(ferritin, transferrin_sat)
    mixed_flags = mixed_pattern_flags(
        mcv_cat, rdw, ferritin, b12, folate, "Recent transfusion (last 3 months)" in exposures
    )
    impression = clinical_impression(mcv_cat, marrow_response, dx_unique, mixed_flags)

    st.markdown("#### Clinical impression")
    st.info(impression)

    if mixed_flags:
        st.markdown("#### Mixed-pattern alert")
        for flag in mixed_flags:
            st.warning(flag)

    if iron_interp:
        fg, bg = confidence_style(iron_confidence)
        st.markdown(
            f'<div style="padding:.8rem 1rem;border-radius:12px;background:{bg};color:{fg};border:1px solid {fg}22;">'
            f'<strong>Iron-study interpretation:</strong> {iron_interp}</div>',
            unsafe_allow_html=True,
        )

    rows = lab_rows(hb, ferritin, transferrin_sat, b12, folate, tsh, egfr, ldh, haptoglobin, indirect_bili, rpi)
    if rows:
        st.markdown("#### Entered data at a glance")
        lab_df = pd.DataFrame(rows)
        def highlight_flag(row):
            palette = {
                "Abnormal": "background-color: #fee2e2; color: #991b1b",
                "Borderline": "background-color: #fef3c7; color: #92400e",
                "Normal": "background-color: #dcfce7; color: #166534",
            }
            style = palette.get(row["Flag"], "background-color: #f1f5f9; color: #475569")
            return [style] * len(row)
        st.dataframe(
            lab_df.style.apply(highlight_flag, axis=1),
            use_container_width=True,
            hide_index=True,
        )

    # ---- Data completeness ----
    st.markdown("#### Data completeness")
    level_txt, level_color = completeness_badge(known)
    st.markdown(pill(level_txt, level_color), unsafe_allow_html=True)
    st.caption("Completeness reflects whether key lab groups were entered")

    # ---- Next steps (POC) ----
    st.markdown("#### Recommended next steps")
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
        for i, item in enumerate(dx_unique[:3], 1):
            fg, bg = confidence_style(item.get("confidence", "Possible"))
            st.markdown(
                f'<div style="padding:.85rem 1rem;margin:.45rem 0;border-radius:14px;border:1px solid #e2e8f0;">'
                f'<div style="display:flex;justify-content:space-between;gap:1rem;align-items:center;">'
                f'<strong>{i}. {item["title"]}</strong>'
                f'<span style="padding:3px 8px;border-radius:999px;background:{bg};color:{fg};font-size:.76rem;font-weight:700;">{item.get("confidence", "Possible")}</span>'
                f'</div>'
                f'<div style="margin-top:.45rem;">{"".join(evidence_chip(x) for x in item.get("evidence", []))}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("#### Copyable assessment & plan")
    assessment_plan = generate_plan(impression, dx_unique, tests, actions)
    st.code(assessment_plan, language=None)
    st.caption("Use the copy icon in the code box, then edit for the individual patient and local practice.")

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
                fg, bg = confidence_style(item.get("confidence", "Possible"))
                st.markdown(
                    f'<span style="padding:3px 8px;border-radius:999px;background:{bg};color:{fg};font-size:.8rem;font-weight:700;">{item.get("confidence", "Possible")}</span>',
                    unsafe_allow_html=True,
                )
                if item.get("evidence"):
                    st.markdown("**Evidence used:**")
                    st.markdown(" ".join(evidence_chip(x) for x in item.get("evidence", [])), unsafe_allow_html=True)
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
st.caption("AnemiaDx • Created by Manal Ahmidouch • GMA Clinic / Medical Education • Educational use only")
