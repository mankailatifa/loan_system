# Système de Gestion des Demandes de Prêt Immobilier - Architecture Microservices

Ce projet implémente un processus métier de gestion des demandes de prêt immobilier en utilisant des concepts avancés de microservices, de tâches asynchrones, et de messagerie interservices. 

Il a été conçu pour être scalable, tolérant aux pannes et orienté événements, démontrant l'utilisation de patterns d'architecture modernes (Chorégraphie, Pattern Saga, WebSockets).

## 🏗️ Architecture du Système

Le système est composé de plusieurs microservices distincts qui communiquent de manière asynchrone[cite: 11]:

1. **Service des demandes de prêt (Loan Service)** : Point d'entrée principal. Gère la création et la validation initiale des dossiers
2. **Service de vérification du crédit (Credit Service)** : Évalue les antécédents financiers du client de manière asynchrone.
3. **Service d'évaluation du bien (Property Service)** : Analyse la valeur du bien immobilier ciblé (tâche asynchrone).
4. **Service de décision (Decision Service)** : Agrège les résultats et procède à l'approbation ou au rejet de la demande.
5. **Service de notification (Notification Service)** : Informe les clients des résultats en temps réel via WebSockets.

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
│
├── loan-service/          # API de création des demandes
├── credit-score/          # Worker Celery pour le crédit
├── property-eval/         # Worker Celery pour l'évaluation immobilière
├── decision-service/      # API d'agrégation et de décision
├── notification-service/  # API WebSockets pour le temps réel
│
├── k8s/                   # Fichiers de configuration Kubernetes
│   ├── infrastructure/    # Déploiements DB, Redis, RabbitMQ
│   └── microservices/     # Déploiements des services métiers
│
└── README.md
```
## ⚙️ Déploiement avec Kubernetes
### Construire les images Docker
```bash 
docker build -t loan-service ./loan-service
docker build -t credit-service ./credit-score
docker build -t property-service ./property-eval
docker build -t decision-service ./decision-service
docker build -t notification-service ./notification-service
```
### Déployer l'infrastructure (Bases de données & Brokers)
```bash
kubectl apply -f k8s/infrastructure/
```
### Déployer les Microservices
```bash
kubectl apply -f k8s/microservices/
```
### Vérifier l'état du cluster
```bash 
kubectl get pods
kubectl get services
```
## Utilisation et Tests
- Interface Utilisateur : Accédez au formulaire de demande via http://localhost:<NodePort-LoanService>/form.
- Dashboard Temps Réel : Ouvrez l'interface de notification sur http://localhost:<NodePort-NotificationService>/dashboard pour voir les mises à jour en direct.
- Monitoring Celery : Accédez à Flower via http://localhost:<NodePort-Flower> pour observer l'exécution des tâches asynchrones en arrière-plan