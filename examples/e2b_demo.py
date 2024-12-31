#!/usr/bin/env python3

import os
from src.e2b import execute_code, execute_file

# Enable debug output
os.environ["DEBUG_LEVEL"] = "1"

print("\n=== Direct Code Execution ===")
code = """
import math

def calculate_circle_area(radius):
    return math.pi * radius ** 2

print(f"Area of circle with radius 5: {calculate_circle_area(5):.2f}")
"""

stdout, stderr = execute_code(code)
print("\nOutput:", stdout)
if stderr:
    print("Errors:", stderr)

print("\n=== File Execution ===")
# Create a temporary file
with open("temp_script.py", "w") as f:
    f.write("""
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print("First 5 Fibonacci numbers:")
for i in range(5):
    print(f"fibonacci({i}) = {fibonacci(i)}")
""")

try:
    stdout, stderr = execute_file("temp_script.py")
    print("\nOutput:", stdout)
    if stderr:
        print("Errors:", stderr)
finally:
    os.remove("temp_script.py") 