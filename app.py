"""Streamlit interface for RoadmapGeneratorAI.

Run with:  streamlit run app.py
"""

import streamlit as st

from roadmap import MaterialStore, RoadmapGenerator

st.set_page_config(page_title="RoadmapGeneratorAI", page_icon="🗺️", layout="centered")


@st.cache_resource
def get_store() -> MaterialStore:
    return MaterialStore("data/chroma")


@st.cache_resource
def get_generator() -> RoadmapGenerator:
    return RoadmapGenerator(get_store())


store = get_store()

# ---- sidebar: course materials --------------------------------------------
with st.sidebar:
    st.header("1. Course materials")
    files = st.file_uploader("Upload syllabi, lecture notes or readings", type=["pdf", "txt"], accept_multiple_files=True)
    if files and st.button("Add to my library"):
        with st.spinner("Reading and indexing…"):
            n = store.add_uploads(files)
        st.success(f"Added {n} passages from {len(files)} file(s).")
    if st.button("Load sample materials"):
        with st.spinner("Loading samples…"):
            n = store.add_folder("sample_materials")
        st.success(f"Added {n} passages from the sample course.")

    sources = store.sources()
    st.caption(f"Library: {store.count()} passages from {len(sources)} file(s)")
    for s in sources:
        st.caption(f"• {s}")
    if sources and st.button("Clear library"):
        store.clear()
        st.rerun()

# ---- main: learner profile -------------------------------------------------
st.title("RoadmapGeneratorAI")
st.write(
    "Get a week-by-week study plan built from **your own course materials**. "
    "Every week shows which file it is based on, so you can check the source."
)

st.header("2. About you")
goal = st.text_input("What do you want to achieve?", placeholder="e.g. build my first data analysis project")
interests = st.multiselect(
    "Which topics interest you?",
    ["Programming", "Data analysis", "Machine learning", "Web development", "Instructional design", "Research methods"],
)
col1, col2 = st.columns(2)
hours = col1.slider("Hours per week", 1, 20, 5)
weeks = col2.slider("Number of weeks", 2, 8, 5)

if st.button("Generate my roadmap", type="primary"):
    if store.count() == 0:
        st.error("Add some course materials first (or load the sample materials).")
    elif not goal or not interests:
        st.error("Please describe your goal and choose at least one topic.")
    else:
        with st.spinner("Finding relevant material and writing your plan (the first run downloads the model)…"):
            roadmap = get_generator().generate(interests, goal, hours, weeks)
        if not roadmap.weeks:
            st.warning("No matching material found. Try other topics or add more files.")
        else:
            if len(roadmap.weeks) < weeks:
                st.info(
                    f"Your materials only had {len(roadmap.weeks)} sections that clearly match this goal, "
                    "so the plan is shorter. Add more materials for a longer plan."
                )
            st.markdown(roadmap.to_markdown())
            st.download_button("Download as Markdown", roadmap.to_markdown(), file_name="my_roadmap.md")
