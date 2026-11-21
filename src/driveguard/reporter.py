"""Reporting: the structured validation report and how it is printed."""

from dataclasses import dataclass, field


@dataclass
class ValidationIssue:
    """One problem found in the data."""

    rule: str
    severity: str
    message: str


@dataclass
class ValidationReport:
    """The result of a validation run: passed or not, plus all issues."""

    passed: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)

    def add_issue(self, rule: str, severity: str, message: str) -> None:
        """Record a problem. Any problem means the data did not pass."""
        self.passed = False
        self.issues.append(ValidationIssue(rule, severity, message))


def format_report(report: ValidationReport) -> str:
    """Turn a report into readable text for the terminal."""
    status = "PASSED" if report.passed else "FAILED"
    lines = [f"Validation {status} ({len(report.issues)} issue(s))"]

    for issue in report.issues:
        lines.append(f"[{issue.severity}] {issue.rule}: {issue.message}")

    return "\n".join(lines)
