FROM python:3.9-slim-buster

COPY ./requirements.txt requirements.txt

WORKDIR /src

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]