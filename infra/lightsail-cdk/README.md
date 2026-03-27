# Lightsail CDK Deployment

This CDK app provisions a Lightsail instance, a static IP, and public ports for the Django store. The instance bootstraps itself on first launch by cloning the repository, installing dependencies, running migrations, collecting static files, and starting `gunicorn` behind `nginx`.

## What It Creates

- 1 Ubuntu Lightsail instance
- 1 static IP attached to the instance
- Public TCP ports 22, 80, and 443
- Bootstrapped Django app under `/opt/almina-design`

## Prerequisites

- AWS account credentials configured for CDK
- AWS CDK CLI installed (`npm install -g aws-cdk`)
- A repo URL the instance can clone on first boot
- Optional: a Lightsail SSH key pair already created in your target region

## Quick Start

```powershell
cd infra/lightsail-cdk
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cdk bootstrap
cdk deploy -c repoUrl=https://github.com/your-user/almina-design.git -c branch=main -c availabilityZone=us-east-1a
```

## Useful Context Values

- `repoUrl` (required): Git URL the instance will clone
- `branch`: Git branch to deploy, default `main`
- `availabilityZone`: Lightsail AZ, default `us-east-1a`
- `bundleId`: Lightsail bundle, default `micro_3_0`
- `blueprintId`: OS image, default `ubuntu_22_04`
- `instanceName`: Lightsail instance name, default `almina-design`
- `appName`: App directory/service prefix, default `almina-design`
- `keyPairName`: Existing Lightsail SSH key pair name
- `domainName`: Optional DNS name for Nginx and HTTPS
- `certificateEmail`: Optional email used by Certbot when `domainName` is set
- `stackName`: Optional CloudFormation stack name override

Example with domain and SSH key pair:

```powershell
cdk deploy `
  -c repoUrl=https://github.com/your-user/almina-design.git `
  -c branch=main `
  -c availabilityZone=us-east-1a `
  -c keyPairName=my-lightsail-key `
  -c domainName=store.example.com `
  -c certificateEmail=you@example.com
```

## Bootstrap Behavior

On first boot, the instance will:

1. Install system packages for Python, Nginx, and Certbot.
2. Clone the selected branch into `/opt/almina-design/current`.
3. Create a virtual environment in `/opt/almina-design/.venv`.
4. Create `/opt/almina-design/shared/.env` if it does not exist.
5. Run `python manage.py migrate` and `collectstatic`.
6. Create a systemd service named `almina-design.service`.
7. Configure Nginx to proxy to Gunicorn on `127.0.0.1:8000`.
8. Optionally request a Let's Encrypt certificate if `domainName` and `certificateEmail` are provided.

## Post-Deploy Steps

1. Point your domain to the stack output static IP if you are using a custom domain.
2. SSH to the instance and edit `/opt/almina-design/shared/.env` to add your Stripe and EasyPost keys.
3. Restart the app after changing env vars:

```bash
sudo systemctl restart almina-design
```

4. Load sample data if desired:

```bash
sudo /opt/almina-design/.venv/bin/python /opt/almina-design/current/manage.py loaddata store/fixtures/sample_inventory.json
```

## Notes

- The default production setup keeps using SQLite on the instance for simplicity.
- Local media uploads are stored on the instance disk under `/opt/almina-design/current/media`.
- The default bootstrap flow assumes the repo is reachable from the instance. For private repositories, use a deploy key or adjust the clone URL accordingly.
