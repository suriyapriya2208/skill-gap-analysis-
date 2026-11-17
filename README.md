# SkillBridge – Labour Market Intelligence & Curriculum Alignment Platform

A runnable academic prototype that turns job-demand signals and employer feedback into skill-demand analysis, course-alignment recommendations and district-level training plans.

## Features
- Dashboard with job openings, course count, placement indicator and high-demand skills.
- Job-posting signal entry (role, sector, district, skills, proficiency and openings).
- Training-course inventory with seats, placements, trainer capacity and equipment status.
- Skill-demand aggregation weighted by number of openings.
- Rule-based course gap analysis and curriculum recommendations.
- Employer validation and satisfaction capture.
- District-level training plan with local skill gaps.
- CSV report export and JSON summary API.
- SQLite database seeded with sample Tamil Nadu data on first run.

## Run locally
Requires Python 3.10+.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## Demo workflow
1. Open **Job Demand** and add current job postings or employer demand signals.
2. Open **Courses** and enter course seats, placements, trainer capacity and equipment status.
3. Open **Employer Validation** and record employer feedback.
4. Review **Skill Analysis** and **District Plan**.
5. Download the CSV report from the navigation bar.

## Project structure
```
skillbridge_lmi/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── jobs.html
│   ├── courses.html
│   ├── analysis.html
│   ├── employers.html
│   └── district.html
└── static/
    └── style.css
```

## Recommendation logic
- Each skill in a job posting receives the posting's `openings` weight.
- Course relevance is the sum of demand weights for skills listed in the course.
- Course placement rate is placements divided by seats.
- Courses with placement rate below 40% or low sampled skill relevance are flagged for review.
- Frequently requested skills missing from a course are suggested as curriculum additions.
- District plans compare local job-skill demand with skills covered by courses in that district.

This is an explainable baseline, not a trained predictive AI model. Real deployment should connect verified job-board feeds, validated employer surveys, official sector statistics and audited placement records; add authentication, role-based access, privacy controls, data-quality checks and model evaluation before production use.

## Suggested future enhancements
- Integrate job-board APIs and scheduled data ingestion.
- Use NLP skill extraction with a curated occupation/skill taxonomy.
- Map courses to NSQF / QP-NOS / qualification standards.
- Add role-based login for administrators, institutes and employers.
- Add time-series forecasting and district maps.
