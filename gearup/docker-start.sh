#!/bin/bash
GREEN='\033[32m'
PURPLE='\033[34m'
PURPLE='\e[0;35m'
RESET='\033[0m'

now=$(date +"%Y%m%d%H%M%S")
docker_image="gearup-admin"
ecr_repo="g2c-admin"
aws_account_id="686487091234"
region="us-east-1"
project="gearup-v7"

docker build -t gearup-admin:$now .;
if [ $? -eq 0 ]; then
    echo -e "${GREEN}(bash start.sh)${RESET}: Docker image built successfully"
else
    echo -e "${PURPLE}(bash start.sh)${RESET}: Docker image build failed"
fi
# echo -e "${GREEN}(bash start.sh)${RESET}: Docker image built successfully"

# login to ECR
aws ecr get-login-password --region $region | docker login --username AWS --password-stdin $aws_account_id.dkr.ecr.$region.amazonaws.com
if [ $? -eq 0 ]; then
    echo -e "${GREEN}(bash start.sh)${RESET}: Logged in to ECR"
else
    echo -e "${PURPLE}(bash start.sh)${RESET}: Logging in to ECR failed"
fi
#echo -e "${GREEN}(bash start.sh)${RESET}: Logged in to ECR"
# Tag your image
docker tag $docker_image:$now $aws_account_id.dkr.ecr.$region.amazonaws.com/$ecr_repo:$now
if [ $? -eq 0 ]; then
    echo -e "${GREEN}(bash start.sh)${RESET}: Image tagged successfully"
else
    echo -e "${PURPLE}(bash start.sh)${RESET}: Image tagging failed"
fi
# echo "${GREEN}(bash start.sh)${RESET}: Image tagged successfully"

docker run -d -p 8000:8000 gearup-admin:$now
if [ $? -eq 0 ]; then
    echo -e "${GREEN}(bash start.sh)${RESET}: Docker container started successfully"
else
    echo -e "${PURPLE}(bash start.sh)${RESET}: Docker container start failed"
fi

# docker push $aws_account_id.dkr.ecr.$region.amazonaws.com/$ecr_repo:$now
# echo "${GREEN}(bash start.sh)${RESET}: Image pushed to ECR";
# echo "${GREEN}(bash start.sh)${RESET}: Overwriting Dockerrun.aws.json"
# echo '{
#     "AWSEBDockerrunVersion": "1",
#     "Image": {
#         "Name": "'$aws_account_id'.dkr.ecr.'$region'.amazonaws.com/'$ecr_repo':'$now'",
#         "Update": "true"
#     },
#     "Ports": [
#         {
#             "ContainerPort": "8000"
#         }
#     ],
#     "Logging": "/var/log/nginx"
# }' > Dockerrun.aws.json
# echo "${GREEN}(bash start.sh)${RESET}: Dockerrun.aws.json overwritten"
# sed -i '' 's/<AWS_ACCOUNT_ID>/'$aws_account_id'/g' Dockerrun.aws.json
# echo "${GREEN}(bash start.sh)${RESET}: Dockerrun file updated aws account id"
# sed -i '' 's/<NAME>/'$erc_repo'/g' Dockerrun.aws.json
# echo "${GREEN}(bash start.sh)${RESET}: Dockerrun file updated repo name"
# sed -i '' 's/<TAG>/'$now'/g' Dockerrun.aws.json
# echo "${GREEN}(bash start.sh)${RESET}: Dockerrun file updated tag"
# cat Dockerrun.aws.json


# Initialize Elastic Beanstalk application
# eb init -p docker $project

# Create an environment
# eb create my-env

# Deploy the application
# eb deploy
# echo "${GREEN}(bash start.sh)${RESET}: Application deployed successfully"
# Add an environment variable to Elastic Beanstalk environment
# eb setenv VARIABLE_NAME=variable_value
# echo "${GREEN}(bash start.sh)${RESET}: Environment variable added successfully"

