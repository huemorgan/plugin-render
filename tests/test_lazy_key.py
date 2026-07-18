"""040 — plugin-render must pick up a key vaulted AFTER load, no reload.

Incident: the owner filled the secure form for `plugin_render.api_key` while the
plugin was already loaded. The client was built only in `on_load`, so every tool
kept raising "Render API key not configured. Add it in Settings > Render." — and
the agent kept telling the owner to go click Settings.

BEFORE-fix behavior (bug): a key saved after load never activates the tools.
AFTER-fix behavior: the first tool use lazily re-resolves the key and succeeds.
"""

from __future__ import annotations

import pytest

import plugin_render
from plugin_render import RenderPlugin
from plugin_render.state import set_client

VAULT_KEY = "plugin_render.api_key"


class _Cred:
    def __init__(self, value: str) -> None:
        self.value = value


class _Vault:
    """A vault whose credential appears only once `key` is set (owner saves it)."""

    def __init__(self) -> None:
        self.key: str | None = None

    async def get_credential(self, name: str) -> _Cred:
        if self.key is None:
            raise KeyError(name)
        return _Cred(self.key)


class _Reg:
    def __init__(self) -> None:
        self.handlers: dict = {}

    def register(self, plugin, tool_def, handler, **kw) -> None:
        self.handlers[tool_def.name] = handler


class _Ctx:
    def __init__(self, vault: _Vault, reg: _Reg) -> None:
        self.vault = vault
        self.tool_registry = reg
        self.skill_registry = None


class _FakeClient:
    """Stand-in for RenderClient so no real Render API call happens."""

    def __init__(self, api_key: str, base_url: str | None = None) -> None:
        self.api_key = api_key

    async def list_services(self):
        return [{"id": "srv-x", "name": "luna-marketplaces"}]

    async def close(self) -> None:  # pragma: no cover
        pass


@pytest.fixture(autouse=True)
def _isolate(monkeypatch):
    set_client(None)
    monkeypatch.setattr(plugin_render, "RenderClient", _FakeClient)
    monkeypatch.delenv("RENDER_API_KEY", raising=False)
    monkeypatch.delenv("LUNA_RENDER_API_KEY", raising=False)
    yield
    set_client(None)


async def test_key_vaulted_after_load_activates_without_reload():
    vault = _Vault()  # empty at load — no key yet
    reg = _Reg()
    plugin = RenderPlugin()
    await plugin.on_load(_Ctx(vault, reg))

    list_services = reg.handlers["render_list_services"]

    # Works-well: with no key anywhere, the tool honestly errors (before & after).
    with pytest.raises(RuntimeError):
        await list_services()

    # Owner vaults the key AFTER the plugin already loaded.
    vault.key = "rnd_live_key"

    # The bug: client was built only at load, so this still raised "not
    # configured". The fix resolves lazily on first use — no reload needed.
    out = await list_services()
    assert out["services"] == [{"id": "srv-x", "name": "luna-marketplaces"}]

    await plugin.on_unload()
