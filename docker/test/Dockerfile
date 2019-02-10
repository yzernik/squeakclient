FROM ubuntu:16.04

RUN apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && apt-get install -y python3.6 python3.6-dev python3-pip && \
    apt-get install -y expect

RUN ln -sfn /usr/bin/python3.6 /usr/bin/python3 && ln -sfn /usr/bin/python3 /usr/bin/python && ln -sfn /usr/bin/pip3 /usr/bin/pip

COPY requirements.txt /

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY src/ /app/src

WORKDIR /app

RUN python -m fbs freeze

# Copy the entrypoint script.
COPY "docker/sqk/start-sqk.sh" .
COPY "docker/sqk/start-sqkctl.sh" .
COPY "src/itests/test.sh" .
COPY "src/itests/sqk_ctl.exp" .
RUN chmod +x start-sqk.sh
RUN chmod +x start-sqkctl.sh
RUN chmod +x test.sh
RUN chmod +x sqk_ctl.exp

CMD ["bash", "test.sh"]
