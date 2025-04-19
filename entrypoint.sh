#!/bin/bash

TARGET_BRANCH=${INPUT_BASE_BRANCH}
LANGUAGE=${INPUT_LANGUAGE}
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

git config --global --add safe.directory /github/workspace
git fetch origin "$TARGET_BRANCH"
git diff origin/"$TARGET_BRANCH"...HEAD > code.diff

EXISTING_PR=$(gh pr list --head "$CURRENT_BRANCH" --base "$TARGET_BRANCH" --json number --jq '.[0].number')

if [ -n "$EXISTING_PR" ]; then
  exit 0
fi

PR_JSON=$(cat code.diff | python3 /summarize_with_gpt.py "$OPENAI_API_KEY" "$LANGUAGE")
PR_TITLE=$(echo "$PR_JSON" | jq -r '.title')
PR_BODY=$(echo "$PR_JSON" | jq -r '.body')

gh pr create \
  --base "$TARGET_BRANCH" \
  --head "$CURRENT_BRANCH" \
  --title "$PR_TITLE" \
  --body "$PR_BODY"
