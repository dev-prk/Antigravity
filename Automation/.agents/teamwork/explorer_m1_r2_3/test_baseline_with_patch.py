import sys
import os
import unittest

WORKSPACE_DIR = "/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi"
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

# Import patch helper
import test_harness_with_patch  # This applies monkeypatches to ext.ProblemExtractor

# Now import test_m1_filtering
import tests.test_m1_filtering as m1_tests

loader = unittest.TestLoader()
suite = loader.loadTestsFromModule(m1_tests)
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
if not result.wasSuccessful():
    sys.exit(1)
print("ALL 28 BASELINE M1 FILTERING TESTS PASSED SUCCESSFULLY!")
