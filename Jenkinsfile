pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'expense-tracker:latest'
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_CREDENTIALS = credentials('docker-hub-credentials')
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    sh 'docker build -t ${DOCKER_IMAGE} .'
                }
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running tests...'
                script {
                    sh '''
                        docker run --rm ${DOCKER_IMAGE} python -m pytest tests/ -v || true
                    '''
                }
            }
        }

        stage('Code Quality Check') {
            steps {
                echo 'Running code quality checks...'
                script {
                    sh '''
                        docker run --rm ${DOCKER_IMAGE} pip install flake8
                        docker run --rm ${DOCKER_IMAGE} flake8 app/ || true
                    '''
                }
            }
        }

        stage('Push to Registry') {
            when {
                branch 'dev-test'
            }
            steps {
                echo 'Pushing image to Docker Hub...'
                script {
                    sh '''
                        echo $DOCKER_CREDENTIALS_PSW | docker login -u $DOCKER_CREDENTIALS_USR --password-stdin
                        docker tag ${DOCKER_IMAGE} ${DOCKER_REGISTRY}/${DOCKER_CREDENTIALS_USR}/${DOCKER_IMAGE}
                        docker push ${DOCKER_REGISTRY}/${DOCKER_CREDENTIALS_USR}/${DOCKER_IMAGE}
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy') {
            when {
                branch 'dev-test'
            }
            steps {
                echo 'Deploying application...'
                script {
                    sh '''
                        docker-compose down || true
                        docker-compose up -d
                        echo "Application deployed successfully!"
                    '''
                }
            }
        }

        stage('Health Check') {
            steps {
                echo 'Running health checks...'
                script {
                    sh '''
                        sleep 10
                        curl -f http://localhost:5000/ || exit 1
                        echo "Health check passed!"
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution completed'
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
