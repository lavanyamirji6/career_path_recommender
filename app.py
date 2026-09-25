from flask import Flask, render_template, send_from_directory, request, jsonify
from pathlib import Path
import json
import datetime

app = Flask(__name__, static_folder='.', template_folder='.')

# ---------------------------------------------------------
# 1. Career dataset (25 careers – you can edit/extend)
# Each career has:
# - title, description, skills (keywords), interests (keywords)
# - demand ("High"/"Medium"/"Emerging")
# - salary_level, demand_level, trend_level (1–5) for graph
# - roadmap: list of steps
# ---------------------------------------------------------

CAREERS = [
    {
        "title": "Software Developer",
        "description": "Builds and maintains applications, websites, and software systems.",
        "skills": ["python", "java", "c++", "problem solving", "algorithms"],
        "interests": ["technology", "coding", "apps"],
        "demand": "High",
        "salary_level": 5,
        "demand_level": 5,
        "trend_level": 5,
        "roadmap": [
            "Learn programming fundamentals and data structures.",
            "Build small projects (web app, CLI tools, games).",
            "Contribute to open source or team projects.",
            "Prepare a portfolio and apply for internships or junior roles."
        ]
    },
    {
        "title": "Data Analyst",
        "description": "Analyzes data to find patterns and support business decisions.",
        "skills": ["python", "sql", "excel", "statistics"],
        "interests": ["data", "numbers", "business"],
        "demand": "High",
        "salary_level": 4,
        "demand_level": 5,
        "trend_level": 5,
        "roadmap": [
            "Learn Excel, SQL, and basic statistics.",
            "Practice with public datasets and dashboards.",
            "Learn Python libraries like pandas and matplotlib.",
            "Build a portfolio of analysis projects and apply for analyst roles."
        ]
    },
    {
        "title": "UI/UX Designer",
        "description": "Designs user interfaces and experiences for apps and websites.",
        "skills": ["figma", "ui", "ux", "design", "wireframes"],
        "interests": ["design", "creativity", "users"],
        "demand": "High",
        "salary_level": 4,
        "demand_level": 4,
        "trend_level": 5,
        "roadmap": [
            "Learn design basics: typography, color, layout.",
            "Practice with Figma or similar tools.",
            "Create case studies for 3–4 sample apps/websites.",
            "Apply for internships or junior designer roles."
        ]
    },
    {
        "title": "Digital Marketer",
        "description": "Creates and manages online marketing campaigns and content.",
        "skills": ["seo", "social media", "content", "analytics"],
        "interests": ["marketing", "communication", "business"],
        "demand": "High",
        "salary_level": 3,
        "demand_level": 4,
        "trend_level": 4,
        "roadmap": [
            "Learn basics of SEO, social media, and content marketing.",
            "Run small campaigns for a personal project or local business.",
            "Learn to use analytics tools and measure results.",
            "Create a portfolio and apply for marketing roles."
        ]
    },
    {
        "title": "Cloud Engineer",
        "description": "Designs and maintains cloud infrastructure on platforms like AWS or Azure.",
        "skills": ["linux", "networking", "aws", "azure", "devops"],
        "interests": ["infrastructure", "cloud", "scalability"],
        "demand": "High",
        "salary_level": 5,
        "demand_level": 5,
        "trend_level": 5,
        "roadmap": [
            "Learn networking, Linux, and basic scripting.",
            "Study one cloud provider (AWS/Azure/GCP) and get a certificate.",
            "Practice deploying sample apps and automating infrastructure.",
            "Apply for cloud/DevOps engineer roles."
        ]
    },
    {
        "title": "Cybersecurity Analyst",
        "description": "Protects systems and data from attacks and vulnerabilities.",
        "skills": ["networking", "linux", "security", "monitoring"],
        "interests": ["security", "systems", "investigation"],
        "demand": "High",
        "salary_level": 4,
        "demand_level": 5,
        "trend_level": 5,
        "roadmap": [
            "Learn networking and operating system fundamentals.",
            "Study security basics and common attack types.",
            "Practice with labs and capture-the-flag platforms.",
            "Aim for security certifications and entry roles."
        ]
    },
    {
        "title": "Machine Learning Engineer",
        "description": "Builds and deploys models that learn from data.",
        "skills": ["python", "ml", "statistics", "linear algebra"],
        "interests": ["ai", "math", "data"],
        "demand": "High",
        "salary_level": 5,
        "demand_level": 4,
        "trend_level": 5,
        "roadmap": [
            "Strengthen math: statistics and linear algebra.",
            "Learn Python ML libraries (scikit-learn, pandas).",
            "Build small ML projects (classification, regression).",
            "Move to deep learning and deployment; apply to ML roles."
        ]
    },
    {
        "title": "Frontend Web Developer",
        "description": "Builds the visual and interactive parts of websites.",
        "skills": ["html", "css", "javascript", "react"],
        "interests": ["web", "design", "interaction"],
        "demand": "High",
        "salary_level": 4,
        "demand_level": 4,
        "trend_level": 5,
        "roadmap": [
            "Master HTML, CSS, and responsive design.",
            "Learn JavaScript fundamentals and the DOM.",
            "Pick a framework like React and build projects.",
            "Create a portfolio website and apply for frontend roles."
        ]
    },
    {
        "title": "Backend Web Developer",
        "description": "Builds APIs and server-side logic for applications.",
        "skills": ["python", "django", "flask", "databases"],
        "interests": ["servers", "logic", "apis"],
        "demand": "High",
        "salary_level": 4,
        "demand_level": 4,
        "trend_level": 4,
        "roadmap": [
            "Learn one backend language (Python/Node/Java).",
            "Understand databases and ORMs.",
            "Build REST APIs for simple apps.",
            "Deploy apps and apply for backend roles."
        ]
    },
    {
        "title": "Mobile App Developer",
        "description": "Creates mobile applications for Android or iOS.",
        "skills": ["android", "kotlin", "swift", "flutter"],
        "interests": ["mobile", "apps", "ui"],
        "demand": "High",
        "salary_level": 4,
        "demand_level": 4,
        "trend_level": 4,
        "roadmap": [
            "Pick Android (Kotlin) or cross-platform (Flutter).",
            "Build small apps like to-do lists or note apps.",
            "Publish at least one app or demo.",
            "Apply for junior mobile developer roles."
        ]
    },
    # you can add more careers here up to 25
]

# ---------------------------------------------------------
# 2. Simple text matching score
# ---------------------------------------------------------

def score_career(career, skills_text, interests_text, experience_text):
    text = (skills_text + " " + interests_text + " " + experience_text).lower()
    score = 0

    for kw in career["skills"]:
        if kw in text:
            score += 2
    for kw in career["interests"]:
        if kw in text:
            score += 1

    # light bonus for exact title words
    title_words = career["title"].lower().split()
    for w in title_words:
        if w in text:
            score += 1

    return score

# ---------------------------------------------------------
# 3. Routes
# ---------------------------------------------------------

@app.route("/")
def index():
    # index.html is in the same folder
    return render_template("index.html")

@app.route("/style.css")
def style():
    return send_from_directory(".", "style.css")

@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.get_json(force=True)
    skills = data.get("skills", "")
    interests = data.get("interests", "")
    experience = data.get("experience", "")

    # score all careers
    scored = []
    for c in CAREERS:
        s = score_career(c, skills, interests, experience)
        if s > 0:
            scored.append((s, c))

    # if nothing matched, just return a few general careers
    if not scored:
        top = CAREERS[:3]
    else:
        scored.sort(reverse=True, key=lambda x: x[0])
        top = [c for _, c in scored[:5]]

    # build clean JSON (copy so we don't mutate originals)
    careers_out = []
    for c in top:
        careers_out.append({
            "title": c["title"],
            "description": c["description"],
            "demand": c["demand"],
            "salary_level": c["salary_level"],
            "demand_level": c["demand_level"],
            "trend_level": c["trend_level"],
            "roadmap": c["roadmap"],
        })

    return jsonify({"careers": careers_out})

@app.route("/api/save-results", methods=["POST"])
def save_results():
    data = request.get_json(force=True)
    out_dir = Path("saved_results")
    out_dir.mkdir(exist_ok=True)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = out_dir / f"result_{ts}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return jsonify({"message": "Results saved successfully."})

# ---------------------------------------------------------
# 4. Run
# ---------------------------------------------------------

if __name__ == "__main__":
    # debug=True is helpful during development
    #app.run(debug=True)
    app.run(debug=True, port=5000)

