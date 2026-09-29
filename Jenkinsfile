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
                script {
                    env.LOCALE_VALIDATION_STATUS = sh(script: 'bash tools/run_checks.sh "$LOCALES_DIR"', returnStatus: true).toString()
                }
            }
        }

        stage('Report') {
            steps {
                archiveArtifacts artifacts: 'reports/locale-report.txt', allowEmptyArchive: false
                script {
                    if (env.LOCALE_VALIDATION_STATUS != '0') {
                        error('Locale validation failed; see reports/locale-report.txt for details.')
                    }
                }
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
