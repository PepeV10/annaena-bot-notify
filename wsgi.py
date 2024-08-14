import sys
import os

# Add your project directory to the sys.path
project_home = '/home/PepeV10/annaena-bot-notify'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activate your virtual environment
activate_env = os.path.expanduser("/home/PepeV10/annaena-bot-notify/venv/bin/activate")
os.environ['VIRTUAL_ENV'] = activate_env
os.environ['PATH'] = os.path.join(activate_env, 'bin') + os.pathsep + os.environ['PATH']
os.environ['PYTHONHOME'] = activate_env

# Load the .env file
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

# Import the main Python file as an application
from annaena_bot_notify import main as application
