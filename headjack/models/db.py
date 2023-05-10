from sqlmodel import Session, select

from headjack.exceptions import ToolError
from headjack.models.tool import ToolSchema
from headjack.tools import builtin_tool_schemas


def create_or_update_tool_schema(session: Session, tool_schema: ToolSchema):
    if tool_schema.name in builtin_tool_schemas:
        raise ToolError(f"Cannot create tool, name `{tool_schema.name}` " "is reserved by a built-in tool")
    session.add(tool_schema)
    session.commit()


def get_tool_schema(session: Session, name: str) -> ToolSchema:
    if builtin_tool := builtin_tool_schemas.get(name):
        return builtin_tool
    return session.exec(select(ToolSchema).where(ToolSchema.name == name)).one()
