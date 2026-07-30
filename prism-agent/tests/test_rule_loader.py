"""Unit tests for RuleLoader."""

from agent.detection.rule_loader import RuleLoader


def test_rule_loader_returns_rules() -> None:
    """Test RuleLoader loads default or custom rules."""
    rules = RuleLoader.load_rules()
    assert isinstance(rules, list)
    assert len(rules) > 0
    assert rules[0].rule_id.startswith("SIG-")
