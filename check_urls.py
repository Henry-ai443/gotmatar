import os
import re

# Parse urls.py to extract URL names
def extract_url_names(filepath):
    names = []
    with open(filepath, 'r') as f:
        content = f.read()
        # Look for name='...' or name="..."
        matches = re.findall(r"name\s*=\s*['\"]([^'\"]+)['\"]", content)
        names.extend(matches)
    return names

main_app_urls = extract_url_names('main_app/urls.py')
accounting_urls = extract_url_names('accounting/urls.py')
all_valid_urls = set(main_app_urls + accounting_urls)

templates_dirs = ['main_app/templates', 'accounting/templates']

issues = []

for d in templates_dirs:
    for root, dirs, files in os.walk(d):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                with open(path, 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        # Find {% url 'name' ... %}
                        url_tags = re.findall(r"{%\s*url\s+['\"]([^'\"]+)['\"]", line)
                        for url in url_tags:
                            if url not in all_valid_urls:
                                issues.append(f"{path}:{i+1} Invalid URL name: {url}")
                        
                        # Find {% url name as var %}
                        url_as_tags = re.findall(r"{%\s*url\s+([^'\" ]+)\s+as\s+[^%]+%}", line)
                        for url in url_as_tags:
                            if url not in all_valid_urls:
                                issues.append(f"{path}:{i+1} Invalid URL name (as var): {url}")
                        
                        # Check for hardcoded urls <a href="/something">
                        # Exclude '#', 'javascript:', 'mailto:', 'tel:' and 'http'
                        href_tags = re.findall(r"href\s*=\s*['\"]([^'\"]+)['\"]", line)
                        for href in href_tags:
                            if href.startswith('/') and not href.startswith('//'):
                                issues.append(f"{path}:{i+1} Hardcoded href: {href}")
                            
                        # Check form actions action="/something"
                        action_tags = re.findall(r"action\s*=\s*['\"]([^'\"]+)['\"]", line)
                        for action in action_tags:
                            if action.startswith('/') and not action.startswith('//'):
                                issues.append(f"{path}:{i+1} Hardcoded form action: {action}")
                                
for issue in issues:
    print(issue)
