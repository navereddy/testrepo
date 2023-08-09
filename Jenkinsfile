pipeline{
    agent{
        label 'linux-ansible'
    }
    environment{
        DOCKERHUB_CREDENTIALS=credentials('karma792-dockerhub')
    }
    stages{
        stage('clone from git') {
            steps {
                git url:'https://github.com/evanke-a3/rest-controller.git', branch: 'feature/devOps_deploy', credentialsId:'github-cred'
            }
        }
        stage('Build docker image'){
            steps{
                sh 'docker build -t karma792/evanke_testapp:$BUILD_NUMBER . --no-cache'
            }
        }
        stage('Dockerhub login'){
            steps{
                sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
            }
        }
        stage('Push docker image'){
            steps{
                sh 'docker image push karma792/evanke_testapp:$BUILD_NUMBER'
            }
        }

        stage('Ansible'){
            steps{
                sh ''' 
                    ansible --version 
                    ansible-galaxy collection install community.docker
                '''
            }
        }
        // stage('ansible-install docker on target'){
        //     steps{
        //         sh 'cd ansible && ansible-playbook playbooks/playbook-docker-install.yml'
        //     }
        // }
        stage('ansible-run webapp'){
            steps{
                sh 'cd ansible && ansible-playbook playbook.yml'
            }
        }

    }
    post{
        always{
            sh 'docker system prune -a -f'
        }
    }
}
