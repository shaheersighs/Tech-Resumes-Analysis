# Tech Resumes Analysis System

An AI-powered Resume Screening Tool designed to analyze, extract, and rank IT resumes based on a given job description. This intelligent web application leverages state-of-the-art Natural Language Processing (NLP) techniques to assist recruiters in shortlisting the most relevant candidates efficiently. Deployed live at https://techresumeanalyzer.netlify.app/

---

## Key Features

- **AI-Driven Resume Ranking** — Ranks resumes based on skill match, work experience, and education alignment.
- **Resume Upload** — Supports PDF resume uploads.
- **Job Description Input** — Accepts job description text for context-aware ranking.
- **NLP-Powered Extraction** — Uses `spaCy`, `TF-IDF`, and BERT-based models for extracting:
  - Technical skills
  - Years of experience
  - Academic qualifications
- **Ranked Output Display** — Clean, sortable table displaying scores and matches.
- **Real-Time Results** — Instant feedback from backend processing.

---

## Tech Stack

| Category     | Technologies Used                              |
|--------------|------------------------------------------------|
| Frontend     | React.js, HTML5, CSS3                          |
| Backend      | Flask (Python)                                 |
| NLP / ML     | spaCy, scikit-learn (TF-IDF), SentenceTransformers (BERT) |
| File Parsing | PyMuPDF (for PDF parsing)                      |
| Deployment   | Netlify (Frontend), Render/AWS/Railway (API)   |

---
## Usage Instructions

1. Paste the **job description** in the input field.
2. Upload one or more **PDF resumes**.
3. Click **Analyze** to view ranked results.
4. Review rankings in the generated table.

---

## Core Functionality

### Skill Matching
- Extracts keywords using **TF-IDF**
- Filters using **spaCy Named Entity Recognition (NER)**

### Experience Detection
- Extracts **dates** and **job titles**
- Calculates **years of experience** using heuristic matching

### Education Parsing
- Identifies **degrees** and **institutions** using regex and keyword patterns

### Semantic Scoring
- Uses **SentenceTransformer** to compare job/resume embeddings
- Final score = **weighted average** of all metrics

---

## Sample Output

| Candidate Name | Skills Match | Experience (Years) | Education Match | Total Score |
|----------------|--------------|--------------------|------------------|-------------|
| John Doe       | 85%          | 4.5                |   Bachelor’s     | 82.3        |
| Jane Smith     | 92%          | 6.0                |   Master’s       | 89.5        |

---

## Roadmap

- [ ] DOCX resume support
- [ ] Drag-and-drop file upload
- [ ] Chart-based ranking visualization
- [ ] Enhanced error handling
- [ ] Dockerized deployment
- [ ] Resume feedback generator

---

## About

This project was developed as part of the **Emerging Trends in Data Technology** course by:

**Shaheer**  
Final Year IT Student | Data Engineer

---

## License

This project is licensed under the **MIT License**.

---

## Acknowledgements

- [spaCy](https://spacy.io/)
- [scikit-learn](https://scikit-learn.org/)
- [SentenceTransformers](https://www.sbert.net/)
- [React](https://reactjs.org/)
- [Flask](https://flask.palletsprojects.com/)
