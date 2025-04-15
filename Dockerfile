FROM --platform=linux/amd64 python:3.11-slim

RUN apt-get update && apt-get install -y git curl jq gpg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list && \
    apt-get update && apt-get install -y gh

COPY entrypoint.sh /entrypoint.sh
COPY summarize_with_gpt.py /summarize_with_gpt.py
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]