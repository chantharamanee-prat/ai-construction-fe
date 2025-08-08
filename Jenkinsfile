def scmVars
node {
    stage('Checkout') {
        scmVars = checkout scm
        echo "Current branch: ${scmVars.GIT_BRANCH}"
    }
    stage('Build') {
        if (scmVars.GIT_BRANCH.endsWith('/master')) {
            sh 'docker build -t yolo-server-api -f Dockerfile .'
            sh 'docker build -t yolo-server-web -f web/Dockerfile web/'
        } else {
            echo "Skipped."
        }
    }
    stage('Deploy Docker') {
        if (scmVars.GIT_BRANCH.endsWith('/master')) {
            sh 'docker compose down'
            sh 'docker compose up -d --build'
        } else {
            echo "Skipped."
        }
    }
}