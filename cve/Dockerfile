FROM --platform=linux/amd64 python:3.9-slim-buster

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .