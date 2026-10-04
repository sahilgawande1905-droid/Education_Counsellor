import urllib.request
import json
import urllib.error

# Test Recommendation Endpoint
data = json.dumps({'student_profile': {'name': 'TestUser', 'age': 18, 'stream': 'Engineering', 'marks': 92.5, 'exam_type': 'MHT-CET', 'preferred_state': 'Maharashtra', 'budget': '<8L', 'college_type': 'Government', 'category': 'OBC', 'family_income': '<8L'}}).encode('utf-8')
req = urllib.request.Request('http://127.0.0.1:8000/api/recommend', data=data, headers={'Content-Type': 'application/json'})

try:
    response = urllib.request.urlopen(req)
    res_data = json.loads(response.read())
    print('RECOMMENDATION TEST: SUCCESS')
    if res_data.get('colleges') and len(res_data['colleges']) > 0:
        c = res_data['colleges'][0]
        print('Sample College:', c.get('college_name'))
        print('CAP Strategy:', c.get('cap_strategy'))
        print('Safe Score:', c.get('target_2027_score'))
        print('Financial Aid:', c.get('financial_aid'))
    else:
        print('No colleges returned.')
except urllib.error.URLError as e:
    print('RECOMMENDATION TEST: FAILED - Connection Refused. Is the backend running?')
except Exception as e:
    print('RECOMMENDATION TEST: FAILED -', e)
