from unittest.mock import Mock

from planner.plan_builder import PlanBuilder
from planner.task import Task
from planner.request_understanding import RequestUnderstanding
from planner.decision import DecisionType, PlannerDecision


def make_builder():
    registry = Mock()

    capability_selector = Mock()
    capability_selector.select.return_value = None

    tool_selector = Mock()
    task_builder = Mock()
    entity_extractor = Mock()

    return (
        PlanBuilder(
            registry=registry,
            capability_selector=capability_selector,
            tool_selector=tool_selector,
            task_builder=task_builder,
            entity_extractor=entity_extractor,
        ),
        registry,
        capability_selector,
        tool_selector,
        task_builder,
        entity_extractor,
    )


def test_build_segments_request():
    (
        builder,
        registry,
        capability_selector,
        tool_selector,
        task_builder,
        entity_extractor,
    ) = make_builder()

    tool = Mock()
    tool.name = "explain"
    tool.requires = []

    tool_selector.select.return_value = [tool]
    entity_extractor.extract.return_value = {"topics": ["BFS"]}
    task_builder.build_tasks.return_value = [
        Task("explain", query="BFS")
    ]

    tasks = builder.build("explain BFS")

    assert tasks == [Task("explain", query="BFS")]
    capability_selector.select.assert_called_once_with("explain BFS")
    tool_selector.select.assert_called_once()


def test_build_passes_entities_to_task_builder():
    (
        builder,
        registry,
        capability_selector,
        tool_selector,
        task_builder,
        entity_extractor,
    ) = make_builder()

    tool = Mock()
    tool.name = "explain"
    tool.requires = []

    entities = {"topics": ["transformers"]}

    tool_selector.select.return_value = [tool]
    entity_extractor.extract.return_value = entities
    task_builder.build_tasks.return_value = [
        Task("explain", query="transformers")
    ]

    builder.build("explain transformers")

    entity_extractor.extract.assert_called_once_with(
        "explain transformers"
    )

    task_builder.build_tasks.assert_called_once_with(
        "explain transformers",
        [tool],
        entities,
    )


def test_build_passes_canonical_query_to_task_builder():
    (
        builder,
        registry,
        capability_selector,
        tool_selector,
        task_builder,
        entity_extractor,
    ) = make_builder()

    tool = Mock()
    tool.name = "explain"
    tool.requires = []

    tool_selector.select.return_value = [tool]
    entity_extractor.extract.return_value = {}
    task_builder.build_tasks.return_value = [
        Task("explain", query="BFS")
    ]

    understanding = [
        RequestUnderstanding(
            original_query="explain BFS",
            canonical_query="bfs",
            decision=PlannerDecision(
                type=DecisionType.EXECUTE
            ),
        )
    ]

    builder.build(
        "explain BFS",
        request_understanding=understanding,
    )

    task_builder.build_tasks.assert_called_once_with(
        "explain BFS",
        [tool],
        {},
        canonical_query="bfs",
    )


def test_build_passes_capability_to_tool_selector():
    (
        builder,
        registry,
        capability_selector,
        tool_selector,
        task_builder,
        entity_extractor,
    ) = make_builder()

    capability = "knowledge"
    capability_selector.select.return_value = capability

    tool = Mock()
    tool.name = "explain"
    tool.requires = []

    tool_selector.select.return_value = [tool]
    entity_extractor.extract.return_value = {}
    task_builder.build_tasks.return_value = [
        Task("explain", query="BFS")
    ]

    builder.build("explain BFS")

    tool_selector.select.assert_called_once_with(
        "explain BFS",
        top_k=2,
        context=None,
        capability=capability,
    )


def test_build_expands_static_dependencies():
    (
        builder,
        registry,
        capability_selector,
        tool_selector,
        task_builder,
        entity_extractor,
    ) = make_builder()

    dependency = Mock()
    dependency.name = "load_document"
    dependency.requires = []

    tool = Mock()
    tool.name = "rag_search"
    tool.requires = ["load_document"]

    registry.get.side_effect = {
        "load_document": dependency,
        "rag_search": tool,
    }.get

    tool_selector.select.return_value = [tool]
    entity_extractor.extract.return_value = {}

    task_builder.build_tasks.return_value = [
        Task(
            "load_document",
            file_path="paper.pdf",
        ),
        Task(
            "rag_search",
            file_path="paper.pdf",
            query="summary",
        ),
    ]

    tasks = builder.build("summarize paper.pdf")

    assert tasks == [
        Task(
            "load_document",
            file_path="paper.pdf",
        ),
        Task(
            "rag_search",
            file_path="paper.pdf",
            query="summary",
        ),
    ]

    task_builder.build_tasks.assert_called_once_with(
        "summarize paper.pdf",
        [dependency, tool],
        {},
    )


def test_build_ignores_empty_segments():
    (
        builder,
        registry,
        capability_selector,
        tool_selector,
        task_builder,
        entity_extractor,
    ) = make_builder()

    tool = Mock()
    tool.name = "explain"
    tool.requires = []

    tool_selector.select.return_value = [tool]
    entity_extractor.extract.return_value = {}
    task_builder.build_tasks.return_value = [
        Task("explain", query="BFS")
    ]

    tasks = builder.build("explain BFS, ,")

    assert tasks == [Task("explain", query="BFS")]


def test_build_uses_request_understanding_segments_without_resplitting():
    (
        builder,
        registry,
        capability_selector,
        tool_selector,
        task_builder,
        entity_extractor,
    ) = make_builder()

    tool = Mock()
    tool.name = "explain"
    tool.requires = []

    entities = {"topics": ["Python and C++"]}
    tool_selector.select.return_value = [tool]

    expected_task = Task("explain", query="Python and C++")
    task_builder.build_tasks.return_value = [expected_task]

    decision = PlannerDecision(type=DecisionType.EXECUTE)

    understanding = RequestUnderstanding(
        original_query="Explain Python and C++",
        canonical_query="explain python and c++",
        entities=entities,
        decision=decision,
    )

    tasks = builder.build(
        "Explain Python and C++",
        request_understanding=[understanding],
    )

    assert tasks == [expected_task]

    capability_selector.select.assert_called_once_with(
        "Explain Python and C++"
    )
    tool_selector.select.assert_called_once()
    entity_extractor.extract.assert_not_called()
    task_builder.build_tasks.assert_called_once_with(
        "Explain Python and C++",
        [tool],
        entities,
        canonical_query="explain python and c++",
    )
