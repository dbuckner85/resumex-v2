import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="✨ Dreamlit Resume Patch Viewer", layout="wide")
st.title("✨ Dreamlit Resume Patch Viewer")

# Default file paths
PATCH_FILE = Path("patches/resume_patch_suggestions.json")
RESUME_FILE = Path("data/daniel_buckner_resume_structured.json")

# Load JSON safely
def load_json(path):
    if path.exists():
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"⚠️ Could not read {path.name}: {e}")
    return None

# Load default data
patch_data = load_json(PATCH_FILE)
resume_data = load_json(RESUME_FILE)

# File uploader
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
