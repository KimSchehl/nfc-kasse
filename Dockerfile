FROM python:3.12-slim

WORKDIR /app

# Kopiere nur die notwendigen Dateien
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Datenbank initialisieren (optional, falls noch nicht vorhanden)
RUN python init_db.py

# Ask user if he wants default data
ARG DEFAULT_DATA
RUN if [ "$DEFAULT_DATA" = "yes" ] || [ "$DEFAULT_DATA" = "y" ]; then python testData.py; fi

EXPOSE 5000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]