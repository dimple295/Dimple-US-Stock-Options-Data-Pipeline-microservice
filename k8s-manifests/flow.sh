
cd script
chmod +x helm.sh
echo "Installing important pacakages"
./helm.sh
cd ../

echo "Deploying Kafka, Zookeeper and ingress"
sleep 30
kubectl apply -f manifest-azure

echo "Deploying microservices with frontend"
sleep 30
kubectl apply -f manifests

echo "Deploying service monitor of all microservices"
sleep 30
kubectl apply -f serviceMonitor