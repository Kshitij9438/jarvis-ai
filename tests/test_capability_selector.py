from planner.capability_selector import Capability, CapabilitySelector


def make_selector():
    return CapabilitySelector()


def test_select_navigation_capability():
    selector = make_selector()

    assert selector.select("open github") == Capability.NAVIGATION


def test_select_calculation_capability():
    selector = make_selector()

    assert selector.select("calculate 2 + 2") == Capability.CALCULATION


def test_select_document_capability():
    selector = make_selector()

    assert selector.select("summarize report.pdf") == Capability.DOCUMENT


def test_select_knowledge_capability():
    selector = make_selector()

    assert selector.select("explain transformers") == Capability.KNOWLEDGE


def test_unknown_query_returns_no_capability():
    selector = make_selector()

    assert selector.select("asdfghjkl") is None


def test_capability_selector_does_not_return_tools():
    selector = make_selector()

    result = selector.select("explain transformers")

    assert isinstance(result, Capability)
