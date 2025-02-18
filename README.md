# Trading Platform

---

**## **🚀 Getting Started****

### **1️⃣ Clone the Repository**
```sh
git clone https://github.com/Yogeshjadaun/trading-platform.git
cd trading-platform
```


### **2️⃣ Setup using Docker**
#### To start and build:
```sh
docker-compose up --build -d
```
#### To check logs:
```sh
docker-compose logs -f
```
#### To stop:
```sh
docker-compose down
```
#### To run tests:
```sh
docker-compose run --rm web pytest --disable-warnings -s -v
```
#### To run the application:
```sh
docker-compose up
```
#### To check the application:
```sh
curl http://localhost:5000/health
```

## Or


### **2️⃣ Setup Virtual Environment & Install Dependencies**
```sh
python3 -m venv venv
source venv/bin/activate 

pip install -r requirements.txt
```

### **3️⃣ Configure the Environment Variables**

Create or update `.env` file in the root directory and define database and other environment variables:
```ini
DATABASE_URL=postgresql://postgres:postgres@localhost/trading_db
REDIS_URL=redis://localhost:6379/0
BROKER_URL=redis://localhost:6379/0
```

---

## **📌 Database Setup**

### **4️⃣ Initialize & Apply Migrations**

PostgreSQL is required for the database. Make sure you have **PostgreSQL running** and create the database:
```sh
psql -U postgres -c "CREATE DATABASE trading_db;"
```

Now, apply migrations to create tables and indexes:
```sh
export FLASK_APP=app.server
flask db upgrade
```

To verify the database tables are created:
```sh
psql -U postgres -d trading_db -c "\dt"
```

This will list all tables in the `trading_db` database.

---

## **🛠 Running the Application**

### **5️⃣ Start the Flask Application**
Run the backend API server:
```sh
python -m app.server
```

---

## **🧪 Running Tests**

To run all test cases:
```sh
pytest
```

The test setup uses **SQLite in-memory database** for faster execution.

---

## ** Background Task Processing & Reporting**

### **6️⃣ Start Celery Worker**
Celery is used for background task execution, such as refreshing materialized views.
```sh
celery -A app.server.celery worker --loglevel=info
```

### **7️⃣ Start Celery Beat (Task Scheduler)**
Celery Beat is used to **schedule periodic background tasks**, such as updating trade reports.
```sh
celery -A app.server.celery beat --loglevel=info
```


## **📌 To-Do & Future Enhancements**
✅ Implement Trading Engine to Apply validation Rules  
✅ Add Centralized Logging & Exception Handling  
✅ Setup Linting, Code coverage for Code Quality  
✅ Improve Deployment Pipeline (Docker & Kubernetes)  
✅ Increase Test Coverage with More Edge Cases  
✅ Enhance API Documentation  

---
