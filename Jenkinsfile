pipeline {
  agent any
  stages {
    stage('Backend tests') {
      steps {
        sh 'docker compose run --rm api pytest'
      }
    }
    stage('Frontend build') {
      steps {
        sh 'docker compose run --rm web sh -c "npm install && npm run build"'
      }
    }
  }
  post {
    always { sh 'docker compose down --remove-orphans || true' }
  }
}
