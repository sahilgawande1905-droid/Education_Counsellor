import csv
import sqlite3
import pandas as pd
import random
import os

colleges = []

# ==========================================
# 1. NATIONAL INSTITUTES (Engineering & Medical & Law)
# ==========================================
# Private National (BITS, VIT, SRM)
bits_campuses = [("BITS Pilani", "Rajasthan", "Pilani", 99.0), ("BITS Goa", "Goa", "Goa", 98.0), ("BITS Hyderabad", "Telangana", "Hyderabad", 97.5)]
for name, state, city, cut in bits_campuses:
    colleges.append([name, "Engineering", "CSE", state, city, "Private", cut, 550000, 4.8])
    colleges.append([name, "Engineering", "ECE", state, city, "Private", cut-2.0, 550000, 4.6])

vit_campuses = [("VIT Vellore", "Tamil Nadu", "Vellore", 97.0), ("VIT Chennai", "Tamil Nadu", "Chennai", 95.0), ("VIT AP", "Andhra Pradesh", "Amaravati", 90.0)]
for name, state, city, cut in vit_campuses:
    colleges.append([name, "Engineering", "CSE", state, city, "Private", cut, 250000, 4.5])
    colleges.append([name, "Engineering", "ECE", state, city, "Private", cut-3.0, 250000, 4.3])

srm_campuses = [("SRM KTR", "Tamil Nadu", "Chennai", 92.0), ("SRM Ramapuram", "Tamil Nadu", "Chennai", 88.0)]
for name, state, city, cut in srm_campuses:
    colleges.append([name, "Engineering", "CSE", state, city, "Private", cut, 250000, 4.2])

# ==========================================
# 2. MASSIVE MAHARASHTRA SPREAD (INCLUDING PHARMACY & BCA)
# ==========================================
maha_districts = [
    ("Mumbai", 1.0), ("Pune", 0.98), ("Nagpur", 0.95), ("Nashik", 0.92), ("Aurangabad", 0.90),
    ("Amravati", 0.88), ("Kolhapur", 0.88), ("Solapur", 0.85), ("Jalgaon", 0.85), ("Nanded", 0.84),
    ("Latur", 0.82), ("Akola", 0.80), ("Dhule", 0.78), ("Ahmednagar", 0.80), ("Satara", 0.82)
]

for dist, multiplier in maha_districts:
    # Pharmacy (MHT-CET PCB)
    colleges.append([f"Government College of Pharmacy {dist}", "Medical", "B.Pharm", "Maharashtra", dist, "Government", 95.0*multiplier, 40000, 4.5])
    colleges.append([f"{dist} Institute of Pharmacy", "Science", "B.Pharm", "Maharashtra", dist, "Private", 82.0*multiplier, 120000, 4.0])
    
    # BCA (Computer Applications)
    colleges.append([f"{dist} College of Computer Applications", "Science", "BCA", "Maharashtra", dist, "Private", 75.0*multiplier, 60000, 4.1])
    colleges.append([f"{dist} College of Computer Applications", "Commerce", "BCA", "Maharashtra", dist, "Private", 75.0*multiplier, 60000, 4.1])
    
    # Science (BSc)
    colleges.append([f"{dist} Science Institute", "Science", "BSc", "Maharashtra", dist, "Government", 80.0*multiplier, 15000, 4.3])
    
    # Commerce (B.Com / BBA)
    colleges.append([f"{dist} City College of Commerce", "Commerce", "B.Com", "Maharashtra", dist, "Private", 75.0*multiplier, 35000, 4.0])
    colleges.append([f"{dist} Institute of Management", "Commerce", "BBA", "Maharashtra", dist, "Private", 70.0*multiplier, 120000, 4.2])
    
    # Medical (BDS / BAMS)
    colleges.append([f"{dist} Dental College", "Medical", "BDS", "Maharashtra", dist, "Private", 85.0*multiplier, 400000, 4.2])
    colleges.append([f"{dist} Ayurvedic College", "Medical", "BAMS", "Maharashtra", dist, "Private", 75.0*multiplier, 250000, 3.9])

csv_path = 'c:/Education_Counsellor/backend/data/colleges.csv'
db_path = 'c:/Education_Counsellor/backend/data/colleges.db'

df_new = pd.DataFrame(colleges, columns=["college_name","stream","branch","state","city","college_type","cutoff_marks","annual_fees","rating"])

if os.path.exists(csv_path):
    df_old = pd.read_csv(csv_path)
    df_combined = pd.concat([df_old, df_new]).drop_duplicates(subset=['college_name', 'branch'])
else:
    df_combined = df_new

df_combined.to_csv(csv_path, index=False)

if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
df_combined.to_sql("colleges", conn, if_exists="replace", index=False)
conn.close()

print(f"Injected B.Pharm, BCA, BITS, VIT, SRM! Total rows: {len(df_combined)}")
