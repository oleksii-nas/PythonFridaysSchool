from collections import defaultdict
from datetime import datetime
from pathlib import Path

_results: dict = defaultdict(list)

W = 72  # table width


def pytest_runtest_logreport(report):
    if report.when != "call":
        return
    parts = report.nodeid.split("::")
    class_name = parts[-2] if len(parts) >= 3 else "No Class"
    test_name = parts[-1]
    if report.passed:
        status = "PASS"
    elif report.failed:
        status = "FAIL"
    else:
        status = "ERROR"
    _results[class_name].append((test_name, status, report.duration))


def _format_table(class_name: str, tests: list) -> list[str]:
    passed = sum(1 for _, s, _ in tests if s == "PASS")
    failed = sum(1 for _, s, _ in tests if s != "PASS")
    lines = []
    lines.append("")
    lines.append("╔" + "═" * (W - 2) + "╗")
    lines.append(f"║  {class_name:<{W - 4}}║")
    lines.append("╠" + "═" * (W - 2) + "╣")
    lines.append(f"║  {'Test':<44}{'Status':<10}{'Time':<{W - 58}}║")
    lines.append("╠" + "─" * (W - 2) + "╣")
    for test_name, status, duration in tests:
        icon = "✓" if status == "PASS" else "✗"
        label = f"{icon} {status}"
        name = test_name[:42] + ".." if len(test_name) > 44 else test_name
        lines.append(f"║  {name:<44}{label:<10}{duration:.4f}s{'':<{W - 66}}║")
    lines.append("╠" + "═" * (W - 2) + "╣")
    summary = f"Total: {len(tests)}   Passed: {passed}   Failed: {failed}"
    lines.append(f"║  {summary:<{W - 4}}║")
    lines.append("╚" + "═" * (W - 2) + "╝")
    return lines


def _print_table(class_name: str, tests: list, tw) -> None:
    for line in _format_table(class_name, tests):
        tw.write_line(line)


def pytest_runtest_teardown(item, nextitem):
    parts = item.nodeid.split("::")
    class_name = parts[-2] if len(parts) >= 3 else "No Class"
    next_class = nextitem.nodeid.split("::")[-2] if nextitem else None

    if next_class != class_name and class_name in _results:
        tw = item.config.pluginmanager.get_plugin("terminalreporter")
        if tw:
            _print_table(class_name, _results[class_name], tw)


def pytest_sessionfinish(session, exitstatus):
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = log_dir / f"pytest_{timestamp}.log"

    lines: list[str] = [
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"{'=' * W}",
    ]

    total_passed = total_failed = 0
    for class_name, tests in _results.items():
        lines.extend(_format_table(class_name, tests))
        total_passed += sum(1 for _, s, _ in tests if s == "PASS")
        total_failed += sum(1 for _, s, _ in tests if s != "PASS")

    lines += [
        "",
        "=" * W,
        f"TOTAL: {total_passed + total_failed}   "
        f"Passed: {total_passed}   Failed: {total_failed}",
    ]

    log_file.write_text("\n".join(lines), encoding="utf-8")