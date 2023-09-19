FROM python:3.10.6
RUN apt update -y
RUN apt upgrade -y
RUN mkdir /unipiLibrary

WORKDIR /unipiLibrary

COPY requirements.txt .
COPY app.py .
COPY users.json .
COPY books.json .
COPY reservedbooks.json .

ADD templates ./templates
ADD static ./static
ADD pymethods ./pymethods

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "-u", "app.py" ]