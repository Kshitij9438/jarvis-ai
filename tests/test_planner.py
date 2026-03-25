from planner.planner import extract_json

def test_extract_json_object():
    text = "```json\n{\"action\": \"echo\", \"args\": {\"text\": \"hi\"}}\n```"
    result = extract_json(text)
    assert result == '{"action": "echo", "args": {"text": "hi"}}'


def test_extract_json_list():
    text = "```json\n[{\"action\": \"echo\", \"args\": {\"text\": \"hi\"}}]\n```"
    result = extract_json(text)
    assert result == '[{"action": "echo", "args": {"text": "hi"}}]'

def test_planner_retry(monkeypatch):
    from planner.planner import Planner

    class FakeRegistry:
        def list_tools(self):
            return []

    planner = Planner(FakeRegistry())

    calls = {"count": 0}

    def fake_generate(prompt, system_prompt):
        calls["count"] += 1

        if calls["count"] == 1:
            return "INVALID JSON"  # ❌ first attempt fails
        else:
            return '{"steps": []}'  # ✅ second attempt works

    planner.llm.generate = fake_generate

    plan = planner.plan("test")

    assert plan is not None
    assert calls["count"] == 2