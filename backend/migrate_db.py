import sqlite3
import pandas as pd

conn = sqlite3.connect('c:/Education_Counsellor/backend/data/colleges.db')
df = pd.read_sql_query('SELECT * FROM colleges', conn)

def get_exams(row):
    name = str(row['college_name']).upper()
    stream = str(row['stream']).upper()
    branch = str(row['branch']).upper()
    state = str(row['state']).upper()
    c_type = str(row['college_type']).upper()
    
    exams = []
    
    if 'IIT ' in name:
        exams.append('JEE ADVANCED')
    elif 'NIT ' in name or 'IIIT ' in name or 'DTU' in name:
        exams.append('JEE MAIN')
    elif 'BITS ' in name or 'BITS' in name:
        exams.append('BITSAT')
    elif 'VIT ' in name:
        exams.append('VITEEE')
    elif 'SRM ' in name:
        exams.append('SRMJEEE')
    elif stream == 'MEDICAL' or 'MBBS' in branch or 'BDS' in branch or 'BAMS' in branch:
        exams.append('NEET UG')
    elif branch == 'B.PHARM':
        exams.extend(['MHT-CET (PCB)', 'NEET UG'])
    elif stream == 'LAW':
        exams.extend(['CLAT', 'LSAT INDIA', 'MH CET LAW', '12TH %'])
    elif stream in ['COMMERCE', 'ARTS'] or 'BSC' in branch or 'BCA' in branch:
        exams.extend(['12TH %', 'CUET UG'])
    elif stream == 'ENGINEERING':
        if state == 'MAHARASHTRA':
            # Government colleges and top state colleges ONLY take MHT-CET
            if c_type == 'GOVERNMENT' or name in ['COEP PUNE', 'VJTI MUMBAI', 'SPIT MUMBAI', 'PICT PUNE']:
                exams.append('MHT-CET (PCM)')
                exams.append('MHT-CET')
            else:
                # Private colleges take both
                exams.extend(['MHT-CET (PCM)', 'MHT-CET', 'JEE MAIN'])
        else:
            exams.extend(['JEE MAIN', 'STATE CET'])
            
    if not exams:
        exams.append('12TH %')
        
    return ', '.join(exams)

df['accepted_exams'] = df.apply(get_exams, axis=1)

# Save back to DB and CSV
df.to_sql('colleges', conn, if_exists='replace', index=False)
df.to_csv('c:/Education_Counsellor/backend/data/colleges.csv', index=False)
conn.close()

print('Successfully migrated DB: Added accepted_exams column to all 991 rows!')
