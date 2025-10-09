from typing import Literal

from starminder.implementations.github import GitHubImplementation

IMPLEMENTATIONS = {
    "github": GitHubImplementation,
}


def get_implementation(provider: Literal["github"]):
    return IMPLEMENTATIONS[provider]
