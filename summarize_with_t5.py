from transformers import T5Tokenizer, T5ForConditionalGeneration
import sys
import json
import re

def clean_diff(diff):
    # Remove git diff headers
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
    
    # Convert to meaningful text
    summary = f"Changes in files: {', '.join(files)}. "
    if changes:
        summary += "Key changes: " + " ".join(changes[:5])
    
    return summary


diff = sys.stdin.read()
cleaned_diff = clean_diff(diff)

model_name = "t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

input_text = "summarize: " + cleaned_diff
inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)

summary_ids = model.generate(inputs, max_length=300, min_length=20, length_penalty=2.0, num_beams=4, early_stopping=True)
summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

sentences = summary.split(". ")
title = sentences[0].strip() + "."
body = " ".join(sentences[1:]).strip()

print(json.dumps({
    "title": title,
    "body": body
}))