# Use your current Python version
FROM python:3.13.7-slim

# Set working directory
WORKDIR /app

# Copy all your code
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the default port for Hugging Face Spaces (7860)
EXPOSE 7860

# Run your backend app
# Change this line depending on your entry point
# If using FastAPI:
#CMD ["python", "backend/api/main.py"]
# If using Flask:
# CMD ["python", "backend/app.py"]
# If using Uvicorn directly:
CMD ["uvicorn", "backend.api.app:app", "--host", "0.0.0.0", "--port", "7860"]
