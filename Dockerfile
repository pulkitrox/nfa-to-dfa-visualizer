FROM python:3.11-slim

# Install graphviz
RUN apt-get update && apt-get install -y graphviz

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 10000

# Run app
CMD ["python", "backend/app.py"]