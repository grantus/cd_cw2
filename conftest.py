# conftest.py
import sys, os

ROOT = os.path.dirname(__file__)
# so that `from app import app` in file_store/tests will pick file_store/app.py:
sys.path.insert(0, os.path.join(ROOT, 'file_store'))
# likewise for analysis and gateway
sys.path.insert(0, os.path.join(ROOT, 'analysis'))
sys.path.insert(0, os.path.join(ROOT, 'gateway'))
