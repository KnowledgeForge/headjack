from headjack.models import db
from headjack.models.tool import ToolSchema

def test_saving_a_tool_schema(session):
    ts = ToolSchema(name="foo", description="A foo description.")
    db.create_or_update_tool_schema(session, ts)
    assert ts == db.get_tool_schema(session, "foo")
