from headjack.agents import standard

from headjack.models.tool import ToolSchema
from headjack.tools.example_builtin_tool_schema import example_builtin_tool_schema

__all__ = ["builtin_tool_schemas"]

builtin_tool_schemas = {
    "example_builtin_tool_schema": example_builtin_tool_schema
}