import csv
import sqlite3
import pandas as pd

colleges = []

# ==========================================
# 1. ALL IITS (Top 15 Represented with Branches)
# ==========================================
iits = [
    ("IIT Bombay", "Maharashtra", "Mumbai", 99.8, 98.5, 96.0, 93.0),
    ("IIT Delhi", "Delhi", "Delhi", 99.7, 98.2, 95.5, 92.5),
    ("IIT Madras", "Tamil Nadu", "Chennai", 99.6, 98.0, 95.0, 92.0),
    ("IIT Kanpur", "Uttar Pradesh", "Kanpur", 99.5, 97.5, 94.5, 91.0),
    ("IIT Kharagpur", "West Bengal", "Kharagpur", 99.3, 97.0, 94.0, 90.5),
    ("IIT Roorkee", "Uttarakhand", "Roorkee", 99.2, 96.5, 93.5, 90.0),
    ("IIT Guwahati", "Assam", "Guwahati", 99.0, 96.0, 93.0, 89.0),
    ("IIT Hyderabad", "Telangana", "Hyderabad", 99.1, 96.2, 93.2, 89.5),
    ("IIT BHU", "Uttar Pradesh", "Varanasi", 98.8, 95.5, 92.5, 88.0),
    ("IIT Indore", "Madhya Pradesh", "Indore", 98.5, 95.0, 91.5, 87.0),
    ("IIT Gandhinagar", "Gujarat", "Gandhinagar", 98.2, 94.5, 91.0, 86.0),
    ("IIT Ropar", "Punjab", "Ropar", 98.0, 94.0, 90.5, 85.0),
    ("IIT Patna", "Bihar", "Patna", 97.5, 93.5, 90.0, 84.0),
    ("IIT Mandi", "Himachal Pradesh", "Mandi", 97.0, 93.0, 89.0, 83.0),
    ("IIT Jodhpur", "Rajasthan", "Jodhpur", 96.5, 92.0, 88.0, 82.0)
]
for name, state, city, cse, ece, mech, civil in iits:
    colleges.append([name, "Engineering", "CSE", state, city, "Government", cse, 250000, 4.8])
    colleges.append([name, "Engineering", "ECE", state, city, "Government", ece, 250000, 4.7])
    colleges.append([name, "Engineering", "Mechanical", state, city, "Government", mech, 250000, 4.6])
    colleges.append([name, "Engineering", "Civil", state, city, "Government", civil, 250000, 4.5])


# ==========================================
# 2. ALL NITS (Top 20 Represented with Branches)
# ==========================================
nits = [
    ("NIT Trichy", "Tamil Nadu", "Trichy", 99.0, 97.0, 94.0, 91.0),
    ("NIT Surathkal", "Karnataka", "Mangalore", 98.8, 96.5, 93.5, 90.0),
    ("NIT Warangal", "Telangana", "Warangal", 98.7, 96.2, 93.0, 89.5),
    ("NIT Calicut", "Kerala", "Kozhikode", 98.5, 95.5, 92.0, 88.0),
    ("NIT Rourkela", "Odisha", "Rourkela", 98.2, 95.0, 91.5, 87.5),
    ("MNNIT Allahabad", "Uttar Pradesh", "Allahabad", 98.0, 94.5, 91.0, 87.0),
    ("MNIT Jaipur", "Rajasthan", "Jaipur", 97.5, 94.0, 90.5, 86.0),
    ("VNIT Nagpur", "Maharashtra", "Nagpur", 97.2, 93.5, 90.0, 85.5),
    ("SVNIT Surat", "Gujarat", "Surat", 97.0, 93.0, 89.0, 85.0),
    ("NIT Kurukshetra", "Haryana", "Kurukshetra", 96.5, 92.5, 88.5, 84.0),
    ("NIT Durgapur", "West Bengal", "Durgapur", 96.0, 92.0, 87.5, 83.0),
    ("NIT Jalandhar", "Punjab", "Jalandhar", 95.5, 91.0, 86.5, 82.0),
    ("NIT Jamshedpur", "Jharkhand", "Jamshedpur", 95.0, 90.5, 86.0, 81.0),
    ("NIT Bhopal", "Madhya Pradesh", "Bhopal", 94.5, 90.0, 85.5, 80.0),
    ("NIT Raipur", "Chhattisgarh", "Raipur", 94.0, 89.0, 84.5, 79.0)
]
for name, state, city, cse, ece, mech, civil in nits:
    colleges.append([name, "Engineering", "CSE", state, city, "Government", cse, 150000, 4.6])
    colleges.append([name, "Engineering", "ECE", state, city, "Government", ece, 150000, 4.5])
    colleges.append([name, "Engineering", "Mechanical", state, city, "Government", mech, 150000, 4.4])
    colleges.append([name, "Engineering", "Civil", state, city, "Government", civil, 150000, 4.3])


# ==========================================
# 3. MAHARASHTRA COLLEGES (0 to 100 Percentile Gradient)
# ==========================================
maha_colleges = [
    # TIER 1 (98-100)
    ("COEP Pune", "Pune", "Government", 99.8, 99.0, 98.0, 97.0, 90000, 4.8),
    ("VJTI Mumbai", "Mumbai", "Government", 99.7, 98.8, 97.5, 96.5, 85000, 4.7),
    ("SPIT Mumbai", "Mumbai", "Private", 99.2, 98.0, 95.0, None, 175000, 4.6),
    ("PICT Pune", "Pune", "Private", 99.0, 97.5, None, None, 150000, 4.6),
    ("Walchand College", "Sangli", "Government", 98.5, 97.0, 95.5, 94.0, 85000, 4.5),
    
    # TIER 2 (92-98)
    ("VIT Pune", "Pune", "Private", 97.5, 95.5, 93.0, 90.0, 165000, 4.4),
    ("DJ Sanghvi", "Mumbai", "Private", 97.0, 95.0, 92.0, None, 190000, 4.5),
    ("KJ Somaiya", "Mumbai", "Private", 96.5, 94.5, 91.5, 89.0, 250000, 4.3),
    ("PCCOE Pune", "Pune", "Private", 95.0, 92.5, 89.0, 86.0, 140000, 4.3),
    ("Cummins College (Women)", "Pune", "Private", 94.5, 91.5, 88.0, None, 150000, 4.4),
    ("Thadomal Shahani", "Mumbai", "Private", 94.0, 91.0, 87.0, None, 180000, 4.3),
    ("VESIT Mumbai", "Mumbai", "Private", 93.0, 90.0, 86.0, None, 130000, 4.2),
    
    # TIER 3 (80-92)
    ("Thakur College", "Mumbai", "Private", 91.0, 88.0, 84.0, 80.0, 160000, 4.1),
    ("Don Bosco Institute", "Mumbai", "Private", 90.0, 87.0, 82.0, 78.0, 140000, 4.1),
    ("DY Patil Pimpri", "Pune", "Private", 89.0, 85.0, 80.0, 75.0, 135000, 4.0),
    ("Ramrao Adik IT", "Navi Mumbai", "Private", 88.0, 84.0, 79.0, None, 150000, 4.0),
    ("Sinhgad Vadgaon", "Pune", "Private", 85.0, 81.0, 75.0, 70.0, 125000, 3.9),
    ("AISSMS Pune", "Pune", "Private", 82.0, 78.0, 72.0, 68.0, 130000, 3.8),
    
    # TIER 4 (50-80)
    ("MIT Academy Alandi", "Pune", "Private", 78.0, 74.0, 68.0, 62.0, 160000, 3.9),
    ("Datta Meghe", "Navi Mumbai", "Private", 75.0, 70.0, 65.0, 60.0, 110000, 3.7),
    ("Terna Engineering", "Navi Mumbai", "Private", 72.0, 68.0, 62.0, 55.0, 115000, 3.6),
    ("Saraswati College", "Navi Mumbai", "Private", 68.0, 62.0, 58.0, 50.0, 105000, 3.5),
    ("Atharva College", "Mumbai", "Private", 65.0, 60.0, 55.0, 48.0, 120000, 3.5),
    ("GH Raisoni", "Pune", "Private", 60.0, 55.0, 50.0, 45.0, 110000, 3.4),
    
    # TIER 5 (0-50 - Extremely lenient cutoffs for low scorers)
    ("Indira College", "Pune", "Private", 48.0, 42.0, 38.0, 32.0, 100000, 3.3),
    ("AP Shah Institute", "Thane", "Private", 45.0, 38.0, 32.0, 28.0, 95000, 3.2),
    ("Universal College", "Vasai", "Private", 40.0, 35.0, 28.0, 22.0, 90000, 3.1),
    ("JCOE Kuran", "Pune", "Private", 35.0, 28.0, 20.0, 15.0, 75000, 3.0),
    ("Siddhant College", "Pune", "Private", 25.0, 20.0, 12.0, 8.0, 70000, 2.9),
    ("Anantrao Pawar", "Pune", "Private", 15.0, 10.0, 5.0, 2.0, 65000, 2.8),
    ("KVCET", "Palghar", "Private", 8.0, 5.0, 2.0, 1.0, 60000, 2.7)
]

for name, city, type_, cse, ece, mech, civil, fees, rating in maha_colleges:
    if cse: colleges.append([name, "Engineering", "CSE", "Maharashtra", city, type_, cse, fees, rating])
    if ece: colleges.append([name, "Engineering", "ECE", "Maharashtra", city, type_, ece, fees, rating - 0.1])
    if mech: colleges.append([name, "Engineering", "Mechanical", "Maharashtra", city, type_, mech, fees, rating - 0.2])
    if civil: colleges.append([name, "Engineering", "Civil", "Maharashtra", city, type_, civil, fees, rating - 0.3])


# Add to existing CSV safely
import os
csv_path = 'c:/Education_Counsellor/backend/data/colleges.csv'
db_path = 'c:/Education_Counsellor/backend/data/colleges.db'

# Convert to DataFrame
df_new = pd.DataFrame(colleges, columns=["college_name","stream","branch","state","city","college_type","cutoff_marks","annual_fees","rating"])

if os.path.exists(csv_path):
    df_old = pd.read_csv(csv_path)
    # Filter out exact duplicates
    df_combined = pd.concat([df_old, df_new]).drop_duplicates(subset=['college_name', 'branch'])
else:
    df_combined = df_new

df_combined.to_csv(csv_path, index=False)

# Rebuild DB
conn = sqlite3.connect(db_path)
df_combined.to_sql("colleges", conn, if_exists="replace", index=False)
conn.close()

print(f"Successfully generated and injected {len(df_new)} advanced college records!")
