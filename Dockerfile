FROM python:3.6-slim-stretch

ENV APP_DIR='/app'
WORKDIR APP_DIR
ENV PYTHONPATH=$APP_DIR:$PYTHONPATH

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "trademark_monitor.py"]