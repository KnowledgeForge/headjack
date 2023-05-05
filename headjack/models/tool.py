from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Optional, cast

from sqlmodel import Field, Relationship, SQLModel, JSON
from sqlalchemy.sql.schema import Column

if TYPE_CHECKING:
    from headjack.models.utterance import Action, Observation


from pydantic import BaseModel, ValidationError, validator, root_validator
from typing import Dict, List, Union, Type, Literal, Optional, Any, TypeVar
from dataclasses import dataclass, field
from headjack.utils import fetch
import uuid
T = TypeVar('T')
def var():
    unique_id = uuid.uuid4()
    variable_name = str(unique_id).replace('-', '_')
    variable_name = 'var_' + variable_name
    return variable_name.upper()

@dataclass
class Compilation:
    variable: str = field(default_factory=var)
    body: str = ""
    where: List[str] = field(default_factory=list)
    code_var: Optional[str] = None

class ParamType(str, Enum):
    string = "string"
    integer = "integer"
    boolean = "boolean"

class Param(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str
    tool_schema_name: Optional[str] = Field(default=None, foreign_key="toolschema.name")
    tool_schema: "ToolSchema" = Relationship(back_populates="parameters")
    name: Optional[str] = None
    description: Optional[str] = None
    options: List[str] = None  # options is only valid if none of the lengths are set and if the type is one of the literals
    length: Optional[
        int
    ] = None  # if length is set we ignore the min_length, max_length
    max_length: Optional[
        int
    ] = None  # "max_length" # instead of "length" we could set max_length
    min_length: Optional[
        int
    ] = None  # "min_length" # if we set max_length but not min_length then min_length defaults to 1
    min_value: Optional[
        int
    ] = None  # if max_value is set defaults to 0 for integer and 1 for string
    max_value: Optional[int] = None
    required: bool = True
    _compilation: Optional[Compilation] = None

    def compile(self, append_var = None):
        if self.compiled(): return self
        compilation = Compilation()
        variable = compilation.variable
        code_var = variable.lower()
        compilation.code_var = code_var
        compilation.body+="#"*35+"\n"+f"#name={self.name}; desc={self.description}\n"+"#"*35
        compilation.body+=f"\n{code_var}=None\n"
        if (self.name or self.description) and self.max_length is None:
            temp = (
                (self.name + " " if self.name else "")
                + (f"({self.description})" if self.description else "")
                + ": "
            )
            compilation.body += f'"{temp}"'

        if self.max_length is not None:
            compilation.code_var = code_var
            min_length = self.min_length or 1
            count_var = variable + "_COUNT"
            temp = " | There are ["+count_var+"] needed."
            if self.name or self.description:
                temp = (
                    (self.name + " " if self.name else "")
                    + (f"({self.description} {temp})" if self.description else "")
                    + ": "
                )
            count_range = [str(i) for i in range(min_length, self.max_length + 1)]
            compilation.where.append(f"{count_var} in {count_range}")
            compilation.body += f"""
"{temp}"
{code_var} = []
for _ in range(int({count_var})):
    "[{variable}], "
    {code_var}.append({{"string": str, "integer": int, "boolean": lambda x: x=='True'}}['{self.type}']({variable}))
            """

        if self.length is not None:
            compilation.code_var = code_var
            compilation.body += f"""
{code_var} = []
for _ in range({self.length}):
    "[{variable}], "
    {code_var}.append({{"string": str, "integer": int, "boolean": lambda x: x=='True'}}['{self.type}']({variable}))
            """

        if self.type == "boolean":
            compilation.body += f"\n{code_var}={variable}=='True'\n"
            compilation.where.append(f"{variable} in ['True', 'False']")

        if self.type == "integer":
            if self.length is None and self.max_length is None:
                compilation.body += f"\"[{variable}]\\n\"\n"
                compilation.body += f"{code_var}=int({variable})\n"
            if self.max_value:
                min_value = self.min_value or 0
                value_range = [str(i) for i in range(min_value, self.max_value + 1)]
                compilation.where.append(f"{variable} in {value_range}")
            else:
                compilation.where.append(f"INT({variable})")

        if self.type == "string":
            if self.length is None and self.max_length is None:
                compilation.body += f"\"[{variable}]\\n\"\n"
                compilation.body += f"{code_var}={variable}\n"
            if self.max_value is not None:
                compilation.where.append(f"len({variable})<={self.max_value}")
            if self.min_value is not None:
                compilation.where.append(f"len({variable})>={self.min_value}")

        # list[param]
        if isinstance(self.type, list):
            compilation.body += f"\n{code_var}=[]\n"
            for param in self.type:
                param.compile(code_var)

        if self.options:
            compilation.where.append(f"{variable} in {self.options}")
        
        if append_var:
            compilation.body+=f"\n{append_var}.append({code_var})"
        
        object.__setattr__(self, "_compilation", compilation)
        return self

    @root_validator
    def length_must_be_positive(cls, values):
        v = values.get("length")
        if v is not None and v <= 0:
            raise ValueError("length must be positive")
        return values

    @root_validator
    def length_and_max_min_length_cannot_both_be_set(cls, values):
        v = values.get("length")
        if v is not None and any((values.get("max_length") is not None, values.get("min_length") is not None,)):
            raise ValueError("cannot set length and max/min_length")
        return values

    @root_validator
    def max_length_must_be_positive(cls, values):
        v = values.get("max_length")
        if v is not None and v <= 0:
            raise ValueError("max_length must be positive")
        return values

    @root_validator
    def max_length_must_be_at_least_min(cls, values):
        v = values.get("max_length")
        if (
            v is not None
            and values.get("min_length") is not None
            and v < values.get("min_length")
        ):
            raise ValueError("max_length must be at least min_length")
        return values

    @root_validator
    def min_length_must_be_positive(cls, values):
        v = values.get("min_length")
        if v is not None and v <= 0:
            raise ValueError("min_length must be positive")
        return values

    @root_validator
    def min_length_must_accompany_max(cls, values):
        v = values.get("min_length")
        if v is not None and values.get("max_length") is None:
            raise ValueError("max_length must be set if setting min_length")
        return values

    @root_validator
    def min_value_must_be_for_strings(cls, values):
        v = values.get("min_value")
        if values.get("type") == "string" and v is not None and v <= 0:
            raise ValueError("min_value must be positive for strings")
        return values

    @root_validator
    def length_cannot_be_set_with_param_list(cls, values):
        if isinstance(values.get("type"), list) and any(
            (
                values.get("length") is not None,
                values.get("max_length") is not None,
                values.get("min_length") is not None,
                values.get("max_value") is not None,
                values.get("min_value") is not None,
            )
        ):
            raise ValueError("cannot set any restrictions with a param list")
        return values

    @root_validator
    def min_max_only_for_integers_strings(cls, values):
        if values.get("type") not in ("string", "integer") and any(
            (
                values.get("max_value") is not None,
                values.get("min_value") is not None,
            )
        ):
            raise ValueError(
                "cannot set any value restrictions with non-integer/string type"
            )
        return values

    @root_validator
    def lengths_values_cannot_be_set_with_options(cls, values):
        if values.get("options") is not None and any(
            (
                values.get("length") is not None,
                values.get("max_length") is not None,
                values.get("min_length") is not None,
                values.get("max_value") is not None,
                values.get("min_value") is not None,
            )
        ):
            raise ValueError("cannot set any other restrictions with options")
        return values

    @root_validator
    def options_cannot_be_set_with_not_string_integer(cls, values):
        v = values.get("type")
        if v not in ("string", "integer") and values.get("options") is not None:
            raise ValueError("cannot set options with a param list")
        return values

    @root_validator
    def options_must_match_type(cls, values):
        if v := values.get("options"):
            ret = []
            for option in v:
                if type := {"string": str, "integer": int}.get(values.get("type")):
                    if type is not None:
                        option = str(type(option))
                        if option not in ret:
                            ret.append(option)
            values["options"] = ret
        return values

    @root_validator
    def min_value_must_accompany_max_for_nonstring(cls, values):
        if (
            values.get("min_value") is not None
            and values.get("max_value") is None
            and values["type"] != "string"
        ):
            raise ValueError(
                "max_value must be set if setting min_value for non-string"
            )
        return values
    @validator("description", check_fields=False)
    def description_length(cls, v):
        if len(v) > 100:
            raise ValueError("description length can be at most 100 chars")
        return v
    def __str__(self):
        return str(self._compilation.code_var)

    def compiled(self):
        return self._compilation is not None
    
    def format_payload(self):
        if not isinstance(self.type, list):
            return self._compilation.code_var
        return "["+", ".join(p.format_payload() for p in self.type)+"]"

class Verb(str, Enum):
    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    PATCH = "PATCH"
    DELETE = "DELETE"

class ToolSchema(SQLModel, table=True):
    name: str = Field(nullable=False, unique=True, primary_key=True)
    description: str
    parameters: List[Param] = Relationship(back_populates="tool_schema")
    json_: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    url: Optional[str] = Field(nullable=True)
    verb: Optional[Verb] = Field(nullable=True)
    results_schema: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON)) # if a results schema is not present this tool will not be referencable from other tools and will return text to agents
    
    @root_validator
    def results_schema_if_url(cls, values):
        if values.get('url') is not None and values.get('verb') is None:
            raise ValueError("given a url, must also give a verb")
        return values
        
    @validator("json_", "results_schema", check_fields=False)
    def json_dict_or_param(cls, v):
        def param_cast_check(value, key: Optional[str] = None):
            if type(value) not in (str, list, int, dict, bool):
                raise TypeError("Unnacceptable type in headjack json.")
            if isinstance(value, list):
                ret = []
                for v in value:
                    try:
                        ret.append(Param(**v))
                    except ValidationError:
                        ret.append(v)
                return ret
            if isinstance(value, dict):
                try:
                    return Param(**{**value, "name": key})
                except ValidationError:
                    return {k: param_cast_check(v) for k, v in value.items()}
            return value

        return {key: param_cast_check(value) for key, value in v.items()}

    def format_url(self, parameters: list):
        if self.url is None:
            raise ValueError("no url for tool schema")
        params=""
        query_params=""
        if self.parameters:
            for value, p in zip(parameters, self.parameters):
                if p.required and value is None:
                    raise ValueError("required value is None")
                if p.name is None:
                    params+="/"+str(value)
                else:
                    query_params+="&"+f"{p.name}={value}"
        return self.url+params+"?"+query_params
    


    def payload_code(self)->str: 
        def helper(value)->str:
            if isinstance(value, Param):
                return value.format_payload()
            if isinstance(value, dict):
                return "{"+", ".join(f"'{k}': {helper(v)}" for k, v in value.items())+"}"
            if isinstance(value, list):
                return "["+", ".join(helper(v) for v in value)+"]"
            return f"'{value}'" if isinstance(value, str) else str(value)
            
        json = None
        parameters = None
        if self.json_ is not None:
            json = helper(self.json_)
        if self.parameters is not None:
            parameters = "["+", ".join(helper(p) for p in self.parameters)+"]"
        return f"{{'parameters': {parameters}, 'json': {json}}}"
    
    def body(self)->str: 
        def helper(value)->str:
            if isinstance(value, Param):
                base = f"\n{value._compilation.body}\n"
                if isinstance(value.type, list):
                    for p in value.type:
                        base+=helper(p)
                return base
            if isinstance(value, dict):
                return "\n".join(helper(v) for v in value.values())
            if isinstance(value, list):
                return "\n".join(helper(v) for v in value)
            return ""
        return "\n".join(helper(p) for p in self.parameters)+"\n"+helper(self.json_)+"\n"

    def where(self)->str: 
        def helper(value)->str:
            if isinstance(value, Param):
                base = value._compilation.where[:]
                if isinstance(value.type, list):
                    for p in value.type:
                        base+=helper(p)
                return base
            if isinstance(value, dict):
                return sum([helper(v) for v in value.values()], [])
            if isinstance(value, list):
                return sum([helper(v) for v in value], [])
            return []

        return " and\n".join(helper(self.json_)+sum([helper(p) for p in self.parameters], []))
    
    def compile(self):
        def helper(value, key = None):
            if isinstance(value, Param):
                if value.name is None and key is not None:
                    object.__setattr__(value, 'name', key)
                value.compile()
                if isinstance(value.type, list):
                    for p in value.type:
                        helper(p)
            if isinstance(value, dict):
                for k, v in value.items():
                    helper(v, k)
            if isinstance(value, list):
                for v in value:
                    helper(v)
            return value
                    
        if self.json_ is not None:
            for k, v in self.json_.items():
                helper(v, k)
        if self.parameters is not None:
            for p in self.parameters:
                helper(p)
        return self
    
    async def fetch(self, payload: Dict[str, Any]):
        if self.url is None or self.verb is None:
            raise ValueError("no url and verb for tool schema")
        return await fetch(self.format_url(payload['parameters']), self.verb, payload['json'], self.results_schema is not None)
       
@dataclass
class Tool:
    schema: ToolSchema
    model_identifier: Optional[str] = None
    description_: Optional[str] = None
    name_: Optional[str] = None
    max_uses_per_query: int = cast(int, float("inf"))

    @property
    def description(self):
        return self.description_ or self.schema.description

    @property
    def name(self):
        return self.name_ or self.schema.name

    async def __call__(self, action: "Action") -> "Observation":
        if self.schema.url is not None:
            return Observation(utterance_=await self.schema.fetch(action.utterance_), tool=self)
        raise NotImplementedError()
