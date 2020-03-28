# Dockerfile
FROM python:3.7-slim
ENV APP_HOME /app
ENV FLASK_APP run.py
WORKDIR ${APP_HOME}
COPY . ./
RUN pip3 install -r requirements.txt
CMD exec gunicorn --bind :$PORT --workers 3 run:app
