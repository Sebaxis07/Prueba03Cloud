#!/usr/bin/env python3
"""
Security Testing Script for XSS Protection
This script tests the implemented security measures.
"""

import os
import re
from pathlib import Path

def test_security_headers(template_path):
    """Test if security headers are present in template."""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Content-Security-Policy',
            'Referrer-Policy',
            'Permissions-Policy'
        ]
        
        missing_headers = []
        for header in required_headers:
            if header not in content:
                missing_headers.append(header)
        
        if missing_headers:
            print(f"❌ {template_path}: Missing headers: {missing_headers}")
            return False
        else:
            print(f"✅ {template_path}: All security headers present")
            return True
            
    except Exception as e:
        print(f"❌ Error testing {template_path}: {e}")
        return False

def test_security_functions(template_path):
    """Test if security JavaScript functions are present."""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_functions = [
            'sanitizeHTML',
            'setSecureInnerHTML',
            'createSecureElement',
            'validateInput',
            'safeJSONParse'
        ]
        
        missing_functions = []
        for func in required_functions:
            if func not in content:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"❌ {template_path}: Missing functions: {missing_functions}")
            return False
        else:
            print(f"✅ {template_path}: All security functions present")
            return True
            
    except Exception as e:
        print(f"❌ Error testing {template_path}: {e}")
        return False

def test_django_escaping(template_path):
    """Test if Django variables are properly escaped."""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find Django variables that might not be escaped
        django_vars = re.findall(r'{{ ([^|}]+) }}', content)
        
        unescaped_vars = []
        for var in django_vars:
            if '|escape' not in var and '|safe' not in var:
                # Skip some common safe variables
                if not any(safe in var for safe in ['csrf_token', 'form.', 'url ']):
                    unescaped_vars.append(var)
        
        if unescaped_vars:
            print(f"⚠️ {template_path}: Potentially unescaped variables: {unescaped_vars}")
            return False
        else:
            print(f"✅ {template_path}: Django variables properly escaped")
            return True
            
    except Exception as e:
        print(f"❌ Error testing {template_path}: {e}")
        return False

def test_innerhtml_usage(template_path):
    """Test for unsafe innerHTML usage."""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for unsafe innerHTML usage
        unsafe_patterns = [
            r'\.innerHTML\s*=\s*`[^`]*`',
            r'\.innerHTML\s*=\s*"[^"]*"',
            r'\.innerHTML\s*=\s*\'[^\']*\'',
        ]
        
        unsafe_usage = []
        for pattern in unsafe_patterns:
            matches = re.findall(pattern, content)
            unsafe_usage.extend(matches)
        
        if unsafe_usage:
            print(f"❌ {template_path}: Unsafe innerHTML usage found: {unsafe_usage}")
            return False
        else:
            print(f"✅ {template_path}: No unsafe innerHTML usage")
            return True
            
    except Exception as e:
        print(f"❌ Error testing {template_path}: {e}")
        return False

def test_csrf_protection(template_path):
    """Test if forms include CSRF protection."""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find forms
        forms = re.findall(r'<form[^>]*>', content)
        
        if not forms:
            print(f"✅ {template_path}: No forms found (no CSRF needed)")
            return True
        
        # Check if CSRF token is present
        if '{% csrf_token %}' in content:
            print(f"✅ {template_path}: CSRF protection present")
            return True
        else:
            print(f"❌ {template_path}: Forms found but no CSRF protection")
            return False
            
    except Exception as e:
        print(f"❌ Error testing {template_path}: {e}")
        return False

def run_security_tests():
    """Run all security tests on all templates."""
    templates_dir = Path("templates")
    
    if not templates_dir.exists():
        print("❌ Templates directory not found!")
        return
    
    html_files = list(templates_dir.rglob("*.html"))
    
    if not html_files:
        print("❌ No HTML files found!")
        return
    
    print("🔍 Running Security Tests...")
    print("=" * 50)
    
    results = {
        'headers': [],
        'functions': [],
        'escaping': [],
        'innerhtml': [],
        'csrf': []
    }
    
    for html_file in html_files:
        print(f"\n📄 Testing: {html_file}")
        print("-" * 30)
        
        # Test security headers
        if test_security_headers(html_file):
            results['headers'].append(html_file)
        
        # Test security functions
        if test_security_functions(html_file):
            results['functions'].append(html_file)
        
        # Test Django escaping
        if test_django_escaping(html_file):
            results['escaping'].append(html_file)
        
        # Test innerHTML usage
        if test_innerhtml_usage(html_file):
            results['innerhtml'].append(html_file)
        
        # Test CSRF protection
        if test_csrf_protection(html_file):
            results['csrf'].append(html_file)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 SECURITY TEST SUMMARY")
    print("=" * 50)
    
    total_templates = len(html_files)
    
    for test_name, passed_files in results.items():
        passed_count = len(passed_files)
        percentage = (passed_count / total_templates) * 100
        status = "✅" if passed_count == total_templates else "⚠️"
        
        print(f"{status} {test_name.upper()}: {passed_count}/{total_templates} ({percentage:.1f}%)")
    
    # Overall security score
    total_passed = sum(len(files) for files in results.values())
    total_tests = total_templates * len(results)
    overall_score = (total_passed / total_tests) * 100
    
    print(f"\n🎯 OVERALL SECURITY SCORE: {overall_score:.1f}%")
    
    if overall_score >= 95:
        print("🛡️ EXCELLENT: High security level achieved!")
    elif overall_score >= 80:
        print("✅ GOOD: Security measures are in place")
    else:
        print("⚠️ NEEDS ATTENTION: Some security issues detected")

if __name__ == "__main__":
    run_security_tests()