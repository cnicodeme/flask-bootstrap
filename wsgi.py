import sys
from main import app_factory

sys.path.append('/var/www/agentp.cc/api/')
app = app_factory()
