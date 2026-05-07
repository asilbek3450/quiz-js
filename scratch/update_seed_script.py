import sys

file_path = "/Users/asilbek/Desktop/AI-Projects/quiz-js/scripts/seed_arena.py"

with open(file_path, 'r') as f:
    content = f.read()

# Update the run() function to include hidden_tests
content = content.replace(
    'existing.examples       = examples_json',
    'existing.examples       = examples_json\n                existing.hidden_tests   = json.dumps(p_data.get("hidden_tests", []), ensure_ascii=False)'
)

content = content.replace(
    'examples       = examples_json,',
    'examples       = examples_json,\n                    hidden_tests   = json.dumps(p_data.get("hidden_tests", []), ensure_ascii=False),'
)

with open(file_path, 'w') as f:
    f.write(content)
print("Updated seed_arena.py successfully.")
