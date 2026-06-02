from collections import defaultdict

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


def _print_table(class_name: str, tests: list, tw) -> None:
    passed = sum(1 for _, s, _ in tests if s == "PASS")
    failed = sum(1 for _, s, _ in tests if s != "PASS")

    def line(s: str) -> None:
        tw.write_line(s)

    line("")
    line("╔" + "═" * (W - 2) + "╗")
    line(f"║  {class_name:<{W - 4}}║")
    line("╠" + "═" * (W - 2) + "╣")
    line(f"║  {'Test':<44}{'Status':<10}{'Time':<{W - 58}}║")
    line("╠" + "─" * (W - 2) + "╣")

    for test_name, status, duration in tests:
        icon = "✓" if status == "PASS" else "✗"
        label = f"{icon} {status}"
        name = test_name[:42] + ".." if len(test_name) > 44 else test_name
        line(f"║  {name:<44}{label:<10}{duration:.4f}s{'':<{W - 66}}║")

    line("╠" + "═" * (W - 2) + "╣")
    summary = f"Total: {len(tests)}   Passed: {passed}   Failed: {failed}"
    line(f"║  {summary:<{W - 4}}║")
    line("╚" + "═" * (W - 2) + "╝")


def pytest_runtest_teardown(item, nextitem):
    parts = item.nodeid.split("::")
    class_name = parts[-2] if len(parts) >= 3 else "No Class"
    next_class = nextitem.nodeid.split("::")[-2] if nextitem else None

    if next_class != class_name and class_name in _results:
        tw = item.config.pluginmanager.get_plugin("terminalreporter")
        if tw:
            _print_table(class_name, _results[class_name], tw)