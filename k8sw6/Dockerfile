FROM ubuntu:22.04

WORKDIR /app

# Install required packages for Python
RUN apt-get update && apt-get install -y python3 python3-pip build-essential wget

# Install network utils including trickle
RUN apt-get install -y iputils-ping dnsutils iproute2 iperf3 trickle

# Install grpcurl (add this line)
#RUN #apt-get install -y grpcurl
# Download and install grpcurl manually
RUN wget -qO /usr/local/bin/grpcurl https://github.com/fullstorydev/grpcurl/releases/download/v1.11.0/grpcurl_1.11.0_linux_x86_64 && chmod +x /usr/local/bin/grpcurl

# Add the 'testing' repository
#RUN echo "deb http://dl-cdn.alpinelinux.org/alpine/edge/testing main" >> /etc/apk/repositories && apk update

# Install grpcurl
#RUN apk add --no-cache grpcurl


# Install Python and necessary packages
RUN pip3 install --no-cache-dir grpcio grpcio-tools kubernetes iperf3

# Copy your application source code
COPY . /app

# Expose the port the app runs on (if applicable)
EXPOSE 5050

# Command to run the application
CMD ["python3", "node.py"]