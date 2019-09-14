FROM python:3.5.7-slim-stretch

RUN apt-get update && apt-get install -y mc

RUN pip install redial
