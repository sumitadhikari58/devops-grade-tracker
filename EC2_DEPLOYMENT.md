# AWS EC2 Live Deployment Guide

This guide deploys DevOps Grade Tracker on an AWS EC2 Ubuntu 22.04 server with Jenkins and Docker.

## Section 1: Launch EC2 Instance

1. Go to **AWS Console** → **EC2** → **Launch Instance**.
2. Name the instance:

```text
devops-grade-tracker-server
```

3. Select AMI: **Ubuntu Server 22.04 LTS (Free Tier)**.
4. Select instance type: **t2.micro (Free Tier)**.
5. Create a key pair:

   - Click **Create new key pair**.
   - Name: `grade-tracker-key`.
   - Type: **RSA**.
   - Format: `.pem`.
   - Download and save the `.pem` file. You cannot re-download it later.

6. Network settings → **Edit**:

   - Allow **SSH**, port `22`, from **My IP**.
   - Add rule: **Custom TCP**, port `8080`, source `0.0.0.0/0` for Jenkins.
   - Add rule: **Custom TCP**, port `5050`, source `0.0.0.0/0` for the development app.
   - Add rule: **HTTP**, port `80`, source `0.0.0.0/0` for the production app.

7. Storage: set root volume to `20GB`.
8. Click **Launch Instance**.
9. Copy the **Public IPv4 address**, for example:

```text
54.123.45.67
```

## Section 2: Connect to EC2

On your Mac terminal, secure the downloaded key:

```bash
chmod 400 ~/Downloads/grade-tracker-key.pem
```

Connect to the EC2 instance:

```bash
ssh -i ~/Downloads/grade-tracker-key.pem ubuntu@YOUR_EC2_IP
```

Example:

```bash
ssh -i ~/Downloads/grade-tracker-key.pem ubuntu@54.123.45.67
```

If the connection works, your terminal prompt will change to the Ubuntu server.

## Section 3: Upload Project to EC2

From your local machine, upload the project:

```bash
scp -i ~/Downloads/grade-tracker-key.pem -r ~/Desktop/devops-grade-tracker ubuntu@YOUR_EC2_IP:/home/ubuntu/
```

Then SSH into the server:

```bash
ssh -i ~/Downloads/grade-tracker-key.pem ubuntu@YOUR_EC2_IP
```

Move into the project:

```bash
cd /home/ubuntu/devops-grade-tracker
```

## Section 4: Install Jenkins and Docker

Run the installer:

```bash
chmod +x scripts/install.sh
sudo ./scripts/install.sh
```

The script installs:

- Java 17
- Jenkins
- Docker
- Jenkins Docker permissions

At the end, the script prints:

- Jenkins URL
- Jenkins initial admin password

Open Jenkins:

```text
http://YOUR_EC2_IP:8080
```

Paste the initial admin password when Jenkins asks for it.

## Section 5: Configure Jenkins

1. Click **Install suggested plugins**.
2. Create the first admin user.
3. Confirm Jenkins URL:

```text
http://YOUR_EC2_IP:8080
```

4. Install or confirm these Jenkins plugins:

   - Git
   - GitHub
   - Pipeline
   - Multibranch Pipeline

5. Restart Jenkins if Jenkins asks for a restart.

## Section 6: Connect Jenkins to GitHub

Follow `WEBHOOK_SETUP.md` to configure:

- GitHub repository
- GitHub webhook
- GitHub Personal Access Token
- Jenkins Multibranch Pipeline job

Expected Jenkins webhook endpoint:

```text
http://YOUR_EC2_IP:8080/github-webhook/
```

Expected Jenkins job name:

```text
grade-tracker-pipeline
```

## Section 7: Manual Deployment Test

Before testing Jenkins, verify Docker deployment manually.

Development deployment:

```bash
cd /home/ubuntu/devops-grade-tracker
chmod +x scripts/deploy.sh
./scripts/deploy.sh dev
```

Open:

```text
http://YOUR_EC2_IP:5050
```

Production deployment:

```bash
./scripts/deploy.sh prod
```

Open:

```text
http://YOUR_EC2_IP
```

## Section 8: Jenkins Branch Deployment Strategy

The Jenkins pipeline deploys based on branch:

- Push to `develop` → deploys development container `grade-tracker-dev` on port `5050`.
- Push to `main` → deploys production container `grade-tracker-prod` on port `80`.

Development test:

```bash
git checkout develop
git add .
git commit -m "deploy develop"
git push origin develop
```

Open:

```text
http://YOUR_EC2_IP:5050
```

Production test:

```bash
git checkout main
git merge develop
git push origin main
```

Open:

```text
http://YOUR_EC2_IP
```

## Section 9: Verify Live Deployment

Check running containers on EC2:

```bash
docker ps
```

Check development health:

```bash
curl http://localhost:5050/health
```

Check production health:

```bash
curl http://localhost:80/health
```

Expected response:

```json
{"env":"Development","status":"ok","students":0}
```

or:

```json
{"env":"Production","status":"ok","students":0}
```

## Section 10: Common Troubleshooting

If Jenkins cannot run Docker commands:

```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

If the app is not reachable:

```bash
docker ps
sudo ufw status
```

Also confirm the EC2 security group allows:

- `8080` for Jenkins
- `5050` for development
- `80` for production

If the webhook does not trigger:

- Check GitHub webhook recent deliveries.
- Confirm the payload URL is `http://YOUR_EC2_IP:8080/github-webhook/`.
- Confirm Jenkins Multibranch Pipeline has GitHub credentials.
- Click **Scan Repository Now** in Jenkins.

If port `80` fails:

```bash
sudo systemctl stop apache2 2>/dev/null || true
sudo systemctl stop nginx 2>/dev/null || true
./scripts/deploy.sh prod
```
