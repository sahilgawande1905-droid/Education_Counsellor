import csv
import sqlite3
import pandas as pd
import random

colleges = []

# ==========================================
# 1. NATIONAL INSTITUTES (Generated)
# ==========================================
# IITs (23)
iit_cities = [("Bombay","Maharashtra",99.8), ("Delhi","Delhi",99.7), ("Madras","Tamil Nadu",99.6),
              ("Kanpur","Uttar Pradesh",99.5), ("Kharagpur","West Bengal",99.4), ("Roorkee","Uttarakhand",99.2),
              ("Guwahati","Assam",99.0), ("Hyderabad","Telangana",99.1), ("Indore","Madhya Pradesh",98.5),
              ("BHU","Uttar Pradesh",98.8), ("Jodhpur","Rajasthan",97.5), ("Patna","Bihar",97.0),
              ("Mandi","Himachal Pradesh",97.2), ("Gandhinagar","Gujarat",98.0), ("Ropar","Punjab",97.8),
              ("Bhubaneswar","Odisha",97.4), ("Tirupati","Andhra Pradesh",96.5), ("Palakkad","Kerala",96.2),
              ("Jammu","J&K",95.5), ("Dharwad","Karnataka",96.0), ("Bhilai","Chhattisgarh",95.8),
              ("Goa","Goa",96.8), ("ISM Dhanbad","Jharkhand",98.2)]

for city, state, base_cut in iit_cities:
    colleges.append([f"IIT {city}", "Engineering", "CSE", state, city, "Government", base_cut, 250000, 4.8])
    colleges.append([f"IIT {city}", "Engineering", "ECE", state, city, "Government", base_cut-1.5, 250000, 4.7])
    colleges.append([f"IIT {city}", "Engineering", "Mechanical", state, city, "Government", base_cut-3.0, 250000, 4.6])
    colleges.append([f"IIT {city}", "Engineering", "Civil", state, city, "Government", base_cut-4.5, 250000, 4.5])

# NITs (Top 20 approximation)
nit_cities = [("Trichy","Tamil Nadu",99.0), ("Surathkal","Karnataka",98.8), ("Warangal","Telangana",98.7),
              ("Calicut","Kerala",98.2), ("Rourkela","Odisha",98.0), ("Allahabad","Uttar Pradesh",97.8),
              ("Jaipur","Rajasthan",97.5), ("Nagpur","Maharashtra",97.2), ("Surat","Gujarat",97.0),
              ("Kurukshetra","Haryana",96.8), ("Durgapur","West Bengal",96.5), ("Bhopal","Madhya Pradesh",96.0)]

for city, state, base_cut in nit_cities:
    colleges.append([f"NIT {city}", "Engineering", "CSE", state, city, "Government", base_cut, 150000, 4.6])
    colleges.append([f"NIT {city}", "Engineering", "ECE", state, city, "Government", base_cut-2.0, 150000, 4.5])
    colleges.append([f"NIT {city}", "Engineering", "Mechanical", state, city, "Government", base_cut-4.0, 150000, 4.3])

# AIIMS (Medical)
aiims_cities = [("Delhi",99.8), ("Jodhpur",98.5), ("Bhopal",98.2), ("Rishikesh",98.0), ("Bhubaneswar",97.8), 
                ("Patna",97.5), ("Raipur",97.0), ("Nagpur",96.8), ("Kalyani",96.5), ("Gorakhpur",96.0)]
for city, cut in aiims_cities:
    state = "Delhi" if city == "Delhi" else "Maharashtra" if city == "Nagpur" else "Other"
    colleges.append([f"AIIMS {city}", "Medical", "MBBS", state, city, "Government", cut, 5000, 4.9])

# NLUs (Law)
nlu_cities = [("NLSIU Bangalore",99.5), ("NALSAR Hyderabad",99.0), ("NLU Delhi",98.5), ("WBNUJS Kolkata",98.0), 
              ("NLIU Bhopal",97.5), ("NLU Jodhpur",97.0), ("GNLU Gandhinagar",96.5), ("RMLNLU Lucknow",96.0),
              ("MNLU Mumbai",95.5), ("MNLU Nagpur",94.0), ("MNLU Aurangabad",92.0)]
for name, cut in nlu_cities:
    colleges.append([name, "Law", "BA LLB", "Other", name.split()[-1], "Government", cut, 250000, 4.8])


# ==========================================
# 2. MASSIVE MAHARASHTRA SPREAD
# ==========================================
maha_districts = [
    ("Mumbai", 1.0), ("Pune", 0.98), ("Nagpur", 0.95), ("Nashik", 0.92), ("Aurangabad", 0.90),
    ("Amravati", 0.88), ("Kolhapur", 0.88), ("Solapur", 0.85), ("Jalgaon", 0.85), ("Nanded", 0.84),
    ("Latur", 0.82), ("Akola", 0.80), ("Dhule", 0.78), ("Ahmednagar", 0.80), ("Satara", 0.82),
    ("Sangli", 0.85), ("Ratnagiri", 0.75), ("Chandrapur", 0.75), ("Wardha", 0.70), ("Gondia", 0.65)
]

# Generate realistic distribution of colleges for EACH district!
for dist, multiplier in maha_districts:
    # 1. Engineering
    # Govt Engg College
    colleges.append([f"Government College of Engineering {dist}", "Engineering", "CSE", "Maharashtra", dist, "Government", 92.0*multiplier, 85000, 4.2])
    colleges.append([f"Government College of Engineering {dist}", "Engineering", "Mechanical", "Maharashtra", dist, "Government", 85.0*multiplier, 85000, 4.0])
    
    # Private Tier-1/2/3 Engg
    for i in range(1, 6):
        tier_cut = 90.0 - (i * 12)  # Tier 1=78, Tier 2=66, Tier 3=54, Tier 4=42, Tier 5=30
        cut = max(5.0, tier_cut * multiplier + random.uniform(-5, 5))
        fee = 100000 + (10000 * i) if i < 3 else 80000 + (5000 * i)
        
        colleges.append([f"{dist} Institute of Technology (Tier {i})", "Engineering", "CSE", "Maharashtra", dist, "Private", cut, fee, max(3.0, 4.5 - (i*0.3))])
        colleges.append([f"{dist} Institute of Technology (Tier {i})", "Engineering", "ECE", "Maharashtra", dist, "Private", max(2.0, cut-5), fee, max(3.0, 4.5 - (i*0.3))])
        colleges.append([f"{dist} Institute of Technology (Tier {i})", "Engineering", "Civil", "Maharashtra", dist, "Private", max(1.0, cut-15), fee, max(3.0, 4.5 - (i*0.3))])
        
    # 2. Medical (GMC & Private)
    colleges.append([f"Government Medical College {dist}", "Medical", "MBBS", "Maharashtra", dist, "Government", 93.0*multiplier, 120000, 4.5])
    colleges.append([f"{dist} Private Medical Institute", "Medical", "MBBS", "Maharashtra", dist, "Private", 85.0*multiplier, 900000, 4.1])
    colleges.append([f"{dist} Ayurvedic College", "Medical", "BAMS", "Maharashtra", dist, "Private", 70.0*multiplier, 300000, 3.8])

    # 3. Law
    colleges.append([f"{dist} Government Law College", "Law", "LLB", "Maharashtra", dist, "Government", 80.0*multiplier, 25000, 4.2])
    colleges.append([f"{dist} College of Law", "Law", "BA LLB", "Maharashtra", dist, "Private", 65.0*multiplier, 75000, 3.8])

    # 4. Commerce & Arts (Degree Colleges)
    colleges.append([f"{dist} City College of Commerce", "Commerce", "B.Com", "Maharashtra", dist, "Private", 75.0*multiplier, 35000, 4.0])
    colleges.append([f"{dist} Institute of Management", "Commerce", "BBA", "Maharashtra", dist, "Private", 70.0*multiplier, 120000, 4.2])
    colleges.append([f"{dist} Arts & Science College", "Arts", "BA English", "Maharashtra", dist, "Government", 60.0*multiplier, 15000, 3.9])
    
    # 5. Science
    colleges.append([f"{dist} Science Institute", "Science", "BSc Computer Science", "Maharashtra", dist, "Private", 65.0*multiplier, 50000, 3.9])

# Add to existing CSV safely
import os
csv_path = 'c:/Education_Counsellor/backend/data/colleges.csv'
db_path = 'c:/Education_Counsellor/backend/data/colleges.db'

df_new = pd.DataFrame(colleges, columns=["college_name","stream","branch","state","city","college_type","cutoff_marks","annual_fees","rating"])

if os.path.exists(csv_path):
    df_old = pd.read_csv(csv_path)
    df_combined = pd.concat([df_old, df_new]).drop_duplicates(subset=['college_name', 'branch'])
else:
    df_combined = df_new

df_combined.to_csv(csv_path, index=False)

# Force recreate the SQLite Database so changes are live immediately!
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
df_combined.to_sql("colleges", conn, if_exists="replace", index=False)
conn.close()

print(f"✅ CRITICAL UPDATE SUCCESSFUL: Injected {len(df_new)} advanced college records across all Maharashtra districts and National Institutes!")
