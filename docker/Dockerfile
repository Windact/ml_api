FROM python:3.8.5

RUN mkdir -p /opt/app

# Defining an non persisted env variable for our package
ENV PIP_EXTRA_INDEX_URL=${PIP_EXTRA_INDEX_URL}

COPY requirements.txt /opt/app/requirements.txt
RUN pip install --upgrade pip

# ensure we can run the make commands
RUN apt-get update -y && \
 	apt-get install -y make && \
 	apt-get install -y libffi-dev gcc && \
 	# for swagger
 	apt-get install -y curl
	# for postgres driver
RUN	apt-get install -y libpq-dev

RUN pip install -r /opt/app/requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/opt/app/"
COPY Makefile /opt/app/Makefile
ADD . /opt/app
WORKDIR /opt/app
