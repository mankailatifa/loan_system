Loan Processing System – Microservices with Kubernetes
Overview

This project implements a Loan Processing System using a microservices architecture deployed on Kubernetes.

The application allows users to submit loan requests, compute a credit score, and determine whether the loan should be approved or rejected.

The services communicate asynchronously using RabbitMQ and Celery, while PostgreSQL is used for data storage.

Architecture

The system contains the following microservices:

1️⃣ Loan Service

Main entry point of the application.

Responsibilities:

Provides an API and HTML form to submit loan requests

Stores loan information in the database

Sends a task to compute the credit score

Technologies:

FastAPI

PostgreSQL

Celery

RabbitMQ

2️⃣ Credit Score Service

Computes the client's credit score asynchronously.

Responsibilities:

Receives tasks from RabbitMQ

Reads financial information

Computes the credit score

Updates the loan database

Credit score formula:

score = 1000 - 0.1 * debt - 50 * latePayments - (200 if hasBankruptcy else 0)


Technologies:

Celery Worker

RabbitMQ

Redis

PostgreSQL

3️⃣ Solvency Decision Service

Determines whether the loan is approved.

Decision rule example:

if score > 600 and monthlyIncome > monthlyExpenses:
    decision = APPROVED
else:
    decision = REJECTED


Technologies:

FastAPI

System Architecture
                +-------------------+
                |       User        |
                +---------+---------+
                          |
                          ▼
                 +------------------+
                 |   Loan Service   |
                 |     (FastAPI)    |
                 +--------+---------+
                          |
                          | Celery Task
                          ▼
                    +------------+
                    | RabbitMQ   |
                    +------+-----+
                           |
                           ▼
               +----------------------+
               | Credit Score Worker  |
               |      (Celery)        |
               +----------+-----------+
                          |
                          ▼
                    +-----------+
                    |PostgreSQL |
                    +-----------+
                          |
                          ▼
               +----------------------+
               | Solvency Decision    |
               |      Service         |
               +----------------------+

Technologies Used

FastAPI

Celery

RabbitMQ

Redis

PostgreSQL

Docker

Kubernetes

Project Structure
loan-system/

│
├── loan-service/
│   ├── app/
│   │   ├── main.py
│   │   └── form.html
│   └── Dockerfile
│
├── credit-score/
│   ├── app/
│   │   └── tasks.py
│   └── Dockerfile
│
├── solvency-decision/
│   ├── app/
│   │   └── main.py
│   └── Dockerfile
│
├── k8s/
│   ├── postgres-deployment.yaml
│   ├── postgres-service.yaml
│   ├── rabbitmq-deployment.yaml
│   ├── rabbitmq-service.yaml
│   ├── redis-deployment.yaml
│   ├── redis-service.yaml
│   ├── loan-service-deployment.yaml
│   ├── loan-service-service.yaml
│   ├── credit-worker-deployment.yaml
│   ├── solvency-service-deployment.yaml
│   └── solvency-service.yaml
│
└── README.md

Kubernetes Deployment
1️⃣ Build Docker Images

Build the images locally:

docker build -t loan-service ./loan-service
docker build -t credit-service ./credit-score
docker build -t decision-service ./solvency-decision

2️⃣ Start Kubernetes

If using Docker Desktop:

Enable Kubernetes


Check cluster:

kubectl get nodes

3️⃣ Deploy Infrastructure Services

Deploy databases and message broker:

kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/rabbitmq-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml


Check pods:

kubectl get pods

4️⃣ Deploy Microservices
kubectl apply -f k8s/loan-service-deployment.yaml
kubectl apply -f k8s/credit-worker-deployment.yaml
kubectl apply -f k8s/solvency-service-deployment.yaml

5️⃣ Verify Services

List services:

kubectl get services


Example output:

loan-service       NodePort
solvency-service   NodePort
postgres           ClusterIP
rabbitmq           ClusterIP

Access the Application

Open the Loan Service:

http://localhost:<NodePort>/form


Example:

http://localhost:30007/form

Debugging

View logs:

kubectl logs <pod-name>


Example:

kubectl logs credit-worker-xxxxx


Enter a container:

kubectl exec -it <pod-name> -- /bin/bash

Useful Commands

Check pods:

kubectl get pods


Check services:

kubectl get svc


Delete deployment:

kubectl delete -f k8s/
