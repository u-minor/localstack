#!/bin/bash
## install commitizen globally
echo "install commitizen globally..."
npm install -g --no-progress --silent commitizen cz-conventional-changelog
echo '{ "path": "cz-conventional-changelog" }' >~/.czrc

## add safe.directory to global git config
echo "add safe directory to global git config..."
git config --global --add safe.directory "${CONTAINER_WORKSPACE_FOLDER}"

## fix permission of .venv
echo "fix permission of .venv..."
sudo chown vscode:vscode .venv

## fix permission of .venv
echo "fix permission of localstack folders..."
for folder in /usr/lib/localstack /var/lib/localstack; do
  sudo mkdir -p $folder
  sudo chown vscode:vscode $folder
done
