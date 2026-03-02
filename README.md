# 💰 BudgetStack   Flask Expense Tracker with CI/CD Pipeline

A full-stack expense tracking web application built with **Flask** and **MySQL**, deployed on **AWS EC2** using a fully automated **CI/CD pipeline** powered by **Jenkins** and **Docker**.

---

## 📌 Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Application Features](#application-features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [CI/CD Pipeline Workflow](#cicd-pipeline-workflow)
- [AWS Infrastructure Setup](#aws-infrastructure-setup)
- [Installation & Local Setup](#installation--local-setup)
- [Docker Setup](#docker-setup)
- [Jenkins Pipeline Configuration](#jenkins-pipeline-configuration)
- [Environment Variables](#environment-variables)
- [Challenges & Fixes](#challenges--fixes)
- [What I Learned](#what-i-learned)

---

## Project Overview

BudgetStack is a two-tier web application that allows users to register, log in, and track their personal expenses across categories. The project emphasizes **DevOps best practices**   the entire deployment lifecycle from a `git push` to a live application running on AWS is fully automated with zero manual steps.

This project was built as a hands-on implementation of a CI/CD pipeline, covering containerization, automated testing, and cloud deployment.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | Python Flask |
| Database | MySQL 8.0 |
| Containerization | Docker, Docker Compose |
| CI/CD | Jenkins |
| Cloud | AWS EC2 (Ubuntu 22.04, t2.micro) |
| Version Control | Git, GitHub |
| Authentication | Flask Sessions, Werkzeug password hashing |
| ORM | Flask-SQLAlchemy |
| Frontend | HTML, Bootstrap 5 |

---

## Application Features

- User registration and login with hashed passwords
- Session-based authentication (each user sees only their own data)
- Add, view, and delete expenses
- Expense categories: Food, Transport, Utilities, Entertainment, Health, Other
- Total expense summary dashboard
- Multi-user support with data isolation

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  AWS EC2 Instance                │
│                                                 │
│   ┌─────────────┐       ┌──────────────────┐    │
│   │  Jenkins    │       │  Docker Network  │    │
│   │  (Port 8080)│       │                  │    │
│   │             │       │  ┌────────────┐  │    │
│   │  Pipeline:  │──────▶│  │ Flask App  │  │    │
│   │  - Clone    │       │  │ (Port 5000)│  │    │
│   │  - Build    │       │  └─────┬──────┘  │    │
│   │  - Deploy   │       │        │         │    │
│   │  - Test     │       │  ┌─────▼──────┐  │    │
│   └─────────────┘       │  │   MySQL    │  │    │
│                         │  │ (Port 3306)│  │    │
│                         │  └────────────┘  │    │
│                         └──────────────────┘    │
└─────────────────────────────────────────────────┘
         ▲
         │ git push triggers webhook
         │
┌────────┴────────┐
│   GitHub Repo   │
│  (Source Code)  │
└─────────────────┘
         ▲
         │ git push
         │
┌────────┴────────┐
│  Developer      │
│  Local Machine  │
│  (WSL/Terminal) │
└─────────────────┘
```

The application runs as two Docker containers on a single EC2 instance   a Flask web container and a MySQL database container   orchestrated by Docker Compose. Jenkins automates the full build and deployment cycle triggered by GitHub webhooks.

---

## Project Structure

```
BudgetStack-Flask-application/
│
├── app/
│   ├── __init__.py          # App factory, SQLAlchemy init
│   ├── models.py            # User and Expense database models
│   ├── routes.py            # All route handlers
│   └── templates/
│       ├── base.html        # Base layout with navbar
│       ├── index.html       # Expense dashboard
│       ├── add_expense.html # Add expense form
│       ├── login.html       # Login page
│       └── register.html    # Registration page
│
├── config.py                # App configuration, DB URI
├── run.py                   # App entry point with DB retry logic
├── requirements.txt         # Python dependencies
├── Dockerfile               # Flask app container definition
├── docker-compose.yml       # Multi-container orchestration
└── Jenkinsfile              # CI/CD pipeline definition
```

---

## CI/CD Pipeline Workflow

The pipeline is defined in the `Jenkinsfile` at the root of the repository and consists of the following stages:

```
GitHub Push
    │
    ▼
Jenkins Webhook Trigger
    │
    ▼
┌─────────────────────┐
│ Stage 1: Clone Repo │  Jenkins pulls latest code from GitHub main branch
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────┐
│ Stage 2: Build Docker    │  docker build -t expense-tracker .
│         Image            │  Packages Flask app into a container image
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Stage 3: Tear Down Old   │  docker-compose down
│         Containers       │  Removes previously running containers
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Stage 4: Deploy          │  docker-compose up -d --build
│         Containers       │  Spins up Flask + MySQL containers
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Stage 5: Wait for DB     │  Polls mysqladmin ping every 10 seconds
│         to be Ready      │  Up to 30 attempts (5 minutes max)
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Stage 6: Integration     │  curl -f http://localhost:5000
│         Test             │  Confirms Flask app is reachable
└──────────┬───────────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
SUCCESS        FAILURE
  │               │
  │          docker-compose logs
  │          printed to console
  ▼
App live at http://EC2-PUBLIC-IP:5000
```

### Jenkinsfile

```groovy
pipeline {
    agent any

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/IsuruIndrajith/BudgetStack-Flask-application.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t expense-tracker .'
            }
        }

        stage('Tear Down Old Containers') {
            steps {
                sh 'docker-compose down || true'
            }
        }

        stage('Deploy Containers') {
            steps {
                sh 'docker-compose up -d --build'
            }
        }

        stage('Wait for DB to be Ready') {
            steps {
                sh '''
                    echo "Waiting for MySQL to be ready..."
                    for i in $(seq 1 30); do
                        if docker-compose exec -T db mysqladmin ping -h localhost -u root -prootpassword --silent; then
                            echo "MySQL is ready!"
                            exit 0
                        fi
                        echo "Attempt $i/30 - MySQL not ready yet, waiting 10s..."
                        sleep 10
                    done
                    echo "MySQL failed to be ready in time"
                    exit 1
                '''
            }
        }

        stage('Integration Test') {
            steps {
                sh 'curl -f http://localhost:5000 || exit 1'
            }
        }
    }

    post {
        success {
            echo 'Deployment successful! App is running on port 5000.'
        }
        failure {
            echo 'Pipeline failed. Check logs above.'
            sh 'docker-compose logs'
        }
    }
}
```

---

## AWS Infrastructure Setup

### EC2 Instance

| Setting | Value |
|---|---|
| AMI | Ubuntu 22.04 LTS |
| Instance Type | t2.micro (Free Tier) |
| Storage | 8GB EBS |
| Key Pair | .pem file for SSH access |

### Security Group Inbound Rules

| Port | Protocol | Purpose |
|---|---|---|
| 22 | TCP | SSH access |
| 8080 | TCP | Jenkins web UI |
| 5000 | TCP | Flask application |

### Installed Services on EC2

```bash
# Docker
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
sudo usermod -aG docker jenkins

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Jenkins
sudo apt install -y default-jdk
curl -fsSL https://pkg.jenkins.io/debian/jenkins.io-2023.key | \
  sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian binary/ | \
  sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt update && sudo apt install -y jenkins
sudo systemctl enable jenkins
```

### Memory Optimization (t2.micro)

To prevent the instance from running out of memory during builds, 2GB of swap space was added:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## Installation & Local Setup

### Prerequisites

- Python 3.11+
- MySQL running locally
- Git

### Steps

```bash
# Clone the repository
git clone https://github.com/IsuruIndrajith/BudgetStack-Flask-application.git
cd BudgetStack-Flask-application

# Install dependencies
pip install -r requirements.txt

# Create the database in MySQL
mysql -u root -p
CREATE DATABASE expense_db;
exit;

# Run the application
python run.py
```

Visit `http://localhost:5000` in your browser.

---

## Docker Setup

To run the full application stack locally using Docker:

```bash
# Build and start both containers
docker-compose up -d --build

# Check running containers
docker ps

# View logs
docker-compose logs

# Stop and remove containers
docker-compose down

# Stop and remove containers AND volumes (resets database)
docker-compose down -v
```

### docker-compose.yml

```yaml
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: expense_db
      MYSQL_USER: expenseuser
      MYSQL_PASSWORD: expensepassword
      MYSQL_ROOT_HOST: '%'
    command: --innodb-buffer-pool-size=128M
    mem_limit: 512m
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build: .
    mem_limit: 256m
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: mysql+pymysql://expenseuser:expensepassword@db/expense_db
      SECRET_KEY: your-secret-key-here
    depends_on:
      db:
        condition: service_healthy

volumes:
  mysql_data:
```

---

## Jenkins Pipeline Configuration

### Initial Setup

1. Access Jenkins at `http://EC2-PUBLIC-IP:8080`
2. Unlock with the initial admin password:
   ```bash
   sudo cat /var/lib/jenkins/secrets/initialAdminPassword
   ```
3. Install suggested plugins
4. Create admin user

### Pipeline Job Setup

1. New Item → Pipeline
2. Pipeline Definition → Pipeline script from SCM
3. SCM → Git
4. Repository URL → your GitHub repo URL
5. Branch → `*/main`
6. Script Path → `Jenkinsfile`
7. Save

### GitHub Webhook (Auto-trigger on Push)

1. In Jenkins job → Configure → Build Triggers → check **GitHub hook trigger for GITScm polling**
2. In GitHub → Repository Settings → Webhooks → Add Webhook:
   - Payload URL: `http://EC2-PUBLIC-IP:8080/github-webhook/`
   - Content type: `application/json`
   - Trigger: Just the push event

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | Full MySQL connection string | `mysql+pymysql://root:password@localhost/expense_db` |
| `SECRET_KEY` | Flask session encryption key | `dev-secret-key` |

In production (Docker), these are injected via `docker-compose.yml` environment section.

---

## Challenges & Fixes

### 1. Jenkins Permission Denied on Docker Socket
**Error:** `permission denied while trying to connect to the Docker daemon socket`

**Fix:** Added Jenkins user to the docker group:
```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### 2. `docker compose` Command Not Found
**Error:** `docker: unknown command: docker compose`

**Fix:** The standalone binary installed was `docker-compose` (with hyphen). Updated all Jenkinsfile references from `docker compose` to `docker-compose`.

### 3. MySQL Not Ready When Flask Starts
**Error:** `(2003, "Can't connect to MySQL server on 'db'")`

**Fix:** Replaced `sleep 15` in the Jenkinsfile with an active polling loop using `mysqladmin ping`, and added retry logic inside `run.py` so Flask retries the DB connection up to 10 times before giving up.

### 4. MySQL Refusing Flask Container Connection
**Error:** `(1130, "host is not allowed to connect to this MySQL server")`

**Fix:** Added `MYSQL_ROOT_HOST: '%'` to the MySQL service environment in `docker-compose.yml` to allow connections from any Docker network host, then cleared the old volume with `docker-compose down -v` to force MySQL to reinitialize with the corrected permissions.

### 5. EC2 Instance Freezing During Builds
**Cause:** t2.micro has 1GB RAM. Jenkins + MySQL + Flask containers together exceeded available memory.

**Fix:** Added 2GB swap space on the EC2 instance and set `mem_limit` on each Docker service in `docker-compose.yml` to prevent any single container from consuming all available memory.

---

## What I Learned

- How to design and implement a real-world CI/CD pipeline from scratch
- How Docker networking works between containers (why `localhost` inside a container is not the host machine)
- How to debug Jenkins build failures using console output and `docker-compose logs`
- How to manage AWS EC2 security groups, resource constraints, and cost optimization on a free tier instance
- How to implement multi-user session-based authentication in Flask
- The importance of health checks and retry logic in containerized environments where service startup order is not guaranteed
- How GitHub webhooks integrate with Jenkins to enable fully automated deployments on every push
