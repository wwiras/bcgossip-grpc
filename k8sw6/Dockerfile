FROM ubuntu:22.04

WORKDIR /app

# Install required packages for Python
RUN apt-get update && apt-get install -y python3 python3-pip build-essential wget curl unzip

#sudo apt install golang-go
# Download and install grpcurl
RUN curl -sSL https://github.com/fullstorydev/grpcurl/releases/download/v1.8.7/grpcurl_1.8.7_linux_x86_64.tar.gz -o grpcurl.tar.gz \
    && tar -xzf grpcurl.tar.gz \
    && mv grpcurl /usr/local/bin/grpcurl \
    && rm grpcurl.tar.gz

# Install network utils including trickle
RUN apt-get install -y iputils-ping dnsutils iproute2 iperf3 trickle

# Install grpcurl using Go
#RUN go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# Install Python and necessary packages
RUN pip3 install --no-cache-dir grpcio grpcio-tools kubernetes iperf3 grpcio-reflection

# Copy your application source code
COPY . /app

# Expose the port the app runs on (if applicable)
EXPOSE 5050

# Command to run the application
CMD ["python3", "node.py"]

#trickle -s -d 125 -u 125 grpcurl -plaintext -proto gossip.proto -d '{"message": "testgrpcurldirect", "sender_id": "gossip-statefulset-0", "timestamp": 1234567890}' 10.44.1.17:5050 gossip.GossipService/SendMessage