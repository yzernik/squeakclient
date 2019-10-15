FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
	python3-pip \
	curl \
	git

COPY requirements.txt /

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Install the gRPC files for lnd.
RUN git clone https://github.com/googleapis/googleapis.git
RUN curl -o rpc.proto -s https://raw.githubusercontent.com/lightningnetwork/lnd/master/lnrpc/rpc.proto

COPY . /app
RUN cp -r googleapis /app
RUN cp rpc.proto /app/squeakclient

WORKDIR /app

RUN python3 -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. squeakclient/rpc.proto
RUN python3 setup.py install

# Copy the entrypoint script.
COPY "docker/sqk/start-sqk.sh" .
COPY "docker/sqk/start-sqkctl.sh" .
RUN chmod +x start-sqk.sh
RUN chmod +x start-sqkctl.sh
