#!/bin/bash
echo "Init instance"
sudo apt-get update
echo "Install docker"
sudo apt-get install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
echo "Install powerline fonts"
git clone https://github.com/powerline/fonts.git
cd fonts
./install.sh
cd ..
rm -rf fonts
echo "Install zsh"
sudo apt update 
sudo apt install zsh -y
sudo chsh -s $(which zsh)
sudo wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true
zsh -c 'git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-/home/ubuntu/.oh-my-zsh/custom}/plugins/zsh-autosuggestions'
zsh -c 'git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-/home/ubuntu/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting'
sudo sed -i 's/plugins=(git)/plugins=(git zsh-autosuggestions zsh-syntax-highlighting)/' /home/ubuntu/.zshrc
echo "Download metadata"
# Get before the key and save it in the metadata with awk '{printf "%s\\n", $0}' ~/.ssh/id_rsa
curl -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/instance/attributes/BITBUCKET_KEY | sed 's/\\n/\n/g' > /home/ubuntu/.ssh/id_rsa
chmod 600 /home/ubuntu/.ssh/id_rsa && ssh-keyscan gitlab.com >> /home/ubuntu/.ssh/known_hosts
cd /home/ubuntu
mkdir apps
cd apps
echo "Clone repositories"
git clone https://gitlab.com/misw4203-cloud/misw42020-back.git web-backend
git clone https://github.com/Juan-Motta/portainer-docker.git portainer
cd portainer
sudo docker compose up -d
cd ..
cd web-backend
git switch develop
echo "Create .env file"
public_ip=$(curl -s -H "Metadata-Flavor: Google" "http://169.254.169.254/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip")
declare -A metadata_keys
metadata_keys=(
    ["DB_USER"]=""
    ["DB_PASSWORD"]=""
    ["DB_HOST"]=""
    ["DB_PORT"]=""
    ["DB_NAME"]=""
    ["DB_USER_TEST"]=""
    ["DB_PASSWORD_TEST"]=""
    ["DB_HOST_TEST"]=""
    ["DB_PORT_TEST"]=""
    ["DB_NAME_TEST"]=""
    ["CELERY_BROKER_HOST"]=""
    ["CELERY_BROKER_PORT"]=""
    ["GCP_PROJECT_ID"]=""
    ["GCP_CREDENTIALS_BASE64"]=""
    ["BACKEND_URL"]="http://$public_ip"
)
env_file=".env"
> "$env_file"
for key in "${!metadata_keys[@]}"; do
    value=$(curl -f -s -H "Metadata-Flavor: Google" "http://169.254.169.254/computeMetadata/v1/instance/attributes/$key" 2>/dev/null)
    if [ $? -ne 0 ] || [ -z "$value" ]; then
        value="${metadata_keys[$key]}"
    fi
    echo "$key=\"$value\"" >> "$env_file"
done
cd compose/base
sudo docker compose -f docker-compose.backend.yml up -d