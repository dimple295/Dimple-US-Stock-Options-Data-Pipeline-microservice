# delete old cluster
kind delete cluster --name stock-cluster

# creating Cluster
echo "Creating Cluster: stock-cluster"
kind create cluster --config cluster/kind-config.yaml 
echo "stock-cluster Created"

# update helm package and load images
cd script
chmod +x helm.sh
chmod +x load_image.sh
./helm.sh
./load_image.sh
cd ..

# apply manifest
kubectl apply -f manifests