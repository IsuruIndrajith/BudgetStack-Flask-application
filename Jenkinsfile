pipeline {
    agent any

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'dev-test',
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
                sh 'sleep 15'
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