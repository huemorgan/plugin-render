"""Cloud key-provisioning contract for plugin-render (change-all-to-key-provisioning).

The client must route through `LUNA_RENDER_BASE_URL` when set (gateway proxy)
and the real Render API otherwise; `credential_slots()` must advertise the
base-url var so the control plane marks the plugin provisionable.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from plugin_render import RenderPlugin
from plugin_render.client import API_BASE, RenderClient

PKG = Path(__file__).resolve().parents[1] / "plugin_render"


def test_client_uses_base_url_override() -> None:
    c = RenderClient("tok", base_url="https://gw.example/proxy/render")
    assert str(c._http.base_url).rstrip("/") == "https://gw.example/proxy/render"


def test_client_defaults_to_real_upstream() -> None:
    c = RenderClient("tok")
    assert str(c._http.base_url).rstrip("/") == API_BASE


def test_credential_slot_advertises_base_url_var() -> None:
    slots = RenderPlugin().credential_slots()
    assert slots[0].slug == "render"
    assert slots[0].env_key_var == "LUNA_RENDER_API_KEY"
    assert slots[0].env_base_url_var == "LUNA_RENDER_BASE_URL"


def test_manifest_and_code_versions_agree() -> None:
    toml_version = tomllib.loads((PKG / "luna-plugin.toml").read_text())["version"]
    code_version = re.search(r'version="([^"]+)"', (PKG / "__init__.py").read_text()).group(1)
    assert toml_version == code_version == RenderPlugin.manifest.version
