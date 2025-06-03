## RoadmapGeneratorAI – Personalized Learning Roadmap Generator

## Overview
PathfinderAI is an AI-powered application that helps learners generate personalized learning roadmaps based on their interests, weekly time availability, and career goals. It uses course material embeddings, retrieval-augmented generation, and text generation to output a structured week-by-week learning plan.

## Features
- Upload course materials (`.txt`) and embed them into a vector database using ChromaDB
- Retrieve context-relevant course content based on user queries
- Generate personalized learning roadmaps using HuggingFace’s `google/flan-t5-base` model
- Clean and simple Streamlit web interface
- AI logic is separated from interface for modular design

## Project Structure
```
PathfinderAI/
├── app.py                             # Streamlit UI
├── backend/
│   ├── roadmap_logic.py               # Roadmap generation with transformers
│   └── data_processing.py             # Material embedding & retrieval with ChromaDB
├── data/
│   └── embeddings/                    # Persistent ChromaDB vector store
└── requirements.txt                   # Dependencies
```

## Technologies Used
- Python 3
- Streamlit
- LangChain
- ChromaDB
- HuggingFace Transformers (`google/flan-t5-base`)
- HuggingFace Embeddings (`all-MiniLM-L6-v2`)

## Installation

1. Clone the repository:

```
git clone https://github.com/yourusername/PathfinderAI.git
cd PathfinderAI
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Place your `.txt` course materials in a folder (e.g., `./data/materials/`)

4. Process and store embeddings:

```python
from backend.data_processing import process_course_materials
process_course_materials("./data/materials")
```

5. Run the application:

```
streamlit run app.py
```

## Example Prompt Use

**Input:**
- Interests: Data Science, Web Development
- Time: 8 hours/week
- Goal: Become a data-driven full-stack developer

**Output:**
```
Week 1: Learn HTML, CSS fundamentals; read 'Intro to Web Dev.txt'
Week 2: Start Python basics; study 'Python for Data.txt'
Week 3: Build a CRUD web app; explore 'Flask Guide.txt'
...
```

## Future Improvements
- Support for PDF and DOCX materials
- Auto-upload and process files via UI
- Export generated roadmap to PDF
- Role-based personalization (e.g., students vs professionals)

## License

MIT License

---

Created with ❤️ by Tuğçe Ünlü
