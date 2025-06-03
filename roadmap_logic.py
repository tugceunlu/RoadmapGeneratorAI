from transformers import pipeline
from backend.data_processing import fetch_course_materials

def generate_ai_roadmap(interests, available_time, goals):
    """
    Generate a personalized roadmap using course materials and AI.
    """
    # Retrieve relevant course materials
    query = f"{', '.join(interests)} for a {goals}"
    relevant_materials = fetch_course_materials(query)
    materials_context = "\n".join(relevant_materials)
    
    # Load an AI model for text generation
    generator = pipeline("text-generation", model="google/flan-t5-base")
    
    # AI prompt
    prompt = f"""
    You are an expert educational advisor. Create a structured, concise learning roadmap for a student with the following details:

    - Interests: {", ".join(interests)}
    - Available Study Time per Week: {available_time} hours
    - Career Goals: {goals}

    Use ONLY the following course materials for context:
    {materials_context}

    The roadmap must follow this structure:
    Week 1: [Specific activity or milestone]
    Week 2: [Specific activity or milestone]
    Week 3: [Specific activity or milestone]
    Week 4: [Specific activity or milestone]
    Week 5: [Specific activity or milestone]
    """
    
    # Generate roadmap
    response = generator(prompt, max_length=300, num_return_sequences=1, do_sample=False)
    return response[0]["generated_text"]
