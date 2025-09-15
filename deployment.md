
# Deployment Guide - AI Sentiment Analysis API on EKS

## Step 1: Setup Local Environment
```bash
# Clone the repository
git clone https://github.com/yourusername/sentiment-api.git
cd sentiment-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
````

## Step 2: Create ECR Repository

```bash
# Create ECR repository
aws ecr create-repository --repository-name sentiment-api --region us-east-1

# Note the repository URI from output
```

## Step 3: Build and Push Docker Image

```bash
# Build Docker image
docker build -t sentiment-api .

# Authenticate Docker with ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag and push image
docker tag sentiment-api:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/sentiment-api:v1.0
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/sentiment-api:v1.0
```

## Step 4: Configure Helm Chart

```bash
# Update sentiment-api-chart/values.yaml with your ECR repository URL
# Replace YOUR_ACCOUNT_ID with your actual AWS account ID
image:
  repository: YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/sentiment-api
  tag: v1.0
  pullPolicy: IfNotPresent
```

## Step 5: Deploy to EKS

```bash
# Ensure your EKS cluster has worker nodes
kubectl get nodes

# If no nodes, create a node group
eksctl create nodegroup \
  --cluster=your-cluster-name \
  --region=us-east-1 \
  --name=worker-nodes \
  --node-type=t3.medium \
  --nodes=2 \
  --nodes-min=1 \
  --nodes-max=4

# Deploy with Helm
helm install sentiment-api ./sentiment-api-chart --namespace default

# Monitor deployment
kubectl get pods -w
kubectl get svc sentiment-api
```

## Step 6: Test the API

```bash
# Get the LoadBalancer external IP
kubectl get svc sentiment-api

# Test basic endpoint
curl http://[EXTERNAL-IP]/

# Test health check
curl http://[EXTERNAL-IP]/health

# Test sentiment analysis
curl -X POST http://[EXTERNAL-IP]/analyze \
-H "Content-Type: application/json" \
-d '{"text": "I love this new AI model! It works amazingly well."}'

# Test batch processing
curl -X POST http://[EXTERNAL-IP]/batch \
-H "Content-Type: application/json" \
-d '{
  "texts": [
    "This movie is fantastic!",
    "I really dislike this product.",
    "The weather is okay today."
  ]
}'
```

## Step 7: Monitor and Scale

```bash
# Check pod status
kubectl get pods
kubectl top pods

# Monitor autoscaling
kubectl get hpa
kubectl get hpa -w

# View logs
kubectl logs -f deployment/sentiment-api

# Manual scaling (if needed)
kubectl scale deployment sentiment-api --replicas=4
```

## Step 8: Rolling Updates

```bash
# Build new version
docker build -t sentiment-api:v2.0 .
docker tag sentiment-api:v2.0 YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/sentiment-api:v2.0
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/sentiment-api:v2.0

# Deploy update
helm upgrade sentiment-api ./sentiment-api-chart --set image.tag=v2.0

# Monitor rollout
kubectl rollout status deployment/sentiment-api
```

## Troubleshooting

```bash
# If pods stuck in Pending
kubectl describe pod [POD-NAME]
kubectl get nodes
kubectl describe nodes

# If service not found
helm list
kubectl get all -l app=sentiment-api
helm get manifest sentiment-api

# If image pull errors
aws ecr describe-repositories
kubectl describe pod [POD-NAME]

# Check resource usage
kubectl top pods
kubectl top nodes
```

## Cleanup

```bash
# Remove deployment
helm uninstall sentiment-api

# Delete ECR repository
aws ecr delete-repository --repository-name sentiment-api --force

# Optional: Delete EKS cluster
# eksctl delete cluster --name your-cluster-name
```

```
```
