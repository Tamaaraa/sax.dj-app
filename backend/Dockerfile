FROM python:alpine

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY backend/.env .

EXPOSE 5000

CMD ["python", "app.py"]