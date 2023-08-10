FROM python:3.10.6
RUN apt update -y
RUN apt upgrade -y
RUN mkdir /DigitalAirlinesService

ADD . /unipiLibrary
WORKDIR /unipiLibrary

COPY requirements.txt .
COPY app.py .

ADD templates ./templates

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "-u", "app.py" ]