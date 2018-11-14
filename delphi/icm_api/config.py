from pathlib import Path

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os

BASE_DIR = Path(__file__).parent

# Define the database - we are working with
# SQLite for this example
#SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR}/delphi.db"
# Uncomment this line for testing
SQLALCHEMY_DATABASE_URI = f"sqlite:////tmp/test.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_CONNECT_OPTIONS = {}
# Following two lines are addedd to execute Celery Background Tasks
CELERY_BROKER_URL = 'pyamqp://localhost//'
#Uncomment this line for normal run
#CELERY_RESULT_BACKEND = f"db+sqlite:///{BASE_DIR}/delphi.sqlite"
#Uncomment this line for testing
CELERY_RESULT_BACKEND = 'db+sqlite:////tmp/test.sqlite'
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['pickle']
# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2
