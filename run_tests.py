#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner


def run_tests():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.test_settings')
    django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    try:
        import coverage
        cov = coverage.Coverage()
        cov.start()
        
        failures = test_runner.run_tests([
            'students.tests',
            'exams.tests', 
            'core.tests',
        ])
        
        cov.stop()
        cov.save()
        
        print("\n" + "="*50)
        print("COVERAGE REPORT")
        print("="*50)
        cov.report()
        
        cov.html_report(directory='htmlcov')
        print(f"\nHTML coverage report generated in 'htmlcov' directory")
        
    except ImportError:
        print("Coverage not available. Install with: pip install coverage")
        failures = test_runner.run_tests([
            'students.tests',
            'exams.tests',
            'core.tests',
        ])
    
    return failures


def run_specific_tests(test_path):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.test_settings')
    django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    failures = test_runner.run_tests([test_path])
    return failures


if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_path = sys.argv[1]
        failures = run_specific_tests(test_path)
    else:
        failures = run_tests()
    
    sys.exit(bool(failures))