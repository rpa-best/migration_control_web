FROM python:3.12.0-alpine
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/
RUN apk add --no-cache libev-dev libnss3 locales-all
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /app/
