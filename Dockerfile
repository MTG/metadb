FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64 && chmod +x /usr/local/bin/dumb-init

RUN mkdir /code
WORKDIR /code

ADD pip.conf /etc/pip.conf

ADD requirements.lock /code/
RUN pip install -r requirements.lock
ADD requirements_dev /code/
RUN pip install  -r requirements_dev
ADD . /code/
