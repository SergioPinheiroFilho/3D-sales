"""Contratos compartilhados pelos agentes."""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Protocol
from urllib.parse import urlsplit


class Classification(StrEnum):
    CONFIRMED = "confirmada"
    OBSERVED = "observada"
    ESTIMATED = "estimada"


@dataclass(frozen=True)
class SourceReference:
    source: str
    url: str
    observed_on: date

    def __post_init__(self) -> None:
        parts = urlsplit(self.url)
        if not self.source.strip() or parts.scheme not in {"http", "https"} or not parts.hostname:
            raise ValueError("Informe a fonte e uma URL HTTP(S) válida.")
        if parts.username is not None or parts.password is not None:
            raise ValueError("A URL da fonte não pode conter credenciais.")


class Agent[RequestT, ResultT](Protocol):
    def run(self, request: RequestT) -> ResultT:
        """Executa uma análise e retorna dados para o fluxo local."""
