FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
	python3-pip \
	curl \
	git

COPY requirements.txt /

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

RUN git clone https://github.com/googleapis/googleapis.git

Run mkdir /app
COPY ./squeakclient/squeaknode/rpc/route_guide.proto /app
RUN cp -r googleapis /app

WORKDIR /app

RUN python3 -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. route_guide.proto

# Copy the entrypoint script.
COPY "itests/test.sh" .
COPY "itests/test.py" .
RUN chmod +x test.sh

CMD ["bash", "test.sh"]
