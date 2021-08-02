# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

RUN pip3 install requests
RUN pip3 install tinkerforge

COPY . .

CMD [ "python3", "modmaster.py"]