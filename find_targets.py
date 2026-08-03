import os, re
for root, dirs, files in os.walk('.'):
    if 'venv' in root or '.git' in root: continue
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            with open(path, 'r') as file:
                content = file.read()
                if '{{ form.as_p }}' in content:
                    print(f"FORM: {path}")
                if '<table ' in content:
                    print(f"TABLE: {path}")
                if '{% empty %}' in content:
                    print(f"EMPTY: {path}")
