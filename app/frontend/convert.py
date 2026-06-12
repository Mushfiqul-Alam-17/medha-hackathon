import re

html_file = r'c:\Users\mushf\Downloads\medha_redesign\index.html'

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract CSS
style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
if style_match:
    with open(r'c:\Users\mushf\Downloads\Medha\app\frontend\src\index.css', 'w', encoding='utf-8') as f:
        f.write(style_match.group(1))

# Extract body
body_match = re.search(r'<body>(.*?)<script>', content, re.DOTALL)
if body_match:
    body = body_match.group(1)
    
    # Simple replacements
    body = body.replace('class=', 'className=')
    body = body.replace('onclick=', 'onClick=')
    body = body.replace('<hr className=\"divider\" style=\"margin:24px 0\">', '<hr className=\"divider\" style={{margin:\"24px 0\"}} />')
    body = body.replace('<hr className=\"divider\" style=\"margin:24px 0;width:100%\">', '<hr className=\"divider\" style={{margin:\"24px 0\", width:\"100%\"}} />')
    body = body.replace('<hr className=\"divider\" style=\"margin:20px 0\">', '<hr className=\"divider\" style={{margin:\"20px 0\"}} />')
    body = re.sub(r'<br>', '<br />', body)
    body = re.sub(r'<!--(.*?)-->', r'{/* \1 */}', body, flags=re.DOTALL)
    
    # Fix onClicks for routing
    body = re.sub(r'onClick=\"showScreen\(\'([^\']+)\'\)\"', r'onClick={() => setView(\"\1\")}', body)
    # Remove other string onClicks to prevent React errors
    body = re.sub(r'onClick=\"([^\"]+)\"', r'', body)
    
    # Convert style="..." to style={{...}}
    def style_replacer(m):
        style_str = m.group(1)
        if not style_str.strip(): return 'style={{}}'
        parts = style_str.split(';')
        out = []
        for p in parts:
            if not p.strip(): continue
            if ':' not in p: continue
            k, v = p.split(':', 1)
            k = k.strip()
            v = v.strip()
            k_camel = re.sub(r'-([a-z])', lambda x: x.group(1).upper(), k)
            out.append(f'{k_camel}: "{v}"')
        return 'style={{' + ', '.join(out) + '}}'
        
    body = re.sub(r'style="([^"]*)"', style_replacer, body)
    
    # Fix SVG attributes
    body = re.sub(r'stroke-width=', 'strokeWidth=', body)
    body = re.sub(r'stroke-linecap=', 'strokeLinecap=', body)
    body = re.sub(r'stroke-linejoin=', 'strokeLinejoin=', body)
    body = re.sub(r'stroke-dasharray=', 'strokeDasharray=', body)
    body = re.sub(r'stroke-dashoffset=', 'strokeDashoffset=', body)
    body = re.sub(r'fill-rule=', 'fillRule=', body)
    body = re.sub(r'clip-rule=', 'clipRule=', body)
    body = re.sub(r'transform-origin=', 'transformOrigin=', body)
    body = re.sub(r'preserveAspectRatio=', 'preserveAspectRatio=', body)
    
    # Dynamic active classes for screens based on 'view' state
    body = re.sub(r'id="s-([^"]+)" className="screen[^"]*"', r'id="s-\1" className={`screen ${view === "\1" ? "active" : ""}`}', body)
    
    # Create the React component wrapper
    jsx = f'''
import React, {{ useEffect }} from "react";

export default function DesignTemplate({{ view, setView }}) {{
  
  useEffect(() => {{
    // Scroll to top on view change
    window.scrollTo({{top: 0, behavior: 'instant'}});
  }}, [view]);

  return (
    <>
      {body}
    </>
  );
}}
'''
    
    with open(r'c:\Users\mushf\Downloads\Medha\app\frontend\src\DesignTemplate.js', 'w', encoding='utf-8') as f:
        f.write(jsx)
    print("Successfully wrote index.css and DesignTemplate.js")
