FROM python:3.8-slim

RUN apt-get update && apt-get install

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./
ENV PYTHONPATH=${PYTHONPATH}:`pwd`

CMD ["python3", "trademark_monitor.py"]