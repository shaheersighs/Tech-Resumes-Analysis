import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [jobDescription, setJobDescription] = useState("");
  const [rankedResumes, setRankedResumes] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);

  const handleJobDescriptionSubmit = async () => {
    try {
      await axios.post("http://127.0.0.1:5000/upload-job-description", {
        job_description: jobDescription,
      });
    } catch (error) {
      console.error("Error uploading job description:", error);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile || selectedFile.length === 0) {
      return; // silent fail
    }

    const formData = new FormData();
    selectedFile.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/upload-resumes",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      setRankedResumes(response.data);
    } catch (error) {
      console.error("Error uploading resumes:", error);
    }
  };

  return (
    <>
      {/* Main Heading */}
      <div className="main-heading">
        <div className="heading-content">
          <div className="heading-text-block">
            <h1>Tech Resumes Analysis System</h1>
            <div className="tagline">Tailored Ranking and Analysis for IT Resumes</div>
          </div>
          <img src="/logo.jpg" alt="Logo" className="logo" />
        </div>
      </div>

      {/* Job Description Input */}
      <div className="section">
        <div className="input-container">
          <label className="input-label">Enter Job Description</label>

          <div className="job-description-box">
            <textarea
              placeholder="Write or paste your description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            />
          </div>

          <button className="btn primary" onClick={handleJobDescriptionSubmit}>
            Submit Job Description
          </button>
        </div>
      </div>

      {/* File Upload */}
      <div className="section">
        <div className="upload-container">
          <div className="upload-box-wrapper">
            <label className="input-label">Enter Resume Files</label>
            <div className="upload-box" onClick={() => document.getElementById("fileInput").click()}>
              {selectedFile && selectedFile.length > 0
                ? `${selectedFile.length} file(s) selected`
                : "Click to select one or more resume files"}
              <input
                id="fileInput"
                type="file"
                multiple
                style={{ display: "none" }}
                onChange={(e) => setSelectedFile(Array.from(e.target.files))}
              />
            </div>
          </div>
          <button className="btn secondary" onClick={handleFileUpload}>
            Upload Resume
          </button>
        </div>
      </div>

      {/* Display Ranked Resumes in Table Format */}
      <div className="section">
        <div className="results-container">
          <h2>Ranking and Analysis</h2>
          {rankedResumes.length > 0 ? (
            <table className="resume-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Name</th>
                  <th>Similarity Score</th>
                  <th>Skills</th>
                  <th>Experience</th>
                  <th>Education</th>
                </tr>
              </thead>
              <tbody>
                {rankedResumes.map((resume, index) => (
                  <tr key={index}>
                    <td>{index + 1}</td>
                    <td>{resume.name}</td>
                    <td>{resume.score}%</td>
                    <td>{Array.isArray(resume.skills) ? resume.skills.join(", ") : "N/A"}</td>
                    <td>{typeof resume.experience === "number" ? `${resume.experience} years` : "N/A"}</td>
                    <td>{Array.isArray(resume.education) ? resume.education.join(", ") : "N/A"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No resumes ranked yet.</p>
          )}
        </div>
      </div>

      {/* Display links */}
      <footer className="footer">
        <p>Designed and Created by <strong>Shaheer Khan</strong></p>
        <div className="footer-content">
          {/* Circular Logo */}
          <a
            href="https://shaheersighs.netlify.app"
            target="_blank"
            rel="noopener noreferrer"
            className="logo-circle"
          >
            <img
              src="/logo.jpg"
              alt="Logo"
              className="logo-image"
              id="footer-logo"
            />
          </a>
          {/* GitHub Icon */}
          <a href="https://github.com/shaheersighs" target="_blank" rel="noopener noreferrer">
            <img
              src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg"
              alt="GitHub"
              className="icon"
            />
          </a>
          {/* LinkedIn Icon */}
          <a href="https://www.linkedin.com/in/shaheersighs/" target="_blank" rel="noopener noreferrer">
            <img
              src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linkedin/linkedin-original.svg"
              alt="LinkedIn"
              className="icon"
            />
          </a>
        </div>
      </footer>
    </>
  );
}

export default App;










