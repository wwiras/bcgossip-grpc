# Set up the base YAML template with the correct placeholders
template_yaml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bcgossip{nodes}nodes{memory}mi
spec:
  selector:
    matchLabels:
      run: bcgossip
  replicas: {nodes}
  template:
    metadata:
      labels:
        run: bcgossip
    spec:
      containers:
      - name: bcgossip-cont
        image: wwiras/bcgossip-grpc:v15  # Replace with your actual Docker image
        ports:
        - containerPort: 5050
        resources:
          requests:
            memory: "{request_memory}Mi"
          limits:
            memory: "{limit_memory}Mi"
"""

# Define memory settings and node counts
memory_details = {
    "150": {"request": 120, "limit": 150},
    "300": {"request": 280, "limit": 300}
}

node_counts = [10, 30, 50, 70, 100, 150, 200, 400]

# Generate the YAML files
for mem_key, mem_values in memory_details.items():
    for count in node_counts:
        filename = f"deploy-{count}nodes-{mem_key}Mi.yaml"
        with open(filename, "w") as file:
            file_content = template_yaml.format(
                nodes=count,
                memory=mem_key,
                request_memory=mem_values["request"],
                limit_memory=mem_values["limit"]
            )
            file.write(file_content)
            print(f"Generated file: {filename}")

# Indicate completion
print("All files have been generated successfully.")
