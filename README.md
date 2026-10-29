<p align="center"><img src="assets/logo.png" alt="WarmGTM" width="96" height="96"></p>

# WarmGTM plugin

Connect Grok Bot, Cursor or ChatGPT to your [WarmGTM](https://warmgtm.com) workspace. Ask about your outreach in plain language, then review and approve what goes out.

- **Analytics:** campaign funnels, reply rates, and what is running right now
- **Inbox:** who replied, full conversation threads, drafted replies you approve before sending
- **Campaigns:** build sequences from templates or your own steps, preview every message, launch on approval, pause or resume individual leads
- **Leads:** build lead lists from search URLs, profile URLs or post engagement
- **Posts:** draft, schedule and publish posts with images, PDFs, video and @mentions
- **Social Signals:** track keywords, review matching posts, approve comments
- **Tags, CRM sync and webhooks**

The plugin is free to install. It works with your existing WarmGTM account and the plan you already have.

## What's in this repo

| Path | Purpose |
|---|---|
| `.grok-plugin/plugin.json`, `.cursor-plugin/plugin.json` | Plugin manifests |
| `.mcp.json`, `mcp.json` | Points to WarmGTM's hosted MCP server, `https://mcp.warmgtm.com/mcp` |
| `skills/warmgtm/SKILL.md` | Tells the assistant how to use the tools, and which actions need your approval |
| `assets/` | Logo |
| `openai/` | OpenAI (ChatGPT / Codex) manifest and `mcp.json`, packaged by `scripts/build-openai-zip.sh` |

## Connecting

1. Install the plugin from the Grok Bot, Cursor or ChatGPT plugin directory.
2. When asked to connect, a WarmGTM sign-in page opens in your browser. Sign in with your WarmGTM email and password.
   - Signed up with Google? Choose **Use an API key instead** and paste a key from WarmGTM **Settings → API Keys**.
3. That's it. The connection uses OAuth 2.1 (PKCE), and tokens refresh on their own.

To disconnect, remove the plugin, or deactivate the key named *MCP connector (created by OAuth sign-in)* in WarmGTM **Settings → API Keys**.

## OpenAI package

The ChatGPT directory takes a ZIP rather than a repo. Build it with:

```sh
./scripts/build-openai-zip.sh
```

This copies `openai/plugin.json`, `openai/mcp.json`, `skills/` and `assets/logo.png` into one package, checks the directory's limits (field lengths, 5 positive and 3 negative review cases, square PNG icons, OAuth with no client secret), and writes `dist/warmgtm-openai-<version>.zip`. Bump `version` in `openai/plugin.json` before each re-upload.

## You stay in control

Anything that reaches a real person or changes live outreach waits for your explicit approval first: sending a message, approving a comment, publishing a post, launching a campaign, adding leads to a running campaign, changing campaign limits, deleting, or sending data to a CRM or webhook. The assistant shows you exactly what will happen (recipient, text, lead count, timing) before it acts. Sending limits set in WarmGTM always apply.

Everything runs through the LinkedIn accounts you connected to WarmGTM, under the limits you configured there.

## Privacy and support

- Privacy policy: https://warmgtm.com/privacy
- Terms: https://warmgtm.com/terms
- Support: support@warmgtm.com
- Security reports: security@warmgtm.com

## License

MIT
