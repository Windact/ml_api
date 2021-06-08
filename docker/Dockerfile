FROM python:3.8.5

RUN mkdir -p /opt/app

# Defining an non persisted env variable for our package
ARG PIP_EXTRA_INDEX_URL

COPY requirements.txt /opt/app/requirements.txt
RUN pip install --upgrade pip

# ensure we can run the make commands
RUN apt-get update -y && \
 	apt-get install -y make && \
 	apt-get install -y libffi-dev gcc && \
 	# for swagger
 	apt-get install -y curl

RUN pip install -r /opt/app/requirements.txt
COPY VERSION /opt/app/VERSION
COPY Makefile /opt/app/Makefile
COPY api /opt/app/api
COPY run.py /opt/app/run.py
WORKDIR /opt/app