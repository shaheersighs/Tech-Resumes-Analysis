from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
import logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from resume_processing import extract_text_from_pdf, extract_resume_info, extract_job_info, rank_resume

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Store Job Description in Memory
job_description = ""

@app.route("/upload-job-description", methods=["POST"])
def upload_job_description():
    global job_description
    data = request.get_json()
    job_description = data.get("job_description", "").strip()

    if not job_description:
        return jsonify({"error": "Job description cannot be empty."}), 400

    logging.debug(f"Received Job Description: {job_description}")
    return jsonify({"message": "Job description updated successfully!"})


@app.route("/upload-resumes", methods=["POST"])
def upload_multiple_resumes():
    global job_description

    if "files" not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "No files received"}), 400

    results = []

    for file in files:
        if file.filename == "":
            continue

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        resume_text = extract_text_from_pdf(filepath)
        resume_info = extract_resume_info(resume_text)
        job_info = extract_job_info(job_description)
        score = rank_resume(resume_info, job_info)

        results.append({
            "name": file.filename,
            "score": score,
            "skills": resume_info.get("skills", []),
            "experience": resume_info.get("experience", 0),
            "education": resume_info.get("education", []),
            "job_titles": resume_info.get("jobs", [])
        })

    # Sort results by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    return jsonify(results)


@app.route("/rank-resumes", methods=["GET"])
def rank_resumes():
    if not os.path.exists(UPLOAD_FOLDER):
        logging.error("No resumes uploaded")
        return jsonify({"error": "No resumes uploaded"}), 400

    # Get the latest uploaded file (single file, not all)
    uploaded_files = sorted(
        [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))],
        key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER, x)),
        reverse=True
    )

    if not uploaded_files:
        return jsonify({"error": "No resumes found"}), 400

    latest_resume = uploaded_files[0]  # Pick the most recently uploaded file
    filepath = os.path.join(UPLOAD_FOLDER, latest_resume)

    # Process only this latest resume
    resume_text = extract_text_from_pdf(filepath)
    resume_info = extract_resume_info(resume_text)
    job_info = extract_job_info(job_description)
    score = rank_resume(resume_info, job_info)

    logging.debug(f"Processed Resume: {latest_resume}, Score: {score}")

    return jsonify({
    "name": latest_resume,
    "score": score,
    "skills": resume_info.get("skills", []),
    "experience": resume_info.get("experience", 0),
    "education": resume_info.get("education", []),
    "job_titles": resume_info.get("jobs", [])  
    })


if __name__ == "__main__":
    app.run(debug=True)





