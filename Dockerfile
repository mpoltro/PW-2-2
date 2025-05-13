FROM python:3.9-slim


RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

COPY wait-for-mysql.sh /app/

# Rendi eseguibile lo script
RUN chmod +x /app/wait-for-mysql.sh

# Copy and install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the app
COPY . .

# Expose and run
EXPOSE 5000
CMD ["python", "app.py"]
