FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && apt-get install -y python3.6 python3.6-dev python3-pip

RUN ln -sfn /usr/bin/python3.6 /usr/bin/python3 && ln -sfn /usr/bin/python3 /usr/bin/python && ln -sfn /usr/bin/pip3 /usr/bin/pip

RUN apt-get update && apt-get install -y \
    curl \
    git

COPY requirements.txt /

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


COPY . /app

WORKDIR /app

# Install the gRPC files for lnd.
RUN git clone https://github.com/googleapis/googleapis.git
RUN curl -o rpc.proto -s https://raw.githubusercontent.com/lightningnetwork/lnd/master/lnrpc/rpc.proto
RUN mv rpc.proto squeakclient/
RUN ls .
RUN ls squeakclient
RUN python -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. squeakclient/rpc.proto
# RUN cp rpc_pb2.py /app
# RUN cp rpc_pb2_grpc.py /app
# RUN touch __init__.py

RUN python setup.py install

# Copy the entrypoint script.
COPY "docker/sqk/start-sqk.sh" .
COPY "docker/sqk/start-sqkctl.sh" .
RUN chmod +x start-sqk.sh
RUN chmod +x start-sqkctl.sh
