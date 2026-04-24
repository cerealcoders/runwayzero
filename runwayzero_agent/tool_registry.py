"""Simple tool registry for the RunwayZero agent.

Each tool is:
- An async function: async def tool_fn(args: dict) -> dict
- A definition dict for the Anthropic API: {name, description, input_schema}

Tools are registered via register_tool() and retrieved via get_tool_definitions()
and dispatch_tool().
"""

from typing import Any, Callable, Coroutine

ToolFn = Callable[[dict[str, Any]], Coroutine[Any, Any, dict[str, Any]]]

_registry: dict[str, tuple[ToolFn, dict[str, Any]]] = {}


def register_tool(
    name: str,
    description: str,
    input_schema: dict[str, Any],
    fn: ToolFn,
) -> None:
    _registry[name] = (fn, {
        "name": name,
        "description": description,
        "input_schema": input_schema,
    })


def get_tool_definitions() -> list[dict[str, Any]]:
    return [defn for _, defn in _registry.values()]


async def dispatch_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    if name not in _registry:
        from runwayzero_agent.errors import error_response
        return error_response(f"Unknown tool: {name}", retryable=False)
    fn, _ = _registry[name]
    return await fn(args)
