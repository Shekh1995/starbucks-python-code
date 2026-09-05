pipeline {

    agent any

    environment {
        IMAGE_NAME = "shekhar013/starbucks-python-code"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Python Setup') {
            steps {
                sh '''
                    python3 --version
                    pip3 --version
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Application Verification') {
            steps {
                sh '''
                    . venv/bin/activate
                    python create_verify.py
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build \
                        -t ${IMAGE_NAME}:${BUILD_NUMBER} \
                        -t ${IMAGE_NAME}:latest \
                        .
                '''
            }
        }

        stage('Docker Push') {
            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {

                    sh '''
                        echo "$DOCKER_PASSWORD" | docker login \
                            -u "$DOCKER_USERNAME" \
                            --password-stdin

                        docker push ${IMAGE_NAME}:${BUILD_NUMBER}
                        docker push ${IMAGE_NAME}:latest
                    '''
                }
            }
        }

        stage('Container Test') {
            steps {
                sh '''
                    docker rm -f vrindavan-nights-test || true

                    docker run -d \
                        --name starbucks-python-code \
                        -p 8000:8000 \
                        ${IMAGE_NAME}:${BUILD_NUMBER}

                    sleep 10

                    curl -f http://localhost:8000/

                    docker rm -f starbucks-python-code
                '''
            }
        }
    }

    post {

        success {
            echo '======================================'
            echo 'starbucks-python-code CI/CD SUCCESS'
            echo '======================================'
        }

        failure {
            echo '======================================'
            echo 'starbucks-python-code FAILED'
            echo 'Check the failed stage.'
            echo '======================================'
        }
    }
}
