FROM python:3.10.12
WORKDIR /app

COPY requirements/requirements_prod.txt /app/requirements.txt
RUN pip install --upgrade pip -r /app/requirements.txt

COPY . /app
