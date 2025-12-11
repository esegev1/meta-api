# -----------------------------------------------------------------
# STAGE 1: Builder - Just for downloading dependencies
# -----------------------------------------------------------------
FROM python:3.11-slim as builder

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file
COPY requirements.txt .


# -----------------------------------------------------------------
# STAGE 2: Final Image - Copies app code and installs dependencies
# -----------------------------------------------------------------
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=server.py
# Set default port higher than 5000 as 5000 is common
ENV PORT=8000

# Set the working directory
WORKDIR /usr/src/app

# Copy requirements from the builder stage and install dependencies directly 
# This ensures gunicorn is installed correctly into the final environment's path
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the internal container port
EXPOSE ${PORT}

# Command to run the application using Gunicorn
# CMD gunicorn --bind 0.0.0.0:${PORT} server:app
CMD ["gunicorn", "--bind", "0.0.0.0:3001", "server:app"]
