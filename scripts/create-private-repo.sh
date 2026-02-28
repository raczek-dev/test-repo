#!/bin/bash
# Create private GitHub repo with lukasz-kaniowski as admin

REPO_NAME="${1:-new-repo}"
DESCRIPTION="${2:-Created by Raczek}"
TOKEN="${GITHUB_TOKEN}"

echo "Creating private repo: $REPO_NAME"

# Create repo
curl -s -H "Authorization: token $TOKEN" \
  -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d "{
    \"name\": \"$REPO_NAME\",
    \"description\": \"$DESCRIPTION\",
    \"private\": true,
    \"auto_init\": true
  }"

# Add collaborator
echo "Adding lukasz-kaniowski as admin..."
curl -s -H "Authorization: token $TOKEN" \
  -X PUT \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/raczek-dev/$REPO_NAME/collaborators/lukasz-kaniowski" \
  -d '{"permission": "admin"}'

echo "Done! https://github.com/raczek-dev/$REPO_NAME"
