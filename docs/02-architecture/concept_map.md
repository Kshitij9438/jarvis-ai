# Concept Map

---

## User Input

Produced By

User

Consumed By

Planner

---

## Tool

Produced By

Registry

Consumed By

ToolSelector

TaskBuilder

Executor

---

## Entity

Produced By

EntityExtractor

Consumed By

TaskBuilder

---

## Arguments

Produced By

ArgExtractor

Consumed By

TaskBuilder

---

## Task

Produced By

TaskBuilder

Consumed By

DependencyResolver

Optimizer

Validator

Executor

---

## Plan

Produced By

Planner

Consumed By

Control Layer

Executor

---

## Action

Produced By

Planner

Consumed By

Executor

---

## Prompt

Produced By

tool_prompt.py

Consumed By

LLM

---

## Reflection

Produced By

LLM

Consumed By

Evaluator