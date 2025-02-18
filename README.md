# trading-platform

python3 -m venv venv

source venv/bin/activate 

pip install -r requirements.txt

flask db init

flask db migrate -m "Initial migration"

flask db upgrade

psql -U postgres -d trading_db -c "\dt"

python -m app.server

pytest