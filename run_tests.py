#!/usr/bin/env python3
"""
Test Runner for O.M.N.I. Survival Engine.
Discovers and executes all unit tests across the test suite.
"""

import unittest
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def run_all_tests():
    print("=" * 70)
    print(" RUNNING O.M.N.I. AUTOMATED UNIT TEST SUITE")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests", pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print(f" ALL {result.testsRun} TESTS PASSED SUCCESSFULLY! (100% SUCCESS)")
    else:
        print(f" TESTS COMPLETED WITH FAILURES: {len(result.failures)} failures, {len(result.errors)} errors.")
    print("=" * 70)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())

