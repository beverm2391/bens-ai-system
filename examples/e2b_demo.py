#!/usr/bin/env python3

import os
from src.e2b.execute import execute_code
from src.e2b.execute_file import execute_file

def run_demos():
    print("\n=== Direct Code Execution Demo ===")
    
    # Simple print
    print("\n1. Simple print statement:")
    stdout, stderr = execute_code('print("Hello from E2B sandbox!")')
    print(f"Stdout: {stdout}")
    print(f"Stderr: {stderr}")
    
    # Math calculation
    print("\n2. Math calculation:")
    stdout, stderr = execute_code('result = 42 * 2; print(f"The answer is {result}")')
    print(f"Stdout: {stdout}")
    print(f"Stderr: {stderr}")
    
    # Error handling
    print("\n3. Error handling:")
    stdout, stderr = execute_code('print(undefined_variable)')
    print(f"Stdout: {stdout}")
    print(f"Stderr: {stderr}")
    
    print("\n=== File Execution Demo ===")
    
    # Create a test file
    test_file = "examples/test_code.py"
    with open(test_file, "w") as f:
        f.write('''
import math

def calculate_circle_area(radius):
    return math.pi * radius ** 2

radius = 5
area = calculate_circle_area(radius)
print(f"Area of circle with radius {radius} is {area:.2f}")
''')
    
    print("\n4. Executing Python file:")
    stdout, stderr = execute_file(test_file)
    print(f"Stdout: {stdout}")
    print(f"Stderr: {stderr}")
    
    # Clean up
    os.remove(test_file)

if __name__ == "__main__":
    run_demos() 