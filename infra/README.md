# CDK Infrastructure

This CDK project provisions:

1. **ECR Repository** — Private container registry for your Docker image
2. **Fargate Service** — Serverless ECS cluster running your Django app behind an Application Load Balancer (ALB)

## What gets created

### ECR Stack

- Private ECR repository: `almina-design`
- Image scan on push enabled
- Lifecycle policy keeping the latest 20 images

### Fargate Stack

- VPC with public/private subnets across 2 AZs
- ECS cluster
- Fargate service (256 CPU, 512 MB memory, 1 task)
- Application Load Balancer with health checks
- CloudWatch Logs group (7-day retention)

## Prerequisites

- AWS CLI configured (`aws configure`)
- AWS CDK CLI installed (`npm i -g aws-cdk`)
- Python 3.11+
- Docker and Docker Compose running locally

## Deploy infrastructure only (ECR + Fargate)

From the `infra` folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cdk bootstrap
cdk deploy
```

When prompted, approve both stacks. Wait for CloudFormation to finish (~5–10 minutes).

## Push app image to ECR and deploy to Fargate

From the **project root** after infrastructure deployment:

```powershell
$Region = "us-east-1"
$AccountId = aws sts get-caller-identity --query Account --output text
$RepoUri = "$AccountId.dkr.ecr.$Region.amazonaws.com/almina-design"

# Authenticate Docker to ECR
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $RepoUri

# Build and push image
docker build -t almina-design:latest .
docker tag almina-design:latest ($RepoUri + ":latest")
docker push ($RepoUri + ":latest")
```

**Note:** If your AWS default region is not `us-east-1`, update `$Region` to your deployed region.

## Access the running app

After infrastructure deploy completes, look for the CloudFormation output `LoadBalancerDns`. Visit that URL in your browser.

Example: `http://almina-alb-1234567890.us-east-1.elb.amazonaws.com`

## Update running app after code changes

1. Rebuild and push a new image tag:

```powershell
$Tag = "v1.0"
docker build -t almina-design:$Tag .
docker tag almina-design:$Tag "$RepoUri:$Tag"
docker push "$RepoUri:$Tag"
```

2. Update the Fargate service to use the new image:

```powershell
aws ecs update-service \
  --cluster AlminaCluster \
  --service AlminaFargateService \
  --force-new-deployment \
  --region us-east-1
```

Or redeploy from CDK (modifies task definition automatically):

```powershell
cdk deploy AlminaFargateStack
```

## Environment variables and secrets

Currently, the Fargate task pulls environment variables from the `.env` file **baked into the Docker image at build time**. For production, consider:

- Store secrets in AWS Secrets Manager and reference them in the task definition
- Use AWS Systems Manager Parameter Store for non-sensitive config
- Pass via `containerEnvironment` in `almina_infra_stack.py`

See [ECR task definition docs](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html#container_definition_environment).

## Database and persistence

This setup uses SQLite (from your Dockerfile). For production:

- Migrate to PostgreSQL or RDS
- Mount EFS for persistent file storage
- Consider managed databases for durability and scaling

## Cost notes

- **VPC, ECS, Fargate**: ~$30–50/month for 1 task
- **ECR**: ~$0.10 per GB stored, no egress within the same region
- **ALB**: ~$16/month + $0.006 per LCU
- **CloudWatch Logs**: Minimal for this volume (~$1/month)

To reduce costs: scale down task count to 0, delete unused images, or use Fargate Spot pricing.

## Cleanup

To delete all resources:

```powershell
cdk destroy
```

Confirm when prompted. The ECR repository is retained by policy (delete manually if needed).
