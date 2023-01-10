FROM python:3.8

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the code for the service
COPY . .

# Run the service when the container starts
CMD ["python", "app.py"]
