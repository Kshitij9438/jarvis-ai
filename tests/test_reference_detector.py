from conversation.reference_detector import contains_reference


def test_detects_reference():
    assert contains_reference("What is it?")
    assert contains_reference("What are its applications?")


def test_does_not_detect_reference():
    assert not contains_reference("Explain transformers")