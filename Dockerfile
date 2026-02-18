FROM python:3.11-slim

WORKDIR /app
RUN mkdir -p /srv/sharespace
ENV DATABASE_URL=sqlite:////srv/sharespace/sharespace.db
VOLUME ["/srv/sharespace"]
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000

CMD python create_db.py && python -m flask -A project/app.py run --host=0.0.0.0 --port=8000
