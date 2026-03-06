# 🏦 BankFlow : Système de Gestion de Prêt Immobilier

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688)
![Kubernetes](https://img.shields.io/badge/Orchestration-Kubernetes-326CE5)
![Docker](https://img.shields.io/badge/Container-Docker-2496ED)
![RabbitMQ](https://img.shields.io/badge/Broker-RabbitMQ-FF6600)
![Celery](https://img.shields.io/badge/Queue-Celery-37814A)
![Flower](https://img.shields.io/badge/Monitoring-Flower-white?logo=celery&logoColor=green)
![PostgreSQL](https://img.shields.io/badge/DB-PostgreSQL-4169E1)

Ce projet implémente un processus métier de gestion des demandes de prêt immobilier en utilisant des concepts avancés de microservices, de tâches asynchrones, et de messagerie interservices. 

Il a été conçu pour être scalable, tolérant aux pannes et orienté événements, démontrant l'utilisation de patterns d'architecture modernes (Chorégraphie, Pattern Saga, WebSockets).

## 🏗️ Architecture du Système

Le système est découpé en services autonomes qui collaborent via **RabbitMQ** :

1.  **Loan Service** : Portail FastAPI. Gère la création des dossiers en PostgreSQL.
2.  **Credit Service** (Worker) : Analyse la solvabilité financière.
3.  **Property Service** (Worker) : Évalue la valeur du bien immobilier.
4.  **Decision Service** (Worker) : Agrège les données et valide/rejette le prêt.
5.  **Notification Service** : Worker d'envoi d'emails et mise à jour en temps réel via WebSockets.
6.  **Flower** : Interface de monitoring pour superviser les tâches Celery.

### Flux de données (Event-Driven)

```text
                +-------------------+
                |  Client / User    | <-------------------------+ (WebSockets SSE)
                +---------+---------+                           |
                          | (HTTP POST)                         |
                          ▼                                     |
                 +------------------+                  +------------------+
                 |   Loan Service   |                  | Notification Svc |
                 |     (FastAPI)    |                  |    (FastAPI)     |
                 +--------+---------+                  +--------+---------+
                          |                                     ▲
                          | Événement "Demande Créée"           | Événement "Décision Prise"
                          ▼                                     |
                    +-----------------------------------------------+
                    |                  RabbitMQ                     |
                    +----+--------------------------------------+---+
                         |                                      |
       +-----------------+-----------------+                    |
       |                                   |                    |
       ▼                                   ▼                    |
+----------------------+        +----------------------+        |
| Credit Score Worker  |        | Property Eval Worker |        |
|      (Celery)        |        |      (Celery)        |        |
+----------+-----------+        +----------+-----------+        |
           |                               |                    |
           +---------------+---------------+                    |
                           | Événements "Évalué"                |
                           ▼                                    |
                 +----------------------+                       |
                 | Solvency Decision    |-----------------------+
                 |      Service         |
                 +----------------------+

```
## Technologies Utilisées
- Backend : Python, FastAPI (API REST et WebSockets).
- Traitements Asynchrones : Celery, Redis (Backend de résultats).
- Message Broker : RabbitMQ (Gestion des flux atomiques et durabilité des messages).
- Base de données : PostgreSQL.Déploiement & Orchestration : Docker, Kubernetes.Monitoring : Flower (Monitoring des tâches Celery)
## 📂 Structure du Projet

```text
loan-system/
├── loan-service/          # API & Frontend (Jinja2/JS)
├── credit-score/          # Worker Score Crédit
├── property-eval/         # Worker Évaluation Bien
├── solvency-decision/     # Worker Décision Finale
├── notification-service/  # Worker Notifications & WS
├── k8s/                   # Manifestes Kubernetes (YAML)
└── docker-compose.yml
```
## 🐳 Déploiement avec Docker Compose
```bash 
docker-compose up -d --build
```
> Accès : http://localhost:8000


## ☸️ Déploiement avec Kubernetes
### Build des images locales
```bash 
docker build -t loan-service:latest ./loan-service
docker build -t credit-worker:latest ./credit-score
docker build -t property-worker:latest ./property-eval
docker build -t notification-worker:latest ./notification-service
docker build -t decision-worker:latest ./solvency-decision
```
### Déploiement de l'Infrastructure(Bases de données & Brokers)
```bash
kubectl apply -f postgres-deployment.yaml
kubectl apply -f rabbitmq-deployment.yaml
```
### Vérifier l'état du cluster
```bash 
kubectl get pods
kubectl get services
```
### Déploiement des Microservices & Monitoring
```bash
kubectl apply -f workers-deployment.yaml
kubectl apply -f loan-deployment.yaml
kubectl apply -f flower-deployment.yaml
```

### Accès aux Services
| Service | Rôle | URL d'accès |
| :--- | :--- | :--- |
| **Interface BankFlow** | Portail client (Dépôt & Suivi de prêt) | [http://localhost:30001](http://localhost:30001) |
| **Monitoring Flower** | Surveillance des tâches Celery | [http://localhost:30005](http://localhost:30005) |
| **RabbitMQ Management** | Gestion du Broker (Files d'attente) | [http://localhost:15672](http://localhost:15672) |

## 👥 Auteurs

Ce projet a été développé et orchestré par :

* **CISSE Mamadou**
    * **GitHub** : [github.com/ciscom](https://github.com/Ciscom224)
    * **LinkedIn** : [linkedin.com/in/cissmamadou](https://www.linkedin.com/in/cissemamadou/)

* **MANKAI Latifa**
     * **GitHub** : [github.com/mankailatifa](https://github.com/mankailatifa)
     * **GitHub** : [linkedin]((https://www.linkedin.com/in/latifa-mankai-467833206/)

---
**Stack Technique** : Python (FastAPI), Celery, RabbitMQ, PostgreSQL, Docker & Kubernetes.
*Environnement de développement : MacBook Pro et windows 11.*
