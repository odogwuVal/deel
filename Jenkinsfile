#!/usr/bin/env groovy
import groovy.transform.Field

@Field
Map defaults = [
    image_repository: 'python',
    publiclyAccessible: true,
    deployment: "reverseip",
    worker_name: "Dev-Worker",
    helmFlags:"--set autoscaling.enabled=false \
        --set volume.secondVolume.enabled=false \
        --set volume.mountPath=/app/.env \
        --set resources.requests.memory=150Mi \
        --set resources.requests.cpu=120m \
        --set resources.limits.cpu=200 \
        --set resources.limits.memory=200Mi \
        --set ingress.enabled=true \
        --set hostNamePrefix=deel \
        --set secretObjects.secretName=reverseip \
        --set probes.readinessProbe.enabled=true \
        --set probes.path=/ \
        --set probes.livenessProbe.enabled=true \
        --set PersistentVolumeClaim.enabled=false \
        --set serviceAccount.name=secret-store \
        --set image.port=80 \
        --set cron.enabled=false \
        --set service.type=NodePort"
]

def ecrRepository = "651611223190.dkr.ecr.us-east-1.amazonaws.com"
node("${defaults.worker_name}") {
    try {
        properties([
            disableConcurrentBuilds(),
            buildDiscarder(logRotator(numToKeepStr: '10'))
        ])
        checkout scm
        stage('Build and push image') {   
        withEnv(["AWS_DEFAULT_REGION=us-east-1", "NAME=${defaults.image_repository}"]) {
            sh "aws ecr describe-repositories --repository-names ${NAME} || aws ecr create-repository --repository-name ${NAME} --image-scanning-configuration scanOnPush=true && aws ecr set-repository-policy --repository-name ${NAME} --policy-text file://ecr.json"
            sh "aws ecr get-login-password \
            | docker login \
                --password-stdin \
                --username AWS \
                '${ecrRepository}/${NAME}'"
            sh "docker build -t ${NAME} ."
            sh "docker tag ${NAME} ${ecrRepository}/${NAME}:${BUILD_NUMBER}"
            sh "docker push ${ecrRepository}/${NAME}:${BUILD_NUMBER}"
            }
        }
        stage ('tool setup') {
            // install kubectl
            sh "curl -O https://s3.us-west-2.amazonaws.com/amazon-eks/1.27.1/2023-04-19/bin/linux/amd64/kubectl || echo 'skip due to other thread'"
            sh "chmod +x ./kubectl || echo 'skip due to other thread'"
            sh "sudo cp ./kubectl /usr/bin/kubectl || echo 'skip due to other thread'"
            sh "kubectl version --short --client"
            sh "aws --version"

            // install helm
            sh "curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 > get_helm.sh && chmod 700 get_helm.sh && ./get_helm.sh || echo 'Skip to other thread'"
            sh "helm version"

            // install aws cli
            sh "curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip || echo 'skip due to other thread'"
            sh "unzip awscliv2.zip || echo 'skip due to other thread'"
            sh "sudo ./aws/install || echo 'skip due to other thread'"
            sh "aws --version"
        }
        stage ('deploy to eks') {
                flags = "${defaults.helmFlags}"
                autoscaling = "--set autoscaling.enabled=false"
                chartDirectory = "deployment-chart"
                helmName = "${defaults.deployment}"
                if (defaults.publiclyAccessible == true) {
                    access = "--set ingress.enabled=true"
                }
                else {
                    access = "--set ingress.enabled=false"
                }
                withCredentials([file(credentialsId: 'github_ssh_pub', variable: 'github_ssh_pub'), 
                file(credentialsId: 'github_ssh', variable: 'github_ssh')]) {
                    // setup ssh connection with github repository
                    sh "mkdir -p ~/.ssh/ || echo 'skip copying due to other thread'"
                    sh "sudo cp -Rf $github_ssh ~/.ssh/id_rsa && sudo cp -Rf $github_ssh_pub ~/.ssh/id_rsa.pub || echo 'skip copying due to other thread'"
                    sh "sudo chmod 600 -R ~/.ssh/* && sudo chown ec2-user:ec2-user -R ~/.ssh/*"
                    sh "eval \$(ssh-agent -s) && ssh-add ~/.ssh/id_rsa && ssh-keyscan -H github.com  >> ~/.ssh/known_hosts && ssh-keyscan -H github.com  >> ~/.ssh/known_hosts"
                    
                    // deploy with helm
                    sh "aws eks --region us-east-1 update-kubeconfig --name ${DEV_EKS_CLUSTER_NAME}"
                    sh "git clone git@github.com:ogtlimited/DEVELOPMENT-DEPLOYMENT-CHART.git || echo 'Already clone'"
                    sh "echo 'I am here' && cd DEVELOPMENT-*-CHART \
                        && helm upgrade --atomic --install ${helmName} ./${chartDirectory} \
                        --set image.repository=${ecrRepository}/${defaults.image_repository} \
                        --set image.tag=${BUILD_NUMBER} \
                        --wait \
                        ${flags} ${autoscaling} ${access}"
                }
        }
    } catch (e) {
        currentBuild.result = "FAILED"
        throw e
    } finally {
        cleanWs deleteDirs: true, notFailBuild: true
    }
}