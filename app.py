import streamlit as st
from backend.roadmap_logic import generate_ai_roadmap

st.title("AI-Powered Roadmap Generator")
st.write("Get a personalized learning roadmap tailored to your interests and goals.")

# Step 1: Collect user preferences
st.header("Tell us about yourself")
interests = st.multiselect(
    "What are your areas of interest?",
    ["AI in Education", "Web Development", "Data Science", "Game Design"]
)
available_time = st.slider("How many hours can you dedicate to learning each week?", 1, 20, 5)
goals = st.text_input("Describe your career goals:", placeholder="E.g., Become a data scientist")

# Generate roadmap
if st.button("Generate My Roadmap"):
    if interests and available_time > 0 and goals:
        roadmap = generate_ai_roadmap(interests, available_time, goals)
        st.header("Your Personalized Roadmap")
        st.write(roadmap)
    else:
        st.error("Please provide all the required information.")
