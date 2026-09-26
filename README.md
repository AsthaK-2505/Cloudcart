# CloudCart – Cloud-Native E-Commerce Platform

CloudCart is a cloud-native e-commerce application that I built as a DevOps learning project.

The main purpose of this project was to understand how a real application can be divided into multiple services and then containerized, deployed, monitored, and managed using DevOps tools.

Instead of keeping everything in one application, CloudCart uses separate services for users, products, orders, payments, and notifications.

---

## What the project does

CloudCart provides a simple e-commerce backend where users can:

* View products
* View users
* Create orders
* View existing orders
* Process mock payments
* Generate order notifications

The application is divided into multiple microservices and communicates between services through the API Gateway.

RabbitMQ is used for asynchronous order notifications, while Redis is used for product caching.

---

## Architecture

The basic request flow looks like this:

```text
                         GitHub
                           |
                      GitHub Actions
                       CI / CD
                           |
                           v
                         GHCR
                    Docker Images
                           |
                           v
                    Kubernetes
                     / Minikube
                           |
                    API Gateway
                       :5000
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
     User Service     Product Service   Order Service
        :5001             :5002            :5003
          |                  |                |
          |                  |                +------> PostgreSQL
          |                  |
          |                  +------> Redis
          |
          |
          +----------------------------+
                                       |
                                       v
                                   PostgreSQL


Order Service
      |
      v
   RabbitMQ
      |
      v
Notification Service
      :5005


Payment Service
      :5004
```

The complete application runs inside Kubernetes.

Prometheus and Grafana are used for monitoring, while Kubernetes HPA is used to automatically scale the API Gateway based on CPU usage.

---

## Services

| Service              |  Port | Purpose                              |
| -------------------- | ----: | ------------------------------------ |
| API Gateway          |  5000 | Main entry point for the application |
| User Service         |  5001 | Handles users                        |
| Product Service      |  5002 | Handles products and Redis caching   |
| Order Service        |  5003 | Creates and retrieves orders         |
| Payment Service      |  5004 | Mock payment processing              |
| Notification Service |  5005 | Processes order notifications        |
| PostgreSQL           |  5432 | Main database                        |
| Redis                |  6379 | Product caching                      |
| RabbitMQ             |  5672 | Message broker                       |
| RabbitMQ Management  | 15672 | RabbitMQ web interface               |

---

## Technologies Used

### Application

* Python
* Flask
* PostgreSQL
* Redis
* RabbitMQ

### Containers

* Docker
* Docker Compose

### Kubernetes

* Kubernetes
* Minikube
* Kubernetes Deployments
* Services
* ConfigMaps
* Secrets
* PersistentVolumeClaims
* Liveness probes
* Readiness probes
* Rolling updates
* Horizontal Pod Autoscaler

### DevOps

* Git
* GitHub
* GitHub Actions
* GitHub Container Registry (GHCR)
* Helm

### Monitoring

* Prometheus
* Grafana

### Testing

* Pytest
* Flask test client
* Mocked service calls

---

# Running the project locally with Docker Compose

Clone the repository:

```bash
git clone https://github.com/AsthaK-2505/Cloudcart.git
cd Cloudcart
```

Start all services:

```bash
docker compose up -d --build
```

Check running containers:

```bash
docker compose ps
```

The API Gateway is available at:

```text
http://localhost:5000
```

Some useful endpoints:

```text
GET  /health
GET  /users
GET  /products
GET  /orders
POST /orders
```

For example:

```bash
curl http://localhost:5000/health
```

---

# RabbitMQ

RabbitMQ Management UI is available at:

```text
http://localhost:15672
```

Default local credentials:

```text
Username: guest
Password: guest
```

The Order Service publishes order events to RabbitMQ.

The Notification Service consumes those events.

This allows notification processing to happen asynchronously instead of making the order request wait for the notification service.

---

# Running automated tests

The project contains automated tests for the API Gateway.

Create the test environment:

```bash
python3 -m venv .venv-test
```

Activate it:

```bash
source .venv-test/bin/activate
```

Install the dependencies:

```bash
pip install -r api-gateway/requirements.txt
pip install -r tests/requirements.txt
```

Run the tests:

```bash
pytest -v tests/
```

Current test coverage includes:

* API Gateway home endpoint
* Health endpoint
* Product endpoint
* User endpoint
* Get orders
* Create orders

The tests use mocked downstream services, so the complete application stack does not need to be running for these tests.

---

# CI Pipeline

GitHub Actions is used to automate the CI process.

Whenever code is pushed to the `main` branch, the pipeline first runs the automated tests.

Only when the tests pass does the pipeline continue to build and push Docker images.

```text
Git Push
   |
   v
Run Tests
   |
   |---- Failed ----> Pipeline stops
   |
   v
Build Docker Images
   |
   v
Push Images to GHCR
```

Six application images are built:

```text
cloudcart-api-gateway
cloudcart-user-service
cloudcart-product-service
cloudcart-order-service
cloudcart-payment-service
cloudcart-notification-service
```

Images are tagged using both:

```text
latest
```

and the Git commit SHA.

---

# Kubernetes Deployment

CloudCart can also be deployed to a local Kubernetes cluster using Minikube.

Start Minikube:

```bash
minikube start --driver=docker
```

The project contains Kubernetes manifests inside:

```text
k8s/
```

The Kubernetes configuration includes:

```text
Deployments
Services
ConfigMap
Secret
PostgreSQL
Redis
RabbitMQ
PersistentVolumeClaim
HPA
Database initialization Job
```

Check the resources:

```bash
kubectl get pods
```

```bash
kubectl get services
```

---

# Helm Deployment

The project also contains a Helm chart:

```text
helm/
```

CloudCart can be deployed using:

```bash
helm upgrade --install cloudcart ./helm \
  -n cloudcart \
  --create-namespace
```

The Helm chart makes it easier to manage the application as a single deployment instead of manually applying each Kubernetes manifest.

---

# Horizontal Pod Autoscaling

The API Gateway is configured with a Horizontal Pod Autoscaler.

The configured behavior is:

```text
Minimum replicas: 2
Maximum replicas: 3
CPU target: 70%
```

During testing, CPU load was generated against the API Gateway.

The number of replicas increased from:

```text
2 → 3
```

After the load was stopped, Kubernetes was able to reduce the replicas again.

This was used to verify that the HPA configuration was actually working rather than just having the YAML configuration present.

---

# Monitoring

Prometheus and Grafana are deployed in the Kubernetes cluster using the `kube-prometheus-stack`.

Prometheus collects Kubernetes and application-related metrics.

Grafana is used to visualize the metrics.

Grafana can be accessed locally using:

```bash
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
```

Then open:

```text
http://localhost:3000
```

Grafana credentials can be retrieved from the Kubernetes secret.

---

# Kubernetes Self-Healing

One of the Kubernetes features tested in this project is self-healing.

If a running application pod is deleted, Kubernetes detects that the desired number of replicas is no longer available and creates a replacement pod.

For example:

```bash
kubectl delete pod <pod-name>
```

Then:

```bash
kubectl get pods
```

A replacement pod is created automatically.

This demonstrates the difference between simply running containers and managing them through Kubernetes.

---

# CI/CD Flow

The overall DevOps workflow used in this project is:

```text
Developer
    |
    v
GitHub
    |
    v
GitHub Actions
    |
    +----> Automated Tests
    |
    +----> Docker Build
    |
    v
GHCR
    |
    v
Helm
    |
    v
Kubernetes / Minikube
    |
    +----> HPA
    |
    +----> Self Healing
    |
    +----> Rolling Updates
    |
    v
Prometheus
    |
    v
Grafana
```

The CD workflow can deploy the application to the local Kubernetes cluster using a self-hosted GitHub Actions runner.

---

# Project Structure

```text
Cloudcart/
│
├── api-gateway/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── user-service/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── product-service/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── order-service/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── payment-service/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── notification-service/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── tests/
│   ├── test_services.py
│   └── requirements.txt
│
├── k8s/
│   ├── deployments
│   ├── services
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── hpa.yaml
│   └── ...
│
├── helm/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
│
├── docker-compose.yml
└── .gitignore
```

---

# What I learned from this project

This project helped me understand how different DevOps tools fit together instead of learning each tool separately.

Some of the main things I practiced were:

* Creating and containerizing microservices
* Connecting containers using Docker Compose
* Working with PostgreSQL, Redis and RabbitMQ
* Creating Kubernetes deployments and services
* Managing configuration using ConfigMaps and Secrets
* Using persistent storage in Kubernetes
* Creating Helm charts
* Building Docker images automatically with GitHub Actions
* Publishing images to GHCR
* Running automated tests in CI
* Deploying applications to Kubernetes
* Using HPA for automatic scaling
* Testing Kubernetes self-healing
* Monitoring Kubernetes using Prometheus and Grafana

---

# Future Improvements

Some possible improvements for a future version of the project could be:

* Add a frontend application
* Add authentication and authorization
* Add real payment integration
* Deploy the application to a cloud provider
* Add more automated tests
* Add centralized logging

These were intentionally kept outside the current scope so that the project could remain manageable while still covering the main DevOps workflow.

---


GitHub:

https://github.com/AsthaK-2505

Project:

https://github.com/AsthaK-2505/Cloudcart
