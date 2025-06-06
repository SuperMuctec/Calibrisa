python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

touch databases/users.db

touch .env

python3 setup.py

python3 main.py

chmod +x run.sh