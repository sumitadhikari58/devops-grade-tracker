pipeline {
  agent any

  environment {
    IMAGE_NAME      = "grade-tracker"
    DEV_PORT        = "5050"
    PROD_PORT       = "80"
    DEV_CONTAINER   = "grade-tracker-dev"
    PROD_CONTAINER  = "grade-tracker-prod"
  }

  stages {

    stage('1 - Git Checkout') {
      steps {
        echo "=============================="
        echo "Build:  #${env.BUILD_NUMBER}"
        echo "=============================="
        checkout scm
        script {
          def detected = env.BRANCH_NAME ?: env.GIT_BRANCH ?: 'develop'
          env.ACTIVE_BRANCH = detected
            .replaceFirst(/^origin\//, '')
            .replaceFirst(/^refs\/heads\//, '')
          echo "Branch: ${env.ACTIVE_BRANCH}"
        }
      }
    }

    stage('2 - Code Lint') {
      steps {
        sh '''
          python -m pip install --user flake8
          echo "Running code quality check..."
          python -m flake8 app.py --max-line-length=120 \
            --exclude=venv,__pycache__ || true
          echo "Lint check complete"
        '''
      }
    }

    stage('3 - Unit Tests') {
      steps {
        sh '''
          python -m pip install --user -r requirements.txt
          echo "Running unit tests..."
          python -m pytest tests/ -v --tb=short
          echo "All tests passed"
        '''
      }
    }

    stage('4 - Docker Build') {
      steps {
        sh """
          echo "Building Docker image..."
          docker build \
            -t ${IMAGE_NAME}:${BUILD_NUMBER} \
            -t ${IMAGE_NAME}:latest \
            .
          echo "Image built: ${IMAGE_NAME}:${BUILD_NUMBER}"
          docker images | grep ${IMAGE_NAME}
        """
      }
    }

    stage('5 - Deploy to Development') {
      when {
        expression { env.ACTIVE_BRANCH == 'develop' }
      }
      steps {
        sh """
          echo "Deploying to DEVELOPMENT on port ${DEV_PORT}..."
          docker stop ${DEV_CONTAINER} || true
          docker rm   ${DEV_CONTAINER} || true
          docker run -d \
            --name ${DEV_CONTAINER} \
            -p ${DEV_PORT}:5050 \
            -e APP_ENV=Development \
            --restart unless-stopped \
            ${IMAGE_NAME}:latest
          echo "Dev container started"
          docker ps | grep ${DEV_CONTAINER}
        """
      }
    }

    stage('5 - Deploy to Production') {
      when {
        expression { env.ACTIVE_BRANCH == 'main' }
      }
      steps {
        sh """
          echo "Deploying to PRODUCTION on port ${PROD_PORT}..."
          docker stop ${PROD_CONTAINER} || true
          docker rm   ${PROD_CONTAINER} || true
          docker run -d \
            --name ${PROD_CONTAINER} \
            -p ${PROD_PORT}:5050 \
            -e APP_ENV=Production \
            --restart unless-stopped \
            ${IMAGE_NAME}:latest
          echo "Prod container started"
          docker ps | grep ${PROD_CONTAINER}
        """
      }
    }

    stage('6 - Health Check') {
      steps {
        sh '''
          echo "Waiting for app to start..."
          sleep 8
        '''
        script {
          def port = (env.ACTIVE_BRANCH == 'main')
                      ? env.PROD_PORT
                      : env.DEV_PORT
          sh """
            echo "Checking health on port ${port}..."
            curl -f http://localhost:${port}/health
            echo ""
            echo "Health check PASSED"
            echo "App URL: http://\$(curl -s ifconfig.me):${port}"
          """
        }
      }
    }
  }

  post {
    success {
      script {
        def port = (env.ACTIVE_BRANCH == 'main')
                    ? env.PROD_PORT
                    : env.DEV_PORT
        def env_name = (env.ACTIVE_BRANCH == 'main')
                        ? 'PRODUCTION'
                        : 'DEVELOPMENT'
        echo """
        ==============================
        DEPLOYMENT SUCCESSFUL
        Environment : ${env_name}
        Branch      : ${env.ACTIVE_BRANCH}
        Build       : #${env.BUILD_NUMBER}
        Port        : ${port}
        ==============================
        """
      }
    }
    failure {
      echo """
      ==============================
      DEPLOYMENT FAILED
      Branch : ${env.ACTIVE_BRANCH}
      Build  : #${env.BUILD_NUMBER}
      Check the stage logs above.
      ==============================
      """
    }
    always {
      sh "docker image prune -f || true"
      echo "Workspace cleaned up."
    }
  }
}
