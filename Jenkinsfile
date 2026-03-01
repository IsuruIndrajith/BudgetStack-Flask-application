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