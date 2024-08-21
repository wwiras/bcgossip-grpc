FROM ubuntu:22.04

WORKDIR /app

# Install required packages for Python
RUN apt-get update && apt-get install -y python3 python3-pip build-essential wget

# Install network utils including trickle
RUN apt-get install -y iputils-ping dnsutils iproute2 iperf3 trickle

# Install Go 1.21 (or any version >= 1.19)
RUN wget -qO go1.21.linux-amd64.tar.gz https://go.dev/dl/go1.21.linux-amd64.tar.gz && \
    rm -rf /usr/local/go && tar -C /usr/local -xzf go1.21.linux-amd64.tar.gz && \
    rm go1.21.linux-amd64.tar.gz

# Set GOPATH (adjust if needed)
ENV GOPATH=/go
ENV PATH=$PATH:/usr/local/go/bin # Add Go to PATH

# Install grpcurl using Go
RUN go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# Add Go bin directory to PATH (adjust if needed)
ENV PATH=$PATH:$GOPATH/bin

# Install Python and necessary packages
RUN pip3 install --no-cache-dir grpcio grpcio-tools kubernetes iperf3

# Copy your application source code
COPY . /app

# Expose the port the app runs on (if applicable)
EXPOSE 5050

# Command to run the application
CMD ["python3", "node.py"]