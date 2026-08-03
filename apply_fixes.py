import os
import re

# We will read each file, modify it, and write it back

def standardize_forms(content):
    # Regex to find forms containing {{ form.as_p }}
    # We will replace the entire <form ...> ... </form> with the include tag
    # We need to extract the submit button text if possible
    pattern = re.compile(r'<form\b[^>]*>.*?{{ form\.as_p }}.*?<button[^>]*>([^<]+)</button>.*?</form>', re.DOTALL)
    
    def replacer(match):
        button_text = match.group(1).strip()
        return f'{{% include "main_app/form_template.html" with form=form button_text="{button_text}" %}}'

    new_content = pattern.sub(replacer, content)
    return new_content

def make_tables_responsive(content):
    # wrap <table class="table ..."> in <div class="table-responsive">
    # We need to avoid double-wrapping if it's already wrapped (though none are)
    # We just replace '<table class="table' with '<div class="table-responsive">\n<table class="table'
    # And replace '</table>' with '</table>\n</div>'
    
    # Let's find each <table>...</table> block
    # Note: re.sub might be tricky if there are nested tables, but here we don't have them.
    # A safe way is to find <table class="table... and the corresponding </table>
    
    def replace_table(match):
        return f'<div class="table-responsive">\n{match.group(0)}\n</div>'
    
    # We will only wrap it if it's not already inside a table-responsive div.
    # Actually, simpler: 
    # Just look for <table class="table and wrap that specific block.
    # But python regex non-greedy dotall:
    pattern = re.compile(r'<table\b[^>]*class="[^"]*table[^"]*"[^>]*>.*?</table>', re.DOTALL | re.IGNORECASE)
    
    def table_replacer(match):
        table_str = match.group(0)
        # check if it already has table-responsive before it... hard with regex in python easily.
        # But we know none of them are responsive right now based on audit.
        return f'<div class="table-responsive">\n{table_str}\n</div>'
        
    return pattern.sub(table_replacer, content)

def improve_empty_states(content):
    # find {% empty %} \n <tr><td colspan="X"> TEXT </td></tr>
    pattern = re.compile(r'({%\s*empty\s*%}\s*)<tr>\s*<td[^>]*>(.*?)</td>\s*</tr>', re.DOTALL | re.IGNORECASE)
    
    def replacer(match):
        empty_tag = match.group(1)
        text = match.group(2).strip()
        # Find if there's an action, we might just put text for now, styled.
        new_empty = (
            f'{empty_tag}'
            f'<tr><td colspan="100%" class="text-center py-5">'
            f'<div class="empty-state">'
            f'<i class="fas fa-folder-open text-muted fa-3x mb-3"></i>'
            f'<h5 class="text-muted">{text}</h5>'
            f'</div>'
            f'</td></tr>'
        )
        return new_empty

    return pattern.sub(replacer, content)

for root, dirs, files in os.walk('.'):
    if 'venv' in root or '.git' in root or 'Lib' in root or 'lib' in root or 'rest_framework' in root or 'admin_doc' in root: continue
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            original_content = content
            
            if '{{ form.as_p }}' in content:
                content = standardize_forms(content)
            
            if '<table ' in content:
                content = make_tables_responsive(content)
                
            if '{% empty %}' in content:
                content = improve_empty_states(content)
                
            if content != original_content:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(content)
                print(f"Updated: {path}")

