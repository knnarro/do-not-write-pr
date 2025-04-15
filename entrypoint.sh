#!/bin/bash

TARGET_BRANCH=${INPUT_BASE_BRANCH}

git fetch origin "$TARGET_BRANCH"
git diff origin/"$TARGET_BRANCH"...HEAD > diff.txt

PR_JSON=$(cat diff.txt | python3 /summarize_with_gpt.py "$INPUT_OPENAI_API_KEY")
PR_TITLE=$(echo "$PR_JSON" | jq -r '.title')
PR_BODY=$(echo "$PR_JSON" | jq -r '.body')

gh pr create \
  --base "$TARGET_BRANCH" \
  --head "$(git rev-parse --abbrev-ref HEAD)" \
  --title "$PR_TITLE" \
  --body "$PR_BODY"