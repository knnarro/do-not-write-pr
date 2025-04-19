# AI PR Generator

[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-AI%20PR%20Generator-blue.svg?colorA=24292e&colorB=0366d6&style=flat&longCache=true&logo=github)](https://github.com/marketplace/actions/ai-pr-generator)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AI PR Generator** is a GitHub Action that automatically generates meaningful PR (Pull Request) titles and descriptions by analyzing Git diffs. It utilizes OpenAI's GPT-4 model to understand code changes and create structured PR descriptions.

## Features

- ✨ **Automatic PR Creation**: Automatically creates PRs when pushing to branches.
- 🤖 **AI-Powered Summaries**: Uses GPT-4 to analyze code changes and generate meaningful summaries.
- 🌐 **Multi-Language Support**: Supports generating PR descriptions in various languages including English, Korean, and more.
- 📋 **Structured Format**: Provides PR titles in '[TYPE] Description' format and systematic body structure.

## Usage

### Basic Setup

Add the following configuration to your workflow file (`.github/workflows/auto-pr.yml`):

```yaml
name: Auto PR Generator

on:
  push:
    branches:
      - feature/**
      - fix/**
      # Add your branch patterns as needed

jobs:
  create-pr:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Generate PR with AI
        uses: knnarro/ai-pr-generator@v1
        with:
          base_branch: main  # Target branch (main, develop, etc.)
          language: en       # Optional, defaults to English
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Input Parameters

| Parameter | Required | Description | Default |
|-----------|----------|-------------|---------|
| `base_branch` | ✅ | Target branch to create PR against (e.g., main, develop) | - |
| `language` | ❌ | Language for PR description (e.g., en, ko, zh) | `en` (English) |

### Environment Variables

You need to set the following environment variables:

| Environment Variable | Description |
|----------------------|-------------|
| `GH_TOKEN` | GitHub token for API access |
| `OPENAI_API_KEY` | OpenAI API key for generating descriptions |

## How It Works

1. When a push occurs to a specified branch pattern (e.g., `feature/**`), the action is triggered.
2. The action analyzes the differences between the target branch and the current branch.
3. It uses the GPT-4 model to understand the code changes and generate an appropriate PR title and description.
4. A PR is automatically created with the generated title and description.

## Example Output

**PR Title:**
```
[FEAT] Implement User Authentication
```

**PR Body:**
```
This PR includes the following changes:

### ✨ User Authentication Feature
- Implement JWT-based authentication system
- Add login and registration API endpoints
- Add authentication middleware

### 🔧 Configuration Updates
- Add JWT secret key to environment variables
- Update user model schema

This PR adds security-related features. Please focus your review on the authentication logic and token handling.
```

## Important Notes

- Using the OpenAI API may incur costs.
- Be cautious as sensitive code or confidential information included in changes will be sent to the OpenAI API.
- If a PR already exists, a new one will not be created.
