FROM python:3.9-slim-bullseye

# forces the stdout and stderr streams to be unbuffered
ENV PYTHONUNBUFFERED True

WORKDIR /cy-genai

COPY ./libs /cy-genai/libs
COPY ./certs /cy-genai/certs
COPY ./cygenai-docker.json /cy-genai/cygenai.json