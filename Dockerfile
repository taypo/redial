FROM python:3.5.7-slim-stretch

RUN apt-get update && apt-get install -y mc && rm -rf /var/cache/apk/*

RUN pip --no-cache-dir install redial
