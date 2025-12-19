from dataclasses import dataclass
from typing import Any


@dataclass
class Request:
    method: str
    params: list[Any]
    id: int

    def respond(self, result: Any) -> "Response":
        return Response(result, self.id)

    def error(self, code: int, error: str) -> "Error":
        return Error(code, error, self.id)


@dataclass
class Response:
    result: Any
    id: int


@dataclass
class Error:
    code: int
    message: str
    id: int
