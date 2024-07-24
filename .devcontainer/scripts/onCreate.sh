#!/bin/bash
GROUP=$USER

## add safe.directory to global git config
echo "add safe directory to global git config..."
git config --global --add safe.directory "${CONTAINER_WORKSPACE_FOLDER}"

## fix permission of .venv
echo "fix permission of .venv..."
sudo chown ${USER}:${GROUP} .venv

## fix permission of .venv
echo "fix permission of localstack folders..."
for folder in /usr/lib/localstack /var/lib/localstack; do
  sudo mkdir -p $folder
  sudo chown ${USER}:${GROUP} $folder
done
