import pytest
import sqlite3
import os
import sys

# Add parent directory to sys path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import normalize_student_score, get_max_fee, get_colleges_from_db

def test_normalize_student_score_mht_cet():
    # MHT-CET score should not be modified
    assert normalize_student_score(92.5, "MHT-CET") == 92.5

def test_normalize_student_score_jee_mains():
    # JEE Mains score gets a slight penalty
    assert normalize_student_score(92.5, "JEE MAINS") == 91.5

def test_normalize_student_score_12th_percentage():
    # 12th Board % gets heavily penalized
    assert normalize_student_score(92.5, "12TH PERCENTAGE") == 77.5

def test_get_max_fee_open_category():
    # Standard budget scaling
    assert get_max_fee("<1L", category="Open") == 100000
    assert get_max_fee("3-8L", category="Open") == 800000

def test_get_max_fee_category_purchasing_power():
    # SC/ST gets 5x purchasing power
    assert get_max_fee("<1L", category="SC") == 500000
    assert get_max_fee("<1L", category="ST") == 500000
    # OBC gets 2x purchasing power
    assert get_max_fee("<1L", category="OBC") == 200000

def test_get_max_fee_maharashtra_women_tfws_policy():
    # Women in MH with <8L income get 8x purchasing power
    assert get_max_fee("<1L", category="Open", gender="Female", state="Maharashtra", income="<8L") == 800000
    # Women in MH with >8L income DO NOT get it
    assert get_max_fee("<1L", category="Open", gender="Female", state="Maharashtra", income=">8L") == 100000
    # Women OUTSIDE MH do not get it
    assert get_max_fee("<1L", category="Open", gender="Female", state="Delhi", income="<8L") == 100000

def test_get_max_fee_boys_tfws():
    # Boys in MH with <8L income also get 8x purchasing power for TFWS
    assert get_max_fee("<1L", category="Open", gender="Male", state="Maharashtra", income="<8L") == 800000
