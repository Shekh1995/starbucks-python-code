pipeline {

    agent any

    environment {
        IMAGE_NAME = "shekhar013/starbucks-python-code"
    }

    stages {

        stage("Clean Workspace") {
            steps {
                cleanWs()
            }
        }

        stage("Git Checkout") {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Shekh1995/starbucks-python-code.git'
            }
        }

        stage("Python Setup") {
            steps {
                sh '''
                    python3 --version
                    pip3 --version
                '''
            }
        }

        stage("Install Dependencies") {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage("Application Verification") {
            steps {
                sh '''
                    . venv/bin/activate
                    python create_verify.py
                '''
            }
        }

        stage("Build Docker Image") {
            steps {
                sh '''
                    docker build \
                        -t ${IMAGE_NAME}:${BUILD_NUMBER} \
                        -t ${IMAGE_NAME}:latest \
                        .
                '''
            }
        }

        stage("Tag & Push to DockerHub") {
            steps {
                script {

                    withDockerRegistry(credentialsId: 'docker') {

                        sh '''
                            docker push ${IMAGE_NAME}:${BUILD_NUMBER}
                            docker push ${IMAGE_NAME}:latest
                        '''
                    }
                }
            }
        }

        stage("Container Test") {
            steps {
                sh '''
                    docker rm -f starbucks-python-code || true

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
