pipeline {
  agent any
  parameters {
    choice(name: 'VERSION', choices: ['v1', 'v2', 'v3'], description: 'Branch / image tag to build')
  }
  environment {
    DOCKER_USER = 'theamansikandar'
    IMAGE       = "${DOCKER_USER}/disease-tracker"
    REPO_URL    = 'https://github.com/YOUR_GITHUB_USERNAME/disease-tracker.git'
  }
  stages {
    stage('Checkout') {
      steps { git branch: params.VERSION, url: env.REPO_URL }
    }
    stage('Build Image') {
      steps { sh "docker build -t ${IMAGE}:${params.VERSION} ." }
    }
    stage('Push to DockerHub') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                         usernameVariable: 'U', passwordVariable: 'P')]) {
          sh 'echo $P | docker login -u $U --password-stdin'
          sh "docker push ${IMAGE}:${params.VERSION}"
        }
      }
    }
    stage('Deploy to Kubernetes') {
      steps {
        sh "sed 's#DOCKERUSER#${DOCKER_USER}#g' k8s/deployment-${params.VERSION}.yaml | kubectl apply -f -"
      }
    }
  }
}
