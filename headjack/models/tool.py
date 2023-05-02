from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar, Optional, cast

from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    from headjack.models.utterance import Action, Observation


class ToolSchema:
    """
    Final answer value produced from an agent
    """

    schema_name: str
    schema_dict: dict
    _compiled: bool = field(init=False, default=False)
    _body: Optional[str] = field(init=False, default=None)
    _where: Optional[str] = field(init=False, default=None)

    @property
    def body(self):
        self._compile()
        return self._body

    @property
    def code(self):
        self._compile()
        return cast(str, self.body).replace('\\"[', "").replace("]", "").replace('\\"', '"').strip()[1:-1]

    @property
    def where(self):
        self._compile()
        return self._where

    def _compile(self):
        if self._compiled:
            return
        schema_dict = self.schema_dict
        if not schema_dict:
            self._body = ""
            self._where = ""
            return
        where = []
        prefix = self.schema_name + "_"

        def _helper(schema, key, end=False):
            if schema == int:
                variable = (prefix + key).upper()
                where.append(f'INT({variable}) and STOPS_AT({variable}, ",")')
                return variable
            if schema == str:
                variable = (prefix + key).upper()
                where.append(f"""STOPS_AT({variable}, '"')""")
                return variable
            if not isinstance(schema, dict):
                raise Exception(f"Unnacceptable type in schema: `{schema}`")
            result = "{{"
            for idx, (key, value) in enumerate(schema.items()):
                if "[" in key or "]" in key:
                    raise Exception("schema keys cannot have `[` or `]`")
                variable = _helper(value, key=key, end=idx == len(schema))
                quote = '\\"' if value == str else ""
                result += f'\\"{key}\\": {quote}[{variable}], '
            result = result[:-2] + "}}"
            return result

        self._body = _helper(schema_dict, key="")
        self._where = " and ".join(where)


@dataclass
class Tool(SQLModel, table=True):  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)
    default_description: ClassVar[str]
    default_ref_name: ClassVar[str]
    input_schema: ClassVar[ToolSchema]
    model_identifier: Optional[str] = None
    description_: Optional[str] = None
    ref_name_: Optional[str] = None
    max_uses_per_query: int = cast(int, float("inf"))

    @property
    def description(self):
        return self.description_ or self.default_description

    @property
    def ref_name(self):
        return self.ref_name_ or self.default_ref_name

    async def __call__(self, action: "Action") -> "Observation":
        raise NotImplementedError()
