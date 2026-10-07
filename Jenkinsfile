pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        COMPOSE_PROJECT_NAME = 'credit-scoring'
        POSTGRES_USER        = 'creditadmin'
        POSTGRES_DB          = 'credit_scoring'
        POSTGRES_PASSWORD    = credentials('postgres-password')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    python3 -m venv .venv-ci
                    . .venv-ci/bin/activate
                    pip install --quiet flake8
                    # Fail only on syntax errors and undefined names
                    flake8 backend ml-service/api.py ml-service/src \
                        --exclude venv,.venv-ci,__pycache__ \
                        --select=E9,F63,F7,F82 --show-source
                '''
            }
        }
        stage('Test') {
            steps {
                sh '''
                    . .venv-ci/bin/activate
                    pip install --quiet pytest httpx python-dotenv
                    pytest tests -q
                '''
            }
        }
        stage('Build images') {
            steps {
                sh 'docker compose build'
            }
        }

        stage('Deploy') {
            steps {
                sh 'docker compose up -d'
            }
        }

        stage('Smoke test') {
            steps {
                sh '''
                    for i in $(seq 1 20); do
                        if docker compose exec -T backend python3 -c "import urllib.request as u; u.urlopen('http://localhost:8000/health'); u.urlopen('http://ml-service:8001/health')"; then
                            echo "Smoke test passed"; exit 0
                        fi
                        echo "Waiting for services ($i/20)..."; sleep 5
                    done
                    docker compose ps
                    exit 1
                '''
            }
        }
    }

    post {
        failure { sh 'docker compose logs --tail=50 || true' }
        always  { sh 'rm -rf .venv-ci' }
    }
}
