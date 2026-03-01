# # Use official Python runtime as base image
# FROM python:3.11-slim

# # Set working directory in container
# WORKDIR /app

# # Copy requirements file
# COPY requirements.txt .

# # Install dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy application code
# COPY . .

# # Expose the port Flask runs on
# EXPOSE 5000

# # Set environment variables
# ENV FLASK_APP=run.py
# ENV FLASK_ENV=production

# # Run the application
# CMD ["python", "run.py"]


FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "run.py"]