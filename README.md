# trading-platform

git clone https://github.com/Yogeshjadaun/trading-platform.git

cd trading-platform

python3 -m venv venv

source venv/bin/activate 

pip install -r requirements.txt

[//]: # (flask db init)

[//]: # ()
[//]: # (flask db migrate -m "Initial migration")

export FLASK_APP=app.server    

flask db upgrade

psql -U postgres -d trading_db -c "\dt"

python -m app.server

pytest

celery -A app.server.celery worker --loglevel=info

celery -A app.server.celery beat --loglevel=info

