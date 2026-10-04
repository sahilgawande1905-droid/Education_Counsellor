import sqlite3
import pandas as pd
import os

# Paths relative to the backend directory
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "colleges.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "colleges.csv")

def init_db():
    """Create the SQLite database and populate it from the CSV if it doesn't exist."""
    if not os.path.exists(DB_PATH):
        print("Initializing SQLite database from CSV data...")
        # Create directory if it somehow doesn't exist
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_csv(CSV_PATH)
        # Load the CSV into an SQLite table called 'colleges'
        df.to_sql("colleges", conn, if_exists="replace", index=False)
        conn.close()
        print("Database initialized successfully!")

def normalize_student_score(raw_score: float, exam_type: str) -> float:
    """
    Transforms raw exam metrics (Percentage, Percentile, Raw Marks) 
    into a standardized 0-100 Normalized Competitiveness Index (NCI)
    to prevent cross-metric corruption during database retrieval.
    """
    exam_type = (exam_type or "").upper().strip()
    
    # 1. Percentile Metrics (JEE Main, MHT-CET, CUET, NEET) -> Retain near 1:1 distribution
    if any(x in exam_type for x in ["JEE MAIN", "MHT-CET", "MHTCET", "CUET", "NEET", "CET"]):
        return max(0.0, min(100.0, raw_score))
        
    # 2. Absolute Metrics (12th Boards) -> Compress to account for grade inflation
    elif any(x in exam_type for x in ["BOARDS", "12TH", "12TH %", "CBSE", "HSC"]):
        # Example: A 95% board score normalizes to an NCI of ~90.25
        return max(0.0, min(100.0, raw_score * 0.95))
        
    # 3. Dynamic Raw Scores (JEE Advanced - Out of 360 baseline)
    elif "ADVANCED" in exam_type:
        # An elite 95/360 sits at roughly ~26.3% raw marks, which translates to an NCI of ~88.0
        percentage_of_paper = (raw_score / 360.0) * 100
        nci_score = (percentage_of_paper * 2.5) + 22.0 
        return max(0.0, min(100.0, nci_score))
        
    # Fallback default
    return raw_score

def get_max_fee(budget_str: str, category: str = "Open", gender: str = "Male", state: str = "Any", income: str = "Any") -> int:
    b = (budget_str or "").upper().strip()
    base_budget = 9999999
    
    if "<1L" in b: base_budget = 100000
    elif "<3L" in b: base_budget = 300000
    elif "3-8L" in b or "5-15L" in b: base_budget = 800000
    elif "<5L" in b: base_budget = 500000
    
    cat = (category or "").upper()
    gen = (gender or "").upper()
    
    # ---------------------------------------------------------
    # TFWS & WOMEN'S 100% TUITION WAIVER (MAHARASHTRA)
    # ---------------------------------------------------------
    # In Maharashtra, female students with income <8L get 100% tuition fee waived.
    # Open category boys with income <8L also apply for TFWS (5% seats).
    if state == "Maharashtra" and income == "<8L":
        return base_budget * 8  # Huge purchasing power for TFWS / Women's policy
        
    # SC/ST get nearly 100% tuition waiver (pay only dev fees). 
    if cat in ["SC", "ST"]:
        return base_budget * 5  
    # OBC/EWS/NT get ~50% tuition fee waiver (EBC scholarship).
    elif cat in ["OBC", "NT", "EWS"]:
        return base_budget * 2  
        
    return base_budget

def get_colleges_from_db(stream: str, marks: float, exam_type: str = "", category: str = "Open", budget: str = "Any", preferred_state: str = "Any", preferred_branch: str = "Any", gender: str = "Male", family_income: str = "Any", limit: int = 10):
    """Retrieve colleges using NCI, Category adjustments, Budget filters, State quotas, and Branch preference."""
    init_db()
    
    # Pre-normalize the score to NCI before hitting the database
    nci_score = normalize_student_score(marks, exam_type)
    
    # Category NCI Boost (Simulating lower cutoffs for reserved categories)
    cat = (category or "").upper()
    gen = (gender or "").upper()
    inc = (family_income or "").upper()
    
    if cat == "SC": nci_score += 8.0
    elif cat == "ST": nci_score += 10.0
    elif cat in ["OBC", "NT", "EWS"]: nci_score += 4.0
    
    # Horizontal Women's Quota (e.g. 30% reservation in MH gives a slight mathematical edge)
    if gen == "FEMALE":
        nci_score += 1.5
        
    # TFWS (Tuition Fee Waiver Scheme) - 5% Supernumerary Seats Penalty
    # If an Open Category student (Boy or Girl) relies on TFWS (Income <8L) to afford a college,
    # we mathematically PENALIZE their score by -2.5% to simulate the brutally high TFWS cutoffs.
    if cat == "OPEN" and inc == "<8L":
        nci_score -= 2.5
        
    max_fee = get_max_fee(budget, category, gender, preferred_state, family_income)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # =========================================================================
    # DYNAMIC QUOTA SIMULATOR (HS vs OS / AIQ)
    # =========================================================================
    if preferred_state and preferred_state != "Any":
        # Simulate Home State (85%) vs Other State (15% AIQ) Quota
        # If the college is in their Home State, they get a generous +3.0 buffer.
        # If the college is Out of State, they get a strict -2.0 penalty to simulate harsh AIQ cutoffs.
        conditions = ["stream = ?", "cutoff_marks <= (? + CASE WHEN state = ? THEN 3.0 ELSE -2.0 END)", "annual_fees <= ?"]
        query_params = [stream, nci_score + 5.0, preferred_state, max_fee]
    else:
        conditions = ["stream = ?", "cutoff_marks <= ?", "annual_fees <= ?"]
        query_params = [stream, nci_score + 5.0, max_fee]
        
    # Branch Filter
    if preferred_branch and preferred_branch != "Any":
        conditions.append("branch LIKE ?")
        query_params.append(f"%{preferred_branch}%")
        
    # =========================================================================
    # EXAM ROUTING ENGINE (Rule-based configuration)
    # Follows Open/Closed Principle: Add new exams here without touching SQL logic
    # =========================================================================
    EXAM_RULES = {
        "MHT-CET": {"banned_keywords": ["IIT ", "NIT ", "IIIT ", "AIIMS ", "NLU ", "National Law"]},
        "STATE CET": {"banned_keywords": ["IIT ", "NIT ", "IIIT ", "AIIMS ", "NLU ", "National Law"]},
        "12TH": {"banned_keywords": ["IIT ", "NIT ", "IIIT ", "AIIMS ", "NLU ", "National Law"]},
        "JEE MAIN": {"allowed_streams": ["Engineering", "Science"], "banned_keywords": ["IIT ", "IISc "]},
        "JEE ADVANCED": {"allowed_streams": ["Engineering", "Science"], "required_keywords": ["IIT ", "IISc "]},
        "NEET": {"allowed_streams": ["Medical"], "banned_keywords": ["IIT "]},
        "BITSAT": {"required_keywords": ["BITS "]},
        "VITEEE": {"required_keywords": ["VIT Vellore", "VIT Chennai", "VIT AP", "VIT Bhopal"]},
        "SRMJEEE": {"required_keywords": ["SRM "]},
        "PCB": {"allowed_branches": ["B.Pharm", "BSc", "BAMS", "BDS", "MBBS"]}
    }

    ex_upper = (exam_type or "").upper()
    
    # Apply rules dynamically
    for exam_key, rules in EXAM_RULES.items():
        if exam_key in ex_upper:
            # 1. Apply Banned Keywords
            if "banned_keywords" in rules:
                for word in rules["banned_keywords"]:
                    conditions.append(f"college_name NOT LIKE '%{word}%'")
            
            # 2. Apply Required Keywords (OR logic)
            if "required_keywords" in rules:
                reqs = [f"college_name LIKE '%{word}%'" for word in rules["required_keywords"]]
                conditions.append(f"({' OR '.join(reqs)})")
                
            # 3. Apply Allowed Streams
            if "allowed_streams" in rules:
                streams_formatted = ", ".join([f"'{s}'" for s in rules["allowed_streams"]])
                conditions.append(f"stream IN ({streams_formatted})")
                
            # 4. Apply Allowed Branches
            if "allowed_branches" in rules:
                branches_formatted = ", ".join([f"'{b}'" for b in rules["allowed_branches"]])
                conditions.append(f"branch IN ({branches_formatted})")
                
    where_clause = " AND ".join(conditions)
        
    if preferred_state and preferred_state != "Any":
        query = f"""
            SELECT * FROM colleges
            WHERE {where_clause}
            ORDER BY (state = ?) DESC, cutoff_marks DESC, rating DESC
            LIMIT ?
        """
        query_params.extend([preferred_state, limit])
    else:
        query = f"""
            SELECT * FROM colleges
            WHERE {where_clause}
            ORDER BY cutoff_marks DESC, rating DESC
            LIMIT ?
        """
        query_params.append(limit)
        
    cursor.execute(query, tuple(query_params))
        
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
