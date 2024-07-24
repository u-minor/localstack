#!/bin/bash
## install commitizen globally
echo "install commitizen globally..."
npm install -g --no-progress --silent commitizen cz-conventional-changelog
echo '{ "path": "cz-conventional-changelog" }' >~/.czrc
