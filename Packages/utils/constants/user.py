import os
import json


user_home_dir = os.path.expanduser("~")
pipezer_dir = os.path.join(user_home_dir, '.pipezer')
user_file_path = os.path.join(pipezer_dir, 'user.json')

if os.path.exists(user_file_path):
    with open(user_file_path, 'r') as user_file:
        data = json.load(user_file)
        USERNAME = data.get("username",
                                os.getenv("USERNAME"))  # Si non défini, utiliser le nom de session par défaut
else:
    USERNAME = os.getenv("USERNAME")
USER_DIR = os.path.expanduser("~")
