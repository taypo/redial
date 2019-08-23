FROM python:3.6

RUN apt-get update && apt-get install -y mc

RUN pip install redial
