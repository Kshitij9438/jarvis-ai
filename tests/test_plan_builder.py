from unittest.mock import Mock

from planner.plan_builder import PlanBuilder
from planner.task import Task


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
