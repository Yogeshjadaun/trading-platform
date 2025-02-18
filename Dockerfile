# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application into the container
COPY . .

# Set environment variables
ENV FLASK_APP=app.server
ENV FLASK_ENV=production
ENV DATABASE_URL=postgresql://postgres:postgres@db:5432/trading_db
ENV REDIS_URL=redis://redis:6379/0
ENV CELERY_BROKER_URL=redis://redis:6379/0
ENV CELERY_RESULT_BACKEND=redis://redis:6379/0

# Expose port 5000 for Flask
EXPOSE 5000

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
