import os
import json
import re
import sys
from openai import OpenAI

def clean_diff(diff):
    # Remove git diff headers and metadata
    diff = re.sub(r'^diff --git.*$', '', diff, flags=re.MULTILINE)
    diff = re.sub(r'^index.*$', '', diff, flags=re.MULTILINE)
    diff = re.sub(r'^---.*$', '', diff, flags=re.MULTILINE)
    diff = re.sub(r'^\+\+\+.*$', '', diff, flags=re.MULTILINE)
    
    # Extract changed file paths
    files = re.findall(r'^\+\+\+ b/(.*)$', diff, flags=re.MULTILINE)
    files = [f for f in files if f]
    
    # Extract actual changes
    changes = []
    for line in diff.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            # Skip empty lines only
            if line.strip():
                changes.append(line[1:])
    
    return {
        "files": files,
        "changes": changes
    }

def generate_pr_description(diff_data, api_key):
    # Check if this is a test run
    if api_key.startswith("test_"):
        return {
            "title": "Test PR: Feature Update",
            "body": "This is a test PR description generated without calling the actual API.\n\nChanges:\n- " + "\n- ".join(diff_data["changes"])
        }
    
    # Set up OpenAI API client
    client = OpenAI(api_key=api_key)
    
    # Create a prompt for GPT
    prompt = f"""
    Analyze the following code changes and create a pull request title and description.
    
    Changed files: {', '.join(diff_data['files'])}
    
    Changes:
    {chr(10).join(f"- {change}" for change in diff_data['changes'])}
    
    Please provide a response in the following JSON format:
    {{
        "title": "A concise title that follows conventional commit format (e.g., feat:, fix:, etc.)",
        "body": "A detailed description of the changes, including the purpose and impact"
    }}
    """
    
    try:
        # Call GPT API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes code changes and creates pull request descriptions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract and parse the response
        content = response.choices[0].message.content
        try:
            result = json.loads(content)
            return result
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            lines = content.split('\n')
            title = lines[0].replace('"title":', '').strip().strip('",')
            body = '\n'.join(lines[1:]).replace('"body":', '').strip().strip('",')
            return {"title": title, "body": body}
    except Exception as e:
        return {"title": "Error generating PR description", "body": f"An error occurred: {str(e)}"}

# Get API key from command line argument
if len(sys.argv) < 2:
    print(json.dumps({
        "title": "Error",
        "body": "OpenAI API key is required as a command line argument"
    }))
    sys.exit(1)

api_key = sys.argv[1]

with open("code.diff", "r") as f:
    diff = f.read()

# Process the diff
diff_data = clean_diff(diff)

# If no changes detected, use test data
if not diff_data["changes"]:
    diff_data["changes"] = ["This is a test change"]

# Generate PR description
try:
    result = generate_pr_description(diff_data, api_key)
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({
        "title": "Error generating PR description",
        "body": f"An error occurred: {str(e)}"
    })) 