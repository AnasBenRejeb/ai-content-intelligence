"""Test runner script"""
import subprocess
import sys

def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("RUNNING COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print()
    
    # Check if pytest is installed
    try:
        import pytest
        print("✅ pytest found")
    except ImportError:
        print("❌ pytest not found")
        print("Installing pytest...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"])
        import pytest
    
    # Run tests
    print("\n" + "=" * 60)
    print("Running tests...")
    print("=" * 60 + "\n")
    
    # Run with pytest
    exit_code = pytest.main([
        "tests/",
        "-v",
        "--tb=short",
        "--color=yes"
    ])
    
    print("\n" + "=" * 60)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ TESTS FAILED (exit code: {exit_code})")
    print("=" * 60)
    
    return exit_code

if __name__ == "__main__":
    sys.exit(run_tests())
