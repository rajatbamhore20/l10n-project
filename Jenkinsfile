pipeline {
    agent any

    parameters {
        string(name: 'LOCALES_DIR', defaultValue: 'locales', description: 'Directory containing en.json and translated locale JSON files')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Validate') {
            steps {
                sh 'bash tools/run_checks.sh "$LOCALES_DIR"'
            }
        }

        stage('Report') {
            steps {
                archiveArtifacts artifacts: 'reports/locale-report.txt', allowEmptyArchive: false
            }
        }
    }

    post {
        success {
            echo 'Locale validation passed.'
        }
        unsuccessful {
            echo 'Locale validation found blocking issues. The build is failed so releases cannot continue with incomplete or inconsistent translations.'
            archiveArtifacts artifacts: 'reports/locale-report.txt', allowEmptyArchive: true
        }
        always {
            echo "Checked locales directory: ${params.LOCALES_DIR}"
        }
    }
}
