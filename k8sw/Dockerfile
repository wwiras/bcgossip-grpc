FROM python:3.9

WORKDIR /app

RUN pip install --no-cache-dir grpcio grpcio-tools

COPY . .

EXPOSE 50051

# Set the NODE_NAME to a default value. This will be overridden by the StatefulSet
#ENV NODE_NAME=node-0

CMD ["python", "gossip_server.py"]