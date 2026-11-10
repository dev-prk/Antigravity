#!/usr/bin/env python3
"""
Comprehensive E2E Test Runner for ZenClass and Guvi CodeKata Automation Suite.
Supports running tests across 4 tiers with clean CLI flags:
  --all: Run all test tiers (Tier 1-4)
  --tier [1|2|3|4]: Run specific test tier
  --feature [F01..F22]: Run specific feature tests
  --verbose: Verbose output
  --json: Output JSON metrics
"""

import argparse
import os
import sys
import time
import unittest
import json
from typing import List, Dict, Any

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


FEATURE_MAP = {
    "F01": ("tier1_features.test_f01_browser", "Headed Browser Lifecycle"),
    "F02": ("tier1_features.test_f02_state_manager", "Persistent State Manager"),
    "F03": ("tier1_features.test_f03_hitl_handler", "Human-in-the-Loop Handler"),
    "F04": ("tier1_features.test_f04_reporter", "Reporting Engine"),
    "F05": ("tier1_features.test_f05_extractor", "Problem Statement Extractor"),
    "F06": ("tier1_features.test_f06_solver", "Autonomous Python 3 Solver"),
    "F07": ("tier1_features.test_f07_sandbox", "Subprocess Test Sandbox"),
    "F08": ("tier1_features.test_f08_ace_adapter", "Ace Editor Keyboard Adapter"),
    "F09": ("tier1_features.test_f09_guvi_auth", "Guvi Authentication"),
    "F10": ("tier1_features.test_f10_codekata_discovery", "CodeKata Table Discovery"),
    "F11": ("tier1_features.test_f11_codekata_execution", "CodeKata Execution & Submit"),
    "F12": ("tier1_features.test_f12_zenclass_auth", "ZenClass Authentication"),
    "F13": ("tier1_features.test_f13_zenclass_tasks_discovery", "ZenClass Tasks Discovery"),
    "F14": ("tier1_features.test_f14_zenclass_submission", "Dynamic Task Submission"),
    "F15": ("tier1_features.test_f15_zenclass_verification", "Task Submission Verification"),
    "F16": ("tier1_features.test_f16_zenclass_projects_discovery", "ZenClass Projects Discovery"),
    "F17": ("tier1_features.test_f17_project_synthesis", "Local Project Code Synthesis"),
    "F18": ("tier1_features.test_f18_project_build", "Local Project Build Verification"),
    "F19": ("tier1_features.test_f19_project_hitl", "Project Human Pause Protocol"),
    "F20": ("tier1_features.test_f20_project_submit", "Project Submission & Verification"),
    "F21": ("tier1_features.test_f21_cli", "Unified CLI Interface"),
    "F22": ("tier1_features.test_f22_e2e_verification", "Final E2E Suite Verification"),
}

TIER_DIRS = {
    1: "tier1_features",
    2: "tier2_boundaries",
    3: "tier3_pairwise",
    4: "tier4_workloads",
}


def load_suite_for_tier(tier: int) -> unittest.TestSuite:
    dir_name = TIER_DIRS.get(tier)
    if not dir_name:
        raise ValueError(f"Unknown tier: {tier}")
    suite_dir = os.path.join(TESTS_DIR, dir_name)
    loader = unittest.defaultTestLoader
    return loader.discover(suite_dir, pattern="test_*.py")


def load_suite_for_feature(feature_key: str) -> unittest.TestSuite:
    norm_key = feature_key.upper().strip()
    if norm_key not in FEATURE_MAP:
        raise ValueError(f"Unknown feature ID: {feature_key}. Valid IDs: {list(FEATURE_MAP.keys())}")
    mod_path, _ = FEATURE_MAP[norm_key]
    module_name = f"tests.e2e.{mod_path}"
    loader = unittest.defaultTestLoader
    return loader.loadTestsFromName(module_name)


def run_test_suite(suite: unittest.TestSuite, verbose: bool = False) -> Dict[str, Any]:
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    start_time = time.time()
    result = runner.run(suite)
    duration = time.time() - start_time

    return {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "passed": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
        "duration_sec": round(duration, 3),
        "success": result.wasSuccessful(),
        "failure_details": [
            {"test": str(case), "traceback": tb}
            for case, tb in result.failures + result.errors
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="ZenClass & Guvi E2E Test Runner")
    parser.add_argument("--all", action="store_true", help="Run all 4 test tiers")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4], help="Run a specific test tier (1-4)")
    parser.add_argument("--feature", type=str, help="Run a specific feature test (e.g., F01, F02, ... F22)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose test runner output")
    parser.add_argument("--json", action="store_true", help="Output summary in JSON format")

    args = parser.parse_args()

    # Default to --all if no specific selector provided
    if not args.tier and not args.feature and not args.all:
        args.all = True

    print("=" * 80)
    print("ZenClass & Guvi CodeKata Automation Suite - E2E Test Runner")
    print("=" * 80)

    summary: Dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tiers": {},
        "total_tests": 0,
        "total_passed": 0,
        "total_failed": 0,
        "total_errors": 0,
        "total_skipped": 0,
        "total_duration_sec": 0.0,
        "success": True,
    }

    if args.feature:
        print(f"Running Feature Test: {args.feature.upper()} ({FEATURE_MAP.get(args.feature.upper(), ('', 'Unknown'))[1]})")
        suite = load_suite_for_feature(args.feature)
        res = run_test_suite(suite, verbose=args.verbose)
        summary["total_tests"] = res["tests_run"]
        summary["total_passed"] = res["passed"]
        summary["total_failed"] = res["failures"]
        summary["total_errors"] = res["errors"]
        summary["total_skipped"] = res["skipped"]
        summary["total_duration_sec"] = res["duration_sec"]
        summary["success"] = res["success"]
    elif args.tier:
        print(f"Running Tier {args.tier} Tests ({TIER_DIRS[args.tier]})...")
        suite = load_suite_for_tier(args.tier)
        res = run_test_suite(suite, verbose=args.verbose)
        summary["tiers"][f"tier_{args.tier}"] = res
        summary["total_tests"] = res["tests_run"]
        summary["total_passed"] = res["passed"]
        summary["total_failed"] = res["failures"]
        summary["total_errors"] = res["errors"]
        summary["total_skipped"] = res["skipped"]
        summary["total_duration_sec"] = res["duration_sec"]
        summary["success"] = res["success"]
    elif args.all:
        print("Running All 4 Tiers (Tier 1: Features, Tier 2: Boundaries, Tier 3: Pairwise, Tier 4: Workloads)...")
        overall_success = True
        for tier_num in [1, 2, 3, 4]:
            print(f"\n--- [Tier {tier_num}: {TIER_DIRS[tier_num]}] ---")
            suite = load_suite_for_tier(tier_num)
            res = run_test_suite(suite, verbose=args.verbose)
            summary["tiers"][f"tier_{tier_num}"] = res
            summary["total_tests"] += res["tests_run"]
            summary["total_passed"] += res["passed"]
            summary["total_failed"] += res["failures"]
            summary["total_errors"] += res["errors"]
            summary["total_skipped"] += res["skipped"]
            summary["total_duration_sec"] += res["duration_sec"]
            if not res["success"]:
                overall_success = False
        summary["success"] = overall_success

    print("\n" + "=" * 80)
    print("E2E Test Run Summary")
    print("=" * 80)
    print(f"Total Tests:    {summary['total_tests']}")
    print(f"Passed:         {summary['total_passed']}")
    print(f"Failed:         {summary['total_failed']}")
    print(f"Errors:         {summary['total_errors']}")
    print(f"Skipped:        {summary['total_skipped']}")
    print(f"Duration:       {round(summary['total_duration_sec'], 3)}s")
    print(f"Overall Result: {'PASSED' if summary['success'] else 'FAILED'}")
    print("=" * 80)

    if args.json:
        print(json.dumps(summary, indent=2))

    sys.exit(0 if summary["success"] else 1)


if __name__ == "__main__":
    main()
