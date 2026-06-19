# plugin-render

Render.com service management for [Luna](https://github.com/huemorgan/luna):
manage services, trigger and inspect deploys, read/set/delete environment
variables, and read live logs.

This is a **Luna plugin** built against the Luna Plugin SDK (`luna_sdk`) v0. It
imports nothing from `luna.*` — only the stable SDK surface (including
`SkillDef` and `get_current_user` for route auth) — so it installs from the Luna
marketplace and runs without being part of Luna core.

## Install

In Luna: **Marketplace → Luna Official → plugin-render → Install**. Then open
**Settings → Connectors → Render**, paste a Render API key, and connect.

## What it does

| Tool | Purpose |
|---|---|
| `render_list_services` | List all Render services. |
| `render_get_service` | Get details of a specific service. |
| `render_restart_service` | Restart a service. |
| `render_suspend_service` | Suspend (stop) a service. |
| `render_resume_service` | Resume a suspended service. |
| `render_get_live_logs` | Read recent logs from a service. |
| `render_trigger_deploy` | Trigger a new deploy. |
| `render_list_deploys` | List recent deploys. |
| `render_get_deploy` | Get a specific deploy. |
| `render_list_env_vars` | List a service's env vars. |
| `render_set_env_var` | Set an env var (owner-approved). |
| `render_delete_env_var` | Delete an env var (owner-approved). |

Tools are skill-gated and grouped into skills (`render-services`,
`render-deploys`, `render-env`, `render-logs`). The API key is stored in Luna's
vault; auth-gated REST routes live under `/api/p/plugin-render/*`.

## Settings UI

The connector's settings panel is served as a themed **iframe** from the
plugin's own managed directory (`interface/webui/settings/index.html`), so it
ships its own UI without compiling into Luna core's bundle. Crash-isolated and
React-version immune.

## Layout

```
plugin_render/
  __init__.py        # the plugin (luna_sdk only) — tools + skills + settings tab
  client.py          # RenderClient (pure httpx)
  routes.py          # REST routes (SDK auth) + iframe UI serving
  state.py           # process-level RenderClient holder
  interface/webui/settings/index.html   # the iframe settings page
  luna-plugin.toml   # the data manifest the marketplace reads
```

## License

MIT — see [LICENSE](./LICENSE).
