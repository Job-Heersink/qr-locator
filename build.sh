AWS_ECR_REPO=375681122944.dkr.ecr.eu-west-2.amazonaws.com
aws ecr get-login-password --region eu-west-2 --profile job-sandbox | docker login --username AWS --password-stdin $AWS_ECR_REPO
docker build -t locationfinder .
docker tag locationfinder:latest $AWS_ECR_REPO/locationfinder:latest
docker push $AWS_ECR_REPO/locationfinder:latest

UPDATE_RETURN=$(aws lambda update-function-code --function-name LocationTest --image-uri $AWS_ECR_REPO/locationfinder:latest --profile job-sandbox --region eu-west-2)

STATUS='InProgress'
while [ "$STATUS" == "InProgress" ]
do
  sleep 3
  STATUS=$(aws lambda get-function --function-name LocationTest --profile job-sandbox --region eu-west-2 --query "Configuration.LastUpdateStatus" --output text)
  echo $STATUS
done
aws lambda get-function-url-config --function-name LocationTest --profile job-sandbox --region eu-west-2 --query "FunctionUrl" --output text
