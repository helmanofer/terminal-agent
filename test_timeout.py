#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main3 import ShellResult
from plumbum import local
import time

def test_timeout_functionality():
    """Test the timeout functionality of shell commands"""
    print("Testing timeout functionality...")
    
    # Test 1: Quick command (should not timeout)
    print("\n1. Testing quick command (should succeed):")
    start_time = time.time()
    try:
        bash = local["bash"]
        retcode, stdout, stderr = bash["-c", "echo 'Hello World'"].run(retcode=None, timeout=5)
        execution_time = time.time() - start_time
        print(f"✅ Quick command completed in {execution_time:.2f}s")
        print(f"Output: {stdout.strip()}")
    except Exception as e:
        print(f"❌ Quick command failed: {e}")
    
    # Test 2: Slow command (should timeout)
    print("\n2. Testing slow command (should timeout):")
    start_time = time.time()
    try:
        bash = local["bash"]
        retcode, stdout, stderr = bash["-c", "sleep 5"].run(retcode=None, timeout=2)
        execution_time = time.time() - start_time
        print(f"❌ Slow command unexpectedly completed in {execution_time:.2f}s")
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"✅ Slow command timed out after {execution_time:.2f}s")
        print(f"Error: {e}")
    
    # Test 3: Create a ShellResult for timeout case
    print("\n3. Testing ShellResult with timeout:")
    timeout_result = ShellResult(
        command="sleep 10",
        output="Command timed out after 3 seconds",
        success=False,
        timed_out=True,
        execution_time=3.0
    )
    print(f"ShellResult: {timeout_result}")

if __name__ == "__main__":
    test_timeout_functionality()