from __future__ import annotations

from typing import TYPE_CHECKING

from tox.config.loader.memory import MemoryLoader
from tox.plugin import impl

from .config import load_project_config

if TYPE_CHECKING:
    from tox.config.sets import ConfigSet
    from tox.session.state import State


def _python_executable(version: str) -> str:
    return f"python{version}"


@impl
def tox_extend_envs() -> tuple[str, ...]:
    return ("docs",)


@impl
def tox_add_core_config(core_conf: ConfigSet, state: State) -> None:
    project_config = load_project_config()
    state.conf.memory_seed_loaders["docs"].append(
        MemoryLoader(
            description="build documentation",
            base_python=_python_executable(project_config.python_version),
            deps=["-rdocs/requirements.txt"],
            extras=tuple(project_config.extras),
            commands=["sphinx-scrapy build"],
        )
    )
