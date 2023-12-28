FROM python:3.12.0
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/
RUN apt-get update
RUN apt-get -y install libev-dev libnss3 locales-all
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /app/