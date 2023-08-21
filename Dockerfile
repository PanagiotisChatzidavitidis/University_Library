# Base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
#COPY requirements.txt .
RUN pip install flask
# Install the dependencies
RUN pip install Django
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pymongo
# Copy the Flask application code
#COPY . .
COPY app.py .
COPY templates templates

# Expose port 5000
EXPOSE 5000

# Set the environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
# Run the Flask application
CMD ["flask", "run"]