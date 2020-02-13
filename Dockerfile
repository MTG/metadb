FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

ADD pip.conf /etc/pip.conf

ADD requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt
ADD requirements_dev.txt /code/
RUN pip install --no-cache-dir  -r requirements_dev.txt
ADD . /code/
