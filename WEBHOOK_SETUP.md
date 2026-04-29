# GitHub Webhook Setup Guide

This guide connects GitHub push events to Jenkins so the DevOps Grade Tracker pipeline runs automatically when code is pushed to `develop` or `main`.

## Section 1: Create GitHub Repository

1. Go to [github.com](https://github.com) and sign in.
2. Click **New Repository**.
3. Name the repository `devops-grade-tracker`.
4. Set visibility to **Public**.
5. Do **not** add a README, `.gitignore`, or license because the project files already exist locally.
6. Click **Create Repository**.

## Section 2: Push Local Code to GitHub

Run these commands in order from your terminal:

```bash
cd ~/Desktop/devops-grade-tracker
git init
git add .
git commit -m "Initial commit - DevOps Grade Tracker"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/devops-grade-tracker.git
git push -u origin main
```

Then create and push the `develop` branch:

```bash
git checkout -b develop
git push -u origin develop
```

Branch purpose:

- `develop` deploys the development app on port `5050`.
- `main` deploys the production app on port `80`.

## Section 3: Configure GitHub Webhook

1. Go to your GitHub repository.
2. Click **Settings** → **Webhooks** → **Add webhook**.
3. Set **Payload URL** to:

```text
http://YOUR_EC2_IP:8080/github-webhook/
```

4. Set **Content type** to:

```text
application/json
```

5. Select **Just the push event**.
6. Check **Active**.
7. Click **Add webhook**.

How to verify the webhook works:

- Push any change to GitHub.
- Go to **GitHub** → **Settings** → **Webhooks** → **Recent Deliveries**.
- The latest delivery should show a green tick with a `200` response.

## Section 4: Configure Jenkins for GitHub Webhook

1. Open Jenkins:

```text
http://YOUR_EC2_IP:8080
```

2. Go to **Manage Jenkins** → **Configure System**.
3. Find the **GitHub** section and click **Add GitHub Server**.
4. Add GitHub credentials using a Personal Access Token:

   - Go to **GitHub** → **Settings** → **Developer Settings**.
   - Click **Personal Access Tokens** → **Generate new token**.
   - Select scopes:
     - `repo`
     - `admin:repo_hook`
   - Copy the token.
   - In Jenkins, click **Add Credentials**.
   - Kind: **Secret text**.
   - Secret: paste the GitHub token.
   - ID: `github-token`.
   - Save the credentials.

5. Create the Multibranch Pipeline job:

   - Click **New Item**.
   - Select **Multibranch Pipeline**.
   - Name it `grade-tracker-pipeline`.
   - Click **OK**.
   - Under **Branch Sources**, choose **GitHub**.
   - Credentials: `github-token`.
   - Repository URL: your GitHub repository URL.
   - Behaviors: **Discover branches** → **All branches**.
   - Build Configuration: **by Jenkinsfile**.
   - Under **Scan Multibranch Pipeline Triggers**, check **Periodically if not otherwise run**.
   - Set the interval to `1 minute`.
   - Click **Save**.

## Section 5: Test the Full Webhook Flow

1. Make a small change in `app.py`, such as adding a comment.
2. Commit the change:

```bash
git add .
git commit -m "test webhook trigger"
```

3. Push to the development branch:

```bash
git push origin develop
```

4. Watch Jenkins. The `grade-tracker-pipeline` job should auto-trigger within about 30 seconds.
5. The Jenkins pipeline should run all 6 stages automatically:

   - Git Checkout
   - Code Lint
   - Unit Tests
   - Docker Build
   - Deploy to Development or Production
   - Health Check

6. After a successful `develop` build, open:

```text
http://YOUR_EC2_IP:5050
```

7. After a successful `main` build, open:

```text
http://YOUR_EC2_IP
```
