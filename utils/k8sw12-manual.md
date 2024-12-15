# Run helm chart in k8s
````
helm install gossip-statefulset k8sw10-chart/ --values k8sw10-chart/values.yaml --debug --set speed=10M --set image.tag=v4
helm install gossip-statefulset chartw/ --values chartw/values.yaml --debug
helm install gossip-statefulset chartw/ --values k8sw10-chart/values.yaml --debug --set image.name=k8sw12 --set image.tag=v1
helm install gossip-statefulset k8sw11-chart-fix/ --values k8sw11-chart-fix/values.yaml --debug
helm install gossip-statefulset chartw/ --values chartw/values.yaml --debug --set image.name=wwiras/k8sw12 --set image.tag=v1
helm install gossip-statefulset chartw/ --values chartw/values.yaml --debug
```


# run docker in k8s
```
docker build -t wwiras/k8sw12:v1 .
docker push wwiras/k8sw12:v1
```


# logs in k8s
```
kubectl logs gossip-statefulset-0
```

# accessing the terminal (old command)
```
kubectl exec -it gossip-statefulset-0 sh
```

# accessing the terminal (new command)
```
kubectl exec -it gossip-statefulset-0 -- sh
```

# Google BigQuery Commmand
```
SELECT jsonPayload.sender_id,jsonPayload.receiver_id, jsonPayload.message, jsonPayload.event_type , jsonPayload.received_timestamp, jsonPayload.propagation_time,jsonPayload.latency_ms, jsonPayload.detail 
FROM `bcgossip-proj.gossip_simulation.stdout` 
-- WHERE TIMESTAMP_TRUNC(timestamp, DAY) = TIMESTAMP("2024-12-14")
WHERE TIMESTAMP_TRUNC(timestamp, DAY) = TIMESTAMP("2024-12-15")
-- AND jsonPayload.message like '%latency_15Dec202408%'
-- AND jsonPayload.message like '%latency_Dec1420241557%'
AND jsonPayload.message like '%latency_Dec152024%'
 LIMIT 1000
```