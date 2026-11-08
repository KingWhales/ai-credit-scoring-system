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
        GRAFANA_PASSWORD  = credentials('grafana-password')
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

        stage('Monitoring check') {
            steps {
                sh '''
                    for i in $(seq 1 24); do
                        if docker compose exec -T backend python3 -c "
import json, urllib.request as u
for url in ('http://backend:8000/metrics', 'http://ml-service:8001/metrics'):
    assert b'# HELP' in u.urlopen(url).read(), url
t = json.load(u.urlopen('http://prometheus:9090/api/v1/targets'))['data']['activeTargets']
assert len(t) >= 2 and all(x['health'] == 'up' for x in t), [(x['labels']['job'], x['health']) for x in t]
print('Monitoring OK:', [(x['labels']['job'], x['health']) for x in t])
"; then exit 0; fi
                        echo "Waiting for Prometheus targets ($i/24)..."; sleep 5
                    done
                    docker compose logs --tail=30 prometheus
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
