#!/usr/bin/env python3
"""
Security Enhancement Script for HTML Templates
This script systematically adds XSS protection to all HTML templates.
"""

import os
import re
from pathlib import Path

def add_security_headers(template_content):
    """Add security headers to HTML templates."""
    security_headers = '''    <!-- Security Headers -->
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    <meta http-equiv="X-Frame-Options" content="DENY">
    <meta http-equiv="X-XSS-Protection" content="1; mode=block">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com; style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; img-src 'self' data: blob:; font-src 'self' https://cdn.tailwindcss.com; connect-src 'self'; frame-ancestors 'none';">
    <meta http-equiv="Referrer-Policy" content="strict-origin-when-cross-origin">
    <meta http-equiv="Permissions-Policy" content="geolocation=(), microphone=(), camera=()">'''
    
    # Check if security headers already exist
    if 'X-Content-Type-Options' in template_content:
        return template_content
    
    # Add security headers after the viewport meta tag
    template_content = re.sub(
        r'(<meta name="viewport" content="width=device-width, initial-scale=1\.0">)',
        r'\1\n' + security_headers,
        template_content
    )
    
    return template_content

def add_security_functions(template_content):
    """Add security JavaScript functions to templates."""
    security_functions = '''        // Sanitize function to prevent XSS
        function sanitizeHTML(str) {
            if (typeof str !== 'string') return '';
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        }
        
        // Secure innerHTML usage
        function setSecureInnerHTML(element, content) {
            if (element && content) {
                element.textContent = content;
            }
        }
        
        // Secure DOM manipulation
        function createSecureElement(tag, className, textContent) {
            const element = document.createElement(tag);
            if (className) element.className = className;
            if (textContent) element.textContent = textContent;
            return element;
        }
        
        // Validate and sanitize user input
        function validateInput(input, maxLength = 1000) {
            if (typeof input !== 'string') return '';
            return input.substring(0, maxLength).replace(/[<>]/g, '');
        }
        
        // Secure JSON parsing
        function safeJSONParse(str) {
            try {
                return JSON.parse(str);
            } catch (e) {
                console.error('Invalid JSON:', e);
                return null;
            }
        }'''
    
    # Check if security functions already exist
    if 'sanitizeHTML' in template_content:
        return template_content
    
    # Add security functions after the first script tag
    script_pattern = r'(<script>)'
    if re.search(script_pattern, template_content):
        template_content = re.sub(
            script_pattern,
            r'\1\n' + security_functions + '\n',
            template_content,
            count=1
        )
    
    return template_content

def escape_django_variables(template_content):
    """Add escape filters to Django template variables."""
    # Pattern to match Django variables that should be escaped
    patterns = [
        (r'{{ ([^}]+) }}', r'{{ \1|escape }}'),
        (r'{{ ([^|}]+)\|([^}]+) }}', r'{{ \1|\2|escape }}'),
    ]
    
    for pattern, replacement in patterns:
        template_content = re.sub(pattern, replacement, template_content)
    
    return template_content

def secure_innerhtml_usage(template_content):
    """Replace unsafe innerHTML usage with secure alternatives."""
    # Replace innerHTML with textContent where appropriate
    template_content = re.sub(
        r'\.innerHTML\s*=\s*`([^`]+)`',
        r'.textContent = sanitizeHTML(`\1`)',
        template_content
    )
    
    # Replace innerHTML with createSecureElement where appropriate
    template_content = re.sub(
        r'\.innerHTML\s*=\s*`([^`]+)`',
        r'.appendChild(createSecureElement("div", "", `\1`))',
        template_content
    )
    
    return template_content

def enhance_template_security(template_path):
    """Enhance a single template with security measures."""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply security enhancements
        content = add_security_headers(content)
        content = add_security_functions(content)
        content = escape_django_variables(content)
        content = secure_innerhtml_usage(content)
        
        # Write back the enhanced content
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Enhanced: {template_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error enhancing {template_path}: {e}")
        return False

def main():
    """Main function to enhance all HTML templates."""
    templates_dir = Path("templates")
    
    if not templates_dir.exists():
        print("❌ Templates directory not found!")
        return
    
    # Find all HTML files
    html_files = list(templates_dir.rglob("*.html"))
    
    if not html_files:
        print("❌ No HTML files found!")
        return
    
    print(f"🔍 Found {len(html_files)} HTML templates")
    print("🛡️ Starting security enhancement...")
    
    success_count = 0
    
    for html_file in html_files:
        if enhance_template_security(html_file):
            success_count += 1
    
    print(f"\n📊 Security Enhancement Complete!")
    print(f"✅ Successfully enhanced: {success_count}/{len(html_files)} templates")
    
    if success_count < len(html_files):
        print("⚠️ Some templates may need manual review")

if __name__ == "__main__":
    main() 