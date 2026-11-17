from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from collections import Counter, defaultdict
import csv, io, os, re

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///skillbridge.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class JobPosting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120), default="Sample Employer")
    district = db.Column(db.String(80), nullable=False)
    sector = db.Column(db.String(80), nullable=False)
    skills = db.Column(db.Text, nullable=False)
    proficiency = db.Column(db.String(30), default="Intermediate")
    openings = db.Column(db.Integer, default=1)
    posted_on = db.Column(db.Date, default=datetime.utcnow)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    sector = db.Column(db.String(80), nullable=False)
    district = db.Column(db.String(80), default="Chennai")
    skills = db.Column(db.Text, nullable=False)
    seats = db.Column(db.Integer, default=30)
    placements = db.Column(db.Integer, default=0)
    trainer_capacity = db.Column(db.Integer, default=1)
    equipment_status = db.Column(db.String(30), default="Adequate")
    qualification = db.Column(db.String(120), default="Certificate")

class EmployerFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employer = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    district = db.Column(db.String(80), nullable=False)
    required_skills = db.Column(db.Text, nullable=False)
    satisfaction = db.Column(db.Integer, default=3)
    comments = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def split_skills(value):
    return {s.strip().lower() for s in re.split(r"[,;\n]", value or "") if s.strip()}

def seed():
    if JobPosting.query.count() == 0:
        jobs = [
            ("Python Developer","Aster Digital","Chennai","IT","Python, SQL, Git, REST APIs","Intermediate",18),
            ("Cloud Support Associate","Northstar Systems","Chengalpattu","IT","Cloud Computing, Linux, Networking, Python","Beginner",14),
            ("Cybersecurity Analyst","SecureGrid","Chennai","IT","Cybersecurity, Linux, Networking, SIEM","Advanced",9),
            ("Data Analyst","InsightWorks","Coimbatore","IT","Python, SQL, Power BI, Statistics","Intermediate",22),
            ("EV Service Technician","Volt Mobility","Tiruvallur","Manufacturing","EV Maintenance, Diagnostics, Electrical Safety","Intermediate",16),
            ("CNC Machine Operator","Precision Works","Hosur","Manufacturing","CNC, CAD, Quality Control, Safety","Beginner",20),
            ("Solar PV Technician","Sunfield Energy","Madurai","Energy","Solar PV, Electrical Wiring, Safety","Beginner",12),
            ("Digital Marketing Executive","MarketSpring","Trichy","Services","SEO, Social Media, Analytics, Content","Intermediate",11),
            ("Full Stack Developer","CodeHarbor","Chennai","IT","JavaScript, React, Python, SQL, Git","Advanced",15),
            ("Industrial IoT Technician","MechNova","Coimbatore","Manufacturing","IoT, Sensors, Python, Networking","Intermediate",8),
        ]
        for title, company, district, sector, skills, level, openings in jobs:
            db.session.add(JobPosting(title=title, company=company, district=district, sector=sector,
                                      skills=skills, proficiency=level, openings=openings))
    if Course.query.count() == 0:
        courses = [
            ("Office Automation","IT","Chennai","MS Office, Typing, Internet",40,12,2,"Adequate"),
            ("Basic Computer Applications","IT","Chengalpattu","Computer Basics, MS Office, Internet",35,10,2,"Adequate"),
            ("Python and Data Analytics","IT","Coimbatore","Python, SQL, Power BI, Statistics",30,21,2,"Adequate"),
            ("Cloud Fundamentals","IT","Chennai","Cloud Computing, Linux, Networking",25,9,1,"Needs upgrade"),
            ("Electrical Technician","Manufacturing","Tiruvallur","Electrical Wiring, Safety, Diagnostics",30,18,2,"Adequate"),
            ("Traditional Machine Operation","Manufacturing","Hosur","Manual Lathe, Safety",35,8,1,"Needs upgrade"),
            ("Solar Installation","Energy","Madurai","Solar PV, Electrical Wiring, Safety",25,17,2,"Adequate"),
            ("Digital Marketing","Services","Trichy","SEO, Social Media, Content",30,19,2,"Adequate"),
        ]
        for name, sector, district, skills, seats, placements, trainers, equipment in courses:
            db.session.add(Course(name=name, sector=sector, district=district, skills=skills, seats=seats,
                                  placements=placements, trainer_capacity=trainers, equipment_status=equipment))
    db.session.commit()

def demand_analysis():
    postings = JobPosting.query.all()
    skill_demand = Counter()
    district_demand = Counter()
    role_demand = Counter()
    for job in postings:
        for skill in split_skills(job.skills):
            skill_demand[skill] += job.openings
        district_demand[job.district] += job.openings
        role_demand[job.title] += job.openings
    return skill_demand, district_demand, role_demand

def build_recommendations():
    demand, districts, _ = demand_analysis()
    recommendations = []
    for course in Course.query.all():
        course_skills = split_skills(course.skills)
        missing = [(s, n) for s, n in demand.items() if s not in course_skills and n >= 8]
        missing.sort(key=lambda x: x[1], reverse=True)
        placement_rate = (course.placements / course.seats * 100) if course.seats else 0
        relevance = sum(demand.get(s, 0) for s in course_skills)
        if placement_rate < 40 or relevance < 15:
            status = "Review / possible oversupply"
            action = "Review demand, employer relevance and course continuation"
        elif missing:
            status = "Curriculum update suggested"
            action = "Consider adding: " + ", ".join(s.title() for s, _ in missing[:3])
        else:
            status = "Aligned with sampled demand"
            action = "Maintain and validate with employers"
        recommendations.append({
            "course": course, "placement_rate": round(placement_rate, 1),
            "relevance": relevance, "missing": [s for s, _ in missing[:5]],
            "status": status, "action": action
        })
    return recommendations

@app.route("/")
def dashboard():
    demand, districts, roles = demand_analysis()
    courses = Course.query.all()
    jobs = JobPosting.query.all()
    total_openings = sum(j.openings for j in jobs)
    total_seats = sum(c.seats for c in courses)
    total_placements = sum(c.placements for c in courses)
    avg_placement = round(total_placements / total_seats * 100, 1) if total_seats else 0
    top_skills = demand.most_common(8)
    top_districts = districts.most_common(6)
    recommendations = build_recommendations()
    return render_template("dashboard.html", openings=total_openings, course_count=len(courses),
                           avg_placement=avg_placement, employer_count=EmployerFeedback.query.count(),
                           top_skills=top_skills, top_districts=top_districts,
                           recommendations=recommendations[:5])

@app.route("/jobs", methods=["GET", "POST"])
def jobs():
    if request.method == "POST":
        job = JobPosting(title=request.form["title"], company=request.form["company"],
                         district=request.form["district"], sector=request.form["sector"],
                         skills=request.form["skills"], proficiency=request.form["proficiency"],
                         openings=max(1, int(request.form["openings"] or 1)))
        db.session.add(job); db.session.commit()
        flash("Job demand signal added successfully.", "success")
        return redirect(url_for("jobs"))
    return render_template("jobs.html", jobs=JobPosting.query.order_by(JobPosting.id.desc()).all())

@app.route("/courses", methods=["GET", "POST"])
def courses():
    if request.method == "POST":
        course = Course(name=request.form["name"], sector=request.form["sector"],
                        district=request.form["district"], skills=request.form["skills"],
                        seats=max(0, int(request.form["seats"] or 0)),
                        placements=max(0, int(request.form["placements"] or 0)),
                        trainer_capacity=max(0, int(request.form["trainer_capacity"] or 0)),
                        equipment_status=request.form["equipment_status"])
        db.session.add(course); db.session.commit()
        flash("Course added successfully.", "success")
        return redirect(url_for("courses"))
    return render_template("courses.html", courses=Course.query.all())

@app.route("/analysis")
def analysis():
    demand, districts, roles = demand_analysis()
    return render_template("analysis.html", skills=demand.most_common(), districts=districts.most_common(),
                           roles=roles.most_common(), recommendations=build_recommendations())

@app.route("/employers", methods=["GET", "POST"])
def employers():
    if request.method == "POST":
        feedback = EmployerFeedback(employer=request.form["employer"], role=request.form["role"],
                                    district=request.form["district"], required_skills=request.form["required_skills"],
                                    satisfaction=int(request.form["satisfaction"]), comments=request.form["comments"])
        db.session.add(feedback); db.session.commit()
        flash("Employer validation recorded.", "success")
        return redirect(url_for("employers"))
    return render_template("employers.html", feedback=EmployerFeedback.query.order_by(EmployerFeedback.id.desc()).all())

@app.route("/district-plan")
def district_plan():
    demand, districts, _ = demand_analysis()
    courses = Course.query.all()
    plans = []
    for district, openings in districts.most_common():
        local_jobs = [j for j in JobPosting.query.filter_by(district=district).all()]
        local_skills = Counter()
        for j in local_jobs:
            for s in split_skills(j.skills): local_skills[s] += j.openings
        local_courses = [c for c in courses if c.district.lower() == district.lower()]
        covered = set().union(*(split_skills(c.skills) for c in local_courses)) if local_courses else set()
        gaps = [s for s, n in local_skills.most_common() if s not in covered]
        plans.append({"district":district,"openings":openings,"courses":local_courses,
                      "top_skills":local_skills.most_common(5),"gaps":gaps[:5]})
    return render_template("district.html", plans=plans)

@app.route("/reports.csv")
def export_report():
    demand, districts, roles = demand_analysis()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Report type","Name","Demand / value"])
    for skill, count in demand.most_common(): writer.writerow(["Skill demand",skill,count])
    for district, count in districts.most_common(): writer.writerow(["District openings",district,count])
    for rec in build_recommendations():
        writer.writerow(["Course alignment",rec["course"].name,rec["status"] + " | " + rec["action"]])
    mem = io.BytesIO(output.getvalue().encode("utf-8-sig")); mem.seek(0)
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="skillbridge_labour_market_report.csv")

@app.route("/api/summary")
def api_summary():
    demand, districts, roles = demand_analysis()
    return jsonify({"top_skills": demand.most_common(10), "districts": districts.most_common(),
                    "roles": roles.most_common(), "recommendations":[
                        {"course":r["course"].name,"status":r["status"],"action":r["action"]} for r in build_recommendations()]})

with app.app_context():
    db.create_all()
    seed()

if __name__ == "__main__":
    app.run(debug=True)
