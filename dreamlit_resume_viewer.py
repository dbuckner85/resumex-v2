import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="✨ Dreamlit Resume Patch Viewer", layout="wide")
st.title("✨ Dreamlit Resume Patch Viewer")

# Default file paths
PATCH_FILE = Path("patches/resume_patch_suggestions.json")
RESUME_FILE = Path("data/daniel_buckner_resume_structured.json")
INTAKE_FILE = Path("intake/intake_v1.json")

# Load JSON safely
def load_json(path):
    if path.exists():
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"⚠️ Could not read {path.name}: {e}")
    return None

def save_json(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"⚠️ Could not save {path.name}: {e}")
        return False

# Load default data
patch_data = load_json(PATCH_FILE)
resume_data = load_json(RESUME_FILE)
intake_data = load_json(INTAKE_FILE) or {}

# Sidebar: Intake Info
st.sidebar.header("📋 Intake Summary")

if intake_data:
    st.sidebar.markdown(f"**Name:** {intake_data.get('user_name', 'N/A')}")
    st.sidebar.markdown(f"**Career Stage:** {intake_data.get('career_stage', 'N/A')}")
    st.sidebar.markdown(f"**Target Roles:** {', '.join(intake_data.get('target_roles', []))}")
    st.sidebar.markdown(f"**Industries (experience):** {', '.join(intake_data.get('industries_experience', []))}")
    st.sidebar.markdown(f"**Open to New Industries:** {intake_data.get('industries_open_to', False)}")
    st.sidebar.markdown(f"**Location Preference:** {intake_data.get('location_preference', 'N/A')}")
    st.sidebar.markdown(f"**Relocation Open:** {intake_data.get('relocation_open', False)}")
    st.sidebar.markdown(f"**Notes:** {intake_data.get('additional_notes', '')}")
else:
    st.sidebar.warning("⚠️ No intake file found.")

# Sidebar: Intake Editor
if st.sidebar.checkbox("✏️ Edit Intake"):
    with st.sidebar.form("intake_form", clear_on_submit=False):
        user_name = st.text_input("Name", intake_data.get("user_name", ""))
        career_stage = st.selectbox("Career Stage", ["Junior", "Mid-level", "Senior", "Executive"],
                                    index=["Junior", "Mid-level", "Senior", "Executive"].index(intake_data.get("career_stage", "Senior")))
        target_roles = st.text_area("Target Roles (comma-separated)",
                                    ", ".join(intake_data.get("target_roles", [])))
        industries_exp = st.text_area("Industries of Experience (comma-separated)",
                                      ", ".join(intake_data.get("industries_experience", [])))
        industries_open = st.checkbox("Open to New Industries",
                                      value=intake_data.get("industries_open_to", False))
        location_pref = st.text_input("Location Preference", intake_data.get("location_preference", ""))
        relocation_open = st.checkbox("Relocation Open",
                                      value=intake_data.get("relocation_open", False))
        notes = st.text_area("Additional Notes", intake_data.get("additional_notes", ""))

        submitted = st.form_submit_button("💾 Save Intake")
        if submitted:
            new_intake = {
                "user_name": user_name,
                "career_stage": career_stage,
                "target_roles": [role.strip() for role in target_roles.split(",") if role.strip()],
                "industries_experience": [ind.strip() for ind in industries_exp.split(",") if ind.strip()],
                "industries_open_to": industries_open,
                "location_preference": location_pref,
                "relocation_open": relocation_open,
                "additional_notes": notes
            }
            if save_json(INTAKE_FILE, new_intake):
                st.sidebar.success("✅ Intake file updated! Please refresh to see changes.")
                intake_data = new_intake

# Sidebar: Patch uploader
st.sidebar.header("📂 Upload a Patch JSON")
uploaded_file = st.sidebar.file_uploader("Upload resume_patch_suggestions.json", type="json")
if uploaded_file is not None:
    try:
        patch_data = json.load(uploaded_file)
        st.sidebar.success("✅ Patch file loaded!")
    except Exception as e:
        st.sidebar.error(f"Could not load uploaded file: {e}")

# Guard: need patch data
if not patch_data:
    st.warning("⚠️ No patch suggestions found. Please add one in `patches/` or upload above.")
    st.stop()

accepted = {}
st.subheader("📌 Suggested Resume Patches")

# "Apply all" toggle
apply_all = st.checkbox("✅ Apply All Suggestions")

# Iterate over patches
for idx, patch in enumerate(patch_data):
    field = patch.get("field", f"Unknown-{idx}")
    original = patch.get("original_value", "N/A")
    suggested = patch.get("suggested_value", "N/A")
    reason = patch.get("reason", "No reason provided")
    confidence = patch.get("confidence_score", 0.0)

    with st.expander(f"📍 {field} — Confidence: {confidence:.2f}"):
        st.markdown(f"**Original:** {original}")
        st.markdown(f"**Suggested:** {suggested}")
        st.markdown(f"**Reason:** {reason}")

        if apply_all:
            decision = "Accept suggestion"
        else:
            decision = st.radio(
                f"Decision for {field}",
                ["Leave unchanged", "Accept suggestion"],
                key=f"decision_{idx}",
                horizontal=True,
            )

        if decision == "Accept suggestion":
            accepted[field] = suggested

# Merge results
st.markdown("---")
st.subheader("✅ Final Resume JSON")

final_resume = resume_data.copy() if resume_data else {}
final_resume.update(accepted)

st.json(final_resume)

# Download button
st.download_button(
    label="📥 Download Final Resume JSON",
    data=json.dumps(final_resume, indent=2),
    file_name="final_resume.json",
    mime="application/json",
)
