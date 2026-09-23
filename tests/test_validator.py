from planner.validator import PlanValidator as LegacyPlanValidator
from planner.plan_validator import PlanValidator
from planner.schema import Plan


def test_legacy_validator_aliases_plan_validator():
    assert LegacyPlanValidator is PlanValidator


def test_legacy_validator_preserves_basic_behavior():
    validator = LegacyPlanValidator()

    result = validator.validate(Plan(steps=[]))

    assert isinstance(result, Plan)
    assert result.steps == []
