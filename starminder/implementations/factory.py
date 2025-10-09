from typing import Literal, Type

from starminder.implementations.base import BaseImplementation
from starminder.implementations.github import GitHubImplementation

IMPLEMENTATIONS: dict[str, Type[BaseImplementation]] = {
    "github": GitHubImplementation,
}


def get_implementation(provider: Literal["github"]) -> Type[BaseImplementation]:
    return IMPLEMENTATIONS[provider]
