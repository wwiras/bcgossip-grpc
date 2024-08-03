FROM busybox:latest

WORKDIR /app

# Install required packages for Python (musl is for compatibility with Alpine's libraries)
RUN apk add --no-cache --virtual .build-deps \
    bash \             # Bash for better scripting
    wget \
    musl-dev \
    gcc

# Download and install Python
RUN wget https://www.python.org/ftp/python/3.11.5/Python-3.11.5.tgz 
RUN tar -xf Python-3.11.5.tgz
WORKDIR /app/Python-3.11.5
RUN ./configure --enable-optimizations && \
    make altinstall  

# Install network utils
RUN apk add --no-cache iputils dnsutils

# Create a symbolic link for 'python3'
RUN ln -s /usr/local/bin/python3.11 /usr/bin/python3

# Install Python and necessary packages
RUN pip install --no-cache-dir grpcio grpcio-tools kubernetes

# Copy your application source code
COPY . /app

# Expose the port the app runs on (if applicable)
# EXPOSE 5050

# Command to run the application
CMD ["python3", "node2.py"]
