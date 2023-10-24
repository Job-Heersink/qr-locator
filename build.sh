aws ecr get-login-password --region eu-west-2 --profile job-sandbox | docker login --username AWS --password-stdin 375681122944.dkr.ecr.eu-west-2.amazonaws.com
docker build -t locationfinder .
docker tag locationfinder:latest 375681122944.dkr.ecr.eu-west-2.amazonaws.com/locationfinder:latest
docker push 375681122944.dkr.ecr.eu-west-2.amazonaws.com/locationfinder:latest

