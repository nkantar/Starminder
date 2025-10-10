from typing import Literal, Type

from starminder.implementations.base import BaseImplementation
from starminder.implementations.github import GitHubImplementation

IMPLEMENTATIONS: dict[str, Type[BaseImplementation]] = {
    "github": GitHubImplementation,
}

ProviderLiteral = Literal["github"]


def get_implementation(provider: ProviderLiteral) -> Type[BaseImplementation]:
    return IMPLEMENTATIONS[provider]
