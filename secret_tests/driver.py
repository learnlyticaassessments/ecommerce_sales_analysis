import importlib.util
import datetime
import os
import numpy as np
import inspect
import random

def test_student_code(solution_path):
    report_dir = os.path.join(os.path.dirname(__file__), "..", "student_workspace")
    report_path = os.path.join(report_dir, "report.txt")
    os.makedirs(report_dir, exist_ok=True)

    spec = importlib.util.spec_from_file_location("student_module", solution_path)
    student_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(student_module)

    report_lines = [f"\n=== E-Commerce Sales Analysis Test Run at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==="]

    keyword_checks = {
        "create_sales_array": ["np.array"],
        "validate_sales_array": ["np.all", ">=", "size"],
        "compute_sales_metrics": ["sum", "mean", "max"],
        "categorize_demand_levels": ["for", "if"],
        "longest_growth_streak": ["for", "if", ">"],
        "format_sales_data": ["for", "f\"", "{x:,}"]
    }

    all_test_cases = {
        "Visible": [
            {"desc": "Create sales array", "func": "create_sales_array", "input": [150, 220, 90, 300, 175], "expected": np.array([150, 220, 90, 300, 175])},
            {"desc": "Validate array with negative values", "func": "validate_sales_array", "input": np.array([100, -50]), "expected": False},
            {"desc": "Compute sales metrics", "func": "compute_sales_metrics", "input": np.array([150, 220, 90, 300, 175]), "expected": (935, 187.0, 300)},
            {"desc": "Categorize demand levels", "func": "categorize_demand_levels", "input": np.array([99, 150, 275]), "expected": np.array(["Low Demand", "Moderate Demand", "High Demand"])},
            {"desc": "Longest growth streak - generic", "func": "longest_growth_streak", "input": np.array([100, 120, 140, 130, 150, 160, 170, 140, 145, 150, 155]), "expected": 4}
        ],
        "Hidden": [
            {"desc": "Format sales data", "func": "format_sales_data", "input": np.array([1000, 24500]), "expected": np.array(["1,000", "24,500"])},
            {"desc": "Validate empty sales array", "func": "validate_sales_array", "input": np.array([]), "expected": False},
            {"desc": "Borderline demand categorization", "func": "categorize_demand_levels", "input": np.array([100, 250]), "expected": np.array(["Moderate Demand", "Moderate Demand"])}
        ]
    }

    # Silent anti-hardcoding checks
    def run_random_check(func_name, func_ref):
        if func_name == "create_sales_array":
            arr = func_ref([random.randint(10, 999) for _ in range(5)])
            return isinstance(arr, np.ndarray) and not np.array_equal(arr, np.array([150, 220, 90, 300, 175]))

        if func_name == "validate_sales_array":
            arr = np.array([-1, 5])
            return func_ref(arr) is False

        if func_name == "compute_sales_metrics":
            arr = np.array([random.randint(1, 100) for _ in range(5)])
            out = func_ref(arr)
            return isinstance(out, tuple) and len(out) == 3 and out[0] == sum(arr)

        if func_name == "categorize_demand_levels":
            arr = np.array([50, 150, 500])
            out = func_ref(arr)
            return isinstance(out, np.ndarray) and "Low Demand" in out and "High Demand" in out

        if func_name == "longest_growth_streak":
            arr = np.array([1, 2, 3, 1, 2, 3, 4])
            return func_ref(arr) == 4

        if func_name == "format_sales_data":
            arr = np.array([2000, 3400])
            formatted = func_ref(arr)
            return "2,000" in formatted[0] and "3,400" in formatted[1]

        return True

    for section, cases in all_test_cases.items():
        for i, case in enumerate(cases, 1):
            try:
                func = getattr(student_module, case["func"])
                src = inspect.getsource(func).replace(" ", "").replace("\n", "").lower()
                reason = None

                # Edge Case: contains only pass
                if 'pass' in src and len(src) < 80:
                    reason = "Function contains only 'pass'"

                # Edge Case: missing logic
                if not reason and all(k not in src for k in keyword_checks[case["func"]]):
                    reason = "Missing required logic/keywords"

                # Edge Case: hardcoded return detected
                if not reason and isinstance(case["expected"], (np.ndarray, list, tuple)):
                    if 'return' in src and str(case["expected"]).replace(" ", "").lower() in src:
                        reason = "Hardcoded return detected"

                # Anti-hardcoding randomized test (silent)
                if not run_random_check(case["func"], func):
                    reason = "Randomized logic test failed (possible hardcoding or shortcut)"

                result = func(*case["input"]) if isinstance(case["input"], tuple) else func(case["input"])
                expected = case["expected"]

                if isinstance(expected, np.ndarray):
                    passed = np.array_equal(result, expected)
                elif isinstance(expected, tuple):
                    passed = all(round(a, 2) == round(b, 2) for a, b in zip(result, expected))
                else:
                    passed = result == expected

                if passed and not reason:
                    msg = f"✅ {section} Test Case {i} Passed: {case['desc']}"
                else:
                    msg = f"❌ {section} Test Case {i} Failed: {case['desc']} | Reason: {reason or 'Output mismatch'}"
                print(msg)
                report_lines.append(msg)
            except Exception as e:
                msg = f"❌ {section} Test Case {i} Crashed: {case['desc']} | Error: {str(e)}"
                print(msg)
                report_lines.append(msg)

    with open(report_path, "a", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")

if __name__ == "__main__":
    solution_file = os.path.join(os.path.dirname(__file__), "..", "student_workspace", "solution.py")
    test_student_code(solution_file)
