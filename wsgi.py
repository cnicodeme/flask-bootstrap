import sys, os
from main import app_factory

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
app = app_factory()
