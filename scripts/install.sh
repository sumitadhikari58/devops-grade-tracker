#!/usr/bin/env bash
set -e

if [ "$(id -u)" -ne 0 ]; then
  echo "Run this installer with sudo: sudo ./scripts/install.sh"
  exit 1
fi

echo "Step 1/7: Updating Ubuntu packages..."
apt-get update
apt-get upgrade -y

echo "Step 2/7: Installing Java 17..."
apt-get install -y openjdk-17-jdk wget curl gnupg ca-certificates

echo "Step 3/7: Installing Jenkins..."
wget -q -O /usr/share/keyrings/jenkins-keyring.asc \
  https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" \
  > /etc/apt/sources.list.d/jenkins.list
apt-get update
apt-get install -y jenkins

echo "Step 4/7: Installing Docker..."
apt-get install -y docker.io
systemctl enable docker
systemctl start docker

echo "Step 5/7: Adding Jenkins user to Docker group..."
usermod -aG docker jenkins

echo "Step 6/7: Starting Jenkins..."
systemctl enable jenkins
systemctl start jenkins

echo "Step 7/7: Installation complete."
echo "Jenkins: http://$(curl -s ifconfig.me):8080"
echo "Admin password:"
cat /var/lib/jenkins/secrets/initialAdminPassword
