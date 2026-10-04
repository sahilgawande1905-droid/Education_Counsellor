import json
import re
import asyncio

try:
    from google import genai
    from google.genai import types
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "Missing Google Gemini SDK. Install the backend dependencies with `python -m pip install -r requirements.txt` after ensuring the project uses `google-genai`."
    ) from exc

from config import GEMINI_API_KEY, GEMINI_MODEL, FALLBACK_MODELS
from models import StudentProfile
from database import get_colleges_from_db

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Curated campus photography mapped by keywords
CAMPUS_IMAGE_MAP = [
    (r"coep", "https://images.unsplash.com/photo-1562774053-701939374585?w=700&auto=format&fit=crop&q=80"),
    (r"vjti", "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=700&auto=format&fit=crop&q=80"),
    (r"iit", "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=700&auto=format&fit=crop&q=80"),
    (r"nit", "https://images.unsplash.com/photo-1592280771190-3e2e4d571952?w=700&auto=format&fit=crop&q=80"),
    (r"pict", "https://images.unsplash.com/photo-1519452635265-7b1fbfd1e4e0?w=700&auto=format&fit=crop&q=80"),
    (r"mit|vit", "https://images.unsplash.com/photo-1525921429624-479b6a26d84d?w=700&auto=format&fit=crop&q=80"),
    (r"spit|somaiya", "https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?w=700&auto=format&fit=crop&q=80"),
    (r"aiims|grant|seth|topiwala|medical", "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?w=700&auto=format&fit=crop&q=80"),
    (r"srcc|xavier|hindu|commerce|bmcc", "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=700&auto=format&fit=crop&q=80"),
    (r"fergusson|ruia|science|iiser", "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=700&auto=format&fit=crop&q=80"),
    (r"law|nlu|nalsar|glc|ils", "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=700&auto=format&fit=crop&q=80"),
    (r"design|nid|nift", "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=700&auto=format&fit=crop&q=80")
]

STREAM_DEFAULT_IMAGES = {
    "Engineering": "https://images.unsplash.com/photo-1562774053-701939374585?w=700&auto=format&fit=crop&q=80",
    "Medical": "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?w=700&auto=format&fit=crop&q=80",
    "Science": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=700&auto=format&fit=crop&q=80",
    "Commerce": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=700&auto=format&fit=crop&q=80",
    "Arts": "https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?w=700&auto=format&fit=crop&q=80",
    "Law": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=700&auto=format&fit=crop&q=80",
    "Design": "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=700&auto=format&fit=crop&q=80"
}

def get_college_image(name: str, stream: str = "Engineering") -> str:
    name_lower = name.lower()
    for pattern, url in CAMPUS_IMAGE_MAP:
        if re.search(pattern, name_lower):
            return url
    return STREAM_DEFAULT_IMAGES.get(stream, STREAM_DEFAULT_IMAGES["Engineering"])


COLLEGE_PROMPT_RAG = """You are an expert Indian college admission strategist. 
We have queried our local database for matches. 

Student Details:
- Name: {name}
- Stream: {stream}
- Exam Taken: {exam_type}
- Marks/Percentile: {marks}%
- Category: {category}
- Family Income: {family_income}

Database Matches:
{db_matches}

Your task:
Format 5-7 highly accurate colleges into a JSON array. 
CRITICAL EXAM RULE: You MUST cross-check the 'Exam Taken' against the college. (e.g., IITs/NITs ONLY accept JEE, they DO NOT accept MHT-CET, State CETs, or 12th %). 
If a database match does not accept the student's exam, DISCARD IT, and intelligently generate a replacement college that DOES accept their exam.

CRITICAL MATH RULE: Percentiles and percentages CANNOT exceed 100.0. When calculating the `target_2027_score`, if the historical cutoff is extremely high (e.g., 99.8), do NOT just add a flat buffer that pushes it over 100. Cap your target score at a maximum of 99.99%.

Since our database only contains basic info, intelligently estimate the missing fields (placements, facilities, nirf_rank, established) for each college.
Crucially, you MUST calculate a `target_2027_score`, write a `cap_strategy`, and determine `financial_aid` eligibility based on their Category and Income.

Output MUST be a JSON array of objects with these keys:
- college_name: Official college name
- location: City and State
- stream: {stream}
- branch: Relevant branch or course name
- college_type: "Government" or "Private"
- cutoff_marks: A realistic percentage or percentile cutoff number
- annual_fees: Estimated annual fee in INR as an integer (e.g. 120000)
- rating: Number between 3.5 and 4.9
- nirf_rank: Text description of rank
- placement_avg: Text summary (e.g. "₹8.5 LPA")
- placement_high: Text summary (e.g. "₹24.0 LPA")
- established: Year founded (e.g. 1960)
- facilities: An array of 3-4 key tags (e.g. ["Central Library", "Hostels"])
- why_recommended: One concise sentence explaining why it fits this student
- cap_strategy: A 1-2 sentence strategy for CAP rounds
- target_2027_score: A safe target score/percentile for next year (max 99.99%)
- financial_aid: A 1-2 sentence note about applicable scholarships (e.g. "Eligible for MahaDBT EBC")
- insight_tags: An array of 2-3 short UI badges (max 4 words) explaining exactly WHY it was chosen (e.g., ["🔥 State Quota Applied", "💸 Under Budget", "⚠️ High AIQ Risk", "🎯 Safe Match"])

Return ONLY the JSON array.
"""


def parse_number(val, default=80.0) -> float:
    if isinstance(val, (int, float)):
        return float(val)
    if not val:
        return default
    m = re.search(r"(\d+(\.\d+)?)", str(val).replace(",", ""))
    if m:
        try:
            return float(m.group(1))
        except:
            pass
    return default


def parse_fees(val, default=150000) -> int:
    if isinstance(val, (int, float)):
        return int(val)
    if not val:
        return default
    s = str(val).replace(",", "").replace("₹", "").replace("INR", "").strip()
    m = re.search(r"(\d+(\.\d+)?)", s)
    if m:
        try:
            num = float(m.group(1))
            if "lakh" in str(val).lower() or (num < 100 and "l" in str(val).lower()):
                return int(num * 100000)
            return int(num)
        except:
            pass
    return default


def get_eligibility_status(student_marks: float, cutoff: float) -> dict:
    diff = student_marks - cutoff
    if diff >= 2:
        return {"status": "eligible", "label": "✅ Eligible", "color": "success"}
    elif diff >= -6:
        return {"status": "borderline", "label": "⚠️ Borderline", "color": "warning"}
    else:
        return {"status": "not_eligible", "label": "❌ Aspirational", "color": "danger"}


def get_career_opportunities(stream: str) -> list:
    careers = {
        "Engineering": [
            "Software Development Engineer (SDE)",
            "AI / Machine Learning Engineer",
            "Data Scientist & Cloud Architect",
            "Full Stack Developer"
        ],
        "Medical": [
            "MBBS Doctor / Resident Physician",
            "Specialist Surgeon",
            "Clinical & Genetic Researcher"
        ],
        "Science": [
            "Research Scientist (CSIR / DRDO)",
            "Data Scientist & Quantitative Analyst",
            "Biotechnologist & Bioinformatician"
        ],
        "Commerce": [
            "Chartered Accountant (CA)",
            "Investment Banking Analyst",
            "Corporate Financial Advisor"
        ],
        "Arts": [
            "Civil Services (UPSC IAS/IPS/IFS)",
            "Public Policy Analyst",
            "Journalist & Media Editor"
        ],
    }
    return careers.get(stream, ["Professional Specialist", "Researcher", "Consultant", "Entrepreneur"])


async def get_live_college_recommendations(profile: StudentProfile) -> list:
    """
    Fetch LIVE AI recommendations using a RAG workflow (SQLite Database -> Gemini API).
    """
    # 1. RAG Retrieval Phase: Query local SQLite database
    db_colleges = get_colleges_from_db(
        stream=profile.stream, 
        marks=profile.marks, 
        exam_type=profile.exam_type,
        category=getattr(profile, 'category', 'Open'),
        budget=getattr(profile, 'budget', 'Any'),
        preferred_state=getattr(profile, 'preferred_state', 'Any'),
        preferred_branch=getattr(profile, 'preferred_branch', 'Any'),
        gender=getattr(profile, 'gender', 'Male'),
        family_income=getattr(profile, 'family_income', 'Any'),
        limit=12
    )
    
    # 2. RAG Generation Phase: Construct prompt
    if not db_colleges:
        if profile.marks < 40:
            db_matches_str = "No matches in DB. Student score is very low. DO NOT hallucinate elite Tier-1 colleges (IIT/NIT/AIIMS). Recommend 5 realistic Tier-3 private/state colleges or management quota options."
        else:
            db_matches_str = "No exact matches in DB. Recommend 5 standard top colleges based on their profile."
    else:
        db_matches_str = "\n".join([f"- {c['college_name']} ({c['branch']}) | Cutoff: {c['cutoff_marks']}% | Fees: ₹{c['annual_fees']}" for c in db_colleges])

    prompt = COLLEGE_PROMPT_RAG.format(
        name=profile.name,
        stream=profile.stream,
        exam_type=profile.exam_type,
        marks=profile.marks,
        category=getattr(profile, 'category', 'Open'),
        family_income=getattr(profile, 'family_income', 'Any'),
        db_matches=db_matches_str
    )

    models_to_try = [GEMINI_MODEL] + [m for m in FALLBACK_MODELS if m != GEMINI_MODEL]

    if client:
        for model_name in models_to_try:
            try:
                loop = asyncio.get_event_loop()
                resp = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                temperature=0.3,
                                response_mime_type="application/json"
                            )
                        )
                    ),
                    timeout=4.5
                )

                raw_text = resp.text or ""
                if not raw_text and resp.candidates:
                    for part in resp.candidates[0].content.parts:
                        if hasattr(part, "text") and part.text:
                            raw_text = part.text
                            break

                if not raw_text:
                    continue

                raw_text = raw_text.strip()
                raw_text = re.sub(r"```json\s*", "", raw_text)
                raw_text = re.sub(r"```\s*", "", raw_text)

                match = re.search(r"\[.*\]", raw_text, re.DOTALL)
                json_str = match.group() if match else raw_text
                colleges_data = json.loads(json_str)

                if isinstance(colleges_data, list) and len(colleges_data) > 0:
                    results = []
                    for c in colleges_data:
                        cname = str(c.get("college_name", "College"))
                        cutoff = parse_number(c.get("cutoff_marks"), 75.0)
                        fees = parse_fees(c.get("annual_fees"), 100000)
                        rating = parse_number(c.get("rating"), 4.3)
                        eligibility = get_eligibility_status(profile.marks, cutoff)
                        image_url = get_college_image(cname, profile.stream)

                        results.append({
                            "college_name": cname,
                            "location": str(c.get("location", "India")),
                            "stream": str(c.get("stream", profile.stream)),
                            "branch": str(c.get("branch", "Relevant Program")),
                            "college_type": str(c.get("college_type", "Government")),
                            "cutoff_marks": round(cutoff, 1),
                            "annual_fees": fees,
                            "rating": min(5.0, max(3.5, round(rating, 1))),
                            "image_url": image_url,
                            "nirf_rank": str(c.get("nirf_rank", "Recognized")),
                            "placement_avg": str(c.get("placement_avg", "High Placement Rate")),
                            "placement_high": str(c.get("placement_high", "Excellent Career Prospects")),
                            "established": c.get("established", 1990),
                            "facilities": c.get("facilities", ["Modern Labs", "Library", "Hostels", "Sports"]),
                            "why_recommended": str(c.get("why_recommended", "Recommended based on your academic profile.")),
                            "cap_strategy": str(c.get("cap_strategy", "Apply dynamically in CAP Round 1 or 2.")),
                            "target_2027_score": str(c.get("target_2027_score", f"{round(cutoff + 1.0, 1)}%")),
                            "financial_aid": str(c.get("financial_aid", "Standard fees apply.")),
                            "eligibility": eligibility,
                            "student_marks": profile.marks,
                        })
                    return results
            except Exception as e:
                print(f"Warning: Model {model_name} failed: {e}")
                continue

    # 3. Absolute Fallback: Return raw SQLite data if API is totally dead
    print("API Failed or Missing. Using direct local SQLite database fallback...")
    fallback_results = []
    
    for c in db_colleges:
        cname = c["college_name"]
        cutoff = parse_number(c.get("cutoff_marks"), 75.0)
        eligibility = get_eligibility_status(profile.marks, cutoff)
        img = get_college_image(cname, c["stream"])
        
        fallback_results.append({
            "college_name": cname,
            "location": f'{c.get("city", "City")}, {c.get("state", "India")}',
            "stream": c["stream"],
            "branch": c.get("branch", "Program"),
            "college_type": c.get("college_type", "Government"),
            "cutoff_marks": round(cutoff, 1),
            "annual_fees": c.get("annual_fees", 100000),
            "rating": c.get("rating", 4.5),
            "image_url": img,
            "eligibility": eligibility,
            "student_marks": profile.marks,
            # Hardcoded fallback strategies
            "cap_strategy": "Safe choice for Round 2." if eligibility["status"] == "eligible" else "Aspirational for Round 1.",
            "target_2027_score": f"{round(cutoff + 1.2, 1)}%",
            "financial_aid": "Check state scholarship portal."
        })
        
    return fallback_results

def get_featured_colleges(stream: str = "All") -> list:
    """Return featured colleges for the landing page using SQLite."""
    from database import init_db
    import sqlite3
    import os
    
    DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "colleges.db")
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if stream == "All":
        cursor.execute("SELECT * FROM colleges ORDER BY rating DESC LIMIT 9")
    else:
        cursor.execute("SELECT * FROM colleges WHERE stream = ? ORDER BY rating DESC LIMIT 9", (stream,))
        
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for c in rows:
        c_dict = dict(c)
        img = get_college_image(c_dict["college_name"], c_dict["stream"])
        results.append({
            **c_dict,
            "image_url": img,
            "eligibility": {"status": "eligible", "label": "Featured", "color": "primary"},
            "student_marks": 90.0
        })
    return results
