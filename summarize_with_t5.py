from transformers import T5Tokenizer, T5ForConditionalGeneration
import sys
import json

diff = sys.stdin.read()

model_name = "t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

input_text = "summarize: " + diff.replace("\n", " ")
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