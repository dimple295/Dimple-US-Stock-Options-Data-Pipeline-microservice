helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
# helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set grafana.enabled=true \
  --set grafana.adminPassword=admin \
  --set prometheus.service.port=9090 \
  --set grafana.service.port=3000 \
  --set nodeExporter.service.port=9100

# # helm uninstall kafka
# helm install kafka bitnami/kafka \
#   --set kraft.enabled=false \
#   --set zookeeper.enabled=true \
#   --set zookeeper.replicaCount=1 \
#   --set broker.replicaCount=1 \
#   --set listeners.client.protocol=PLAINTEXT \
#   --set listeners.client.port=9092 \
#   --set autoCreateTopicsEnable=false \
#   --set controller.replicaCount=0 \
#   --version 26.9.0



# helm install nginx-ingress ingress-nginx/ingress-nginx \
#   --set controller.service.type=NodePort \
#   --set controller.publishService.enabled=true



