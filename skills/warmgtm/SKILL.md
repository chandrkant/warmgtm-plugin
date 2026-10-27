---
name: warmgtm
description: "Work with the user's WarmGTM account: campaign and reply analytics, leads and lead lists, LinkedIn inbox conversations, posts, Social Signals (keyword posts), tags, CRM sync and webhooks. Use when the user asks about their outreach, campaigns, prospects, replies, posts or WarmGTM data. Anything that contacts a real person or changes live outreach needs the user's explicit confirmation first."
---

# WarmGTM

WarmGTM runs outreach through LinkedIn accounts the user has connected to their own WarmGTM workspace ("senders"). These tools act on that workspace. Every message, comment, post and campaign step goes out under the user's real name to real people, so treat write actions with care.

## Start here

1. Call `get_encrypted_identifiers` before anything else. It returns the encrypted IDs for senders, campaigns and organisation members that most other tools need. Never guess or invent an ID.
2. If the user has more than one sender and the request doesn't say which, ask.
3. For questions ("how is X doing", "who replied", "show me…"), use only read tools. Don't change anything while answering a question.

## Confirm before acting — always

These actions reach real people, publish publicly, share data outside WarmGTM, or change live outreach. **Before calling any of them, show the user exactly what will happen and wait for an explicit yes in this conversation.** Show the recipient or audience, the full text, the campaign, how many leads it affects, and when it happens.

| Tool | Why it needs confirmation |
|---|---|
| `send_message` | Sends a LinkedIn message as the user |
| `set_comment` (approve) | Posts a public comment on LinkedIn |
| `create_post` / `update_post` with `schedule_now` or `scheduled_at` | Publishes or schedules a public post |
| `activate_predefined_campaign` | Starts sending to every lead in the campaign |
| `create_predefined_campaign` / `create_manual_campaign` with `is_draft: false` | Creates the campaign already live, so it starts sending |
| `add_leads_to_campaign`, `create_lead_list` linked to a running campaign, `unpause_campaign_leads` | Puts people into live outreach |
| `append_campaign_steps` on an active campaign | Adds steps that will send |
| `update_campaign_settings` | Changes limits, schedule or behaviour of live outreach |
| `delete_post`, `delete_webhook`, `delete_keyword_post` | Permanent |
| `sync_contacts_to_crm`, `send_chat_webhook_data`, `create_webhook`, `update_webhook` | Sends prospect data to another system |
| `create_api_key` | Issues a new credential |

Rules:

- One yes covers the one action you showed. Ask again for the next one, and again if anything changed (different text, more leads, another recipient).
- Never send messages in a loop over many people. For more than a handful of recipients, build a campaign and let WarmGTM pace it.
- Keep the user's sending limits. Don't raise daily caps or shorten delays unless the user asks for a specific value, and then say what the new value is.
- If a tool result is unclear or fails, report it. Don't retry a send or an activation automatically; it may have gone through.

Safe without confirmation: every read tool, `pause_campaign_leads` (stops outreach), `generate_content` (draft only), `create_post` with neither `schedule_now` nor `scheduled_at` (saves a draft), creating a campaign as a draft (leave `is_draft` unset), and `preview_predefined_campaign`.

## Common tasks

**How is my outreach doing?**
`get_dashboard_info` for the workspace overview, `get_active_campaigns` for what is running now, `get_campaign_info` and `get_campaign_detail` for one campaign's funnel and steps.

**Who replied, and what did they say?**
`get_chat_members` to list conversations, `get_member_conversations` for one thread, `get_campaign_lead_conversations` for replies to campaign leads. To answer someone, draft the reply, show it, wait for a yes, then `send_message` (the recipient must be a 1st-degree connection of the sender).

**Build and launch a campaign**
1. Get leads: `create_leads` (LinkedIn or Sales Navigator search URL, post likers/commenters and other sources), `create_lead_list` (exact profile URLs) or `import_post_leads`. Check them with `get_lead_lists` / `get_lead_list_members`.
2. Create it as a draft with `create_predefined_campaign` (template flow, e.g. `starter_connection`) or `create_manual_campaign` (your own steps). Leave `is_draft` unset so it stays a draft.
3. Show the full sequence with `preview_predefined_campaign` on the returned `campaign_routine_id`, including every message body. It is the only tool that can show a draft's steps.
4. Only after the user approves the preview and the lead count: `activate_predefined_campaign`.

**Stop or resume a lead**
`get_campaign_leads` to find the enrolment, then `pause_campaign_leads`. Resuming with `unpause_campaign_leads` needs confirmation.

**Posts**
`generate_content` for a draft, then `create_post` as a draft. Publish or schedule only on confirmation. Publishing is asynchronous: poll `get_post` until the status is `published` or `failed`. Use `search_post_mentions` to find people or companies to @mention.

**Social Signals (keyword posts)**
`fetch_linkedin_keyword_posts` to track a keyword, `get_linkedin_keyword_post_status` for sync status, `retrieve_keyword_posts` for the matching posts. Comment approvals: `get_comments_list`, then `set_comment` per comment after the user approves it.

**Tags, CRM and webhooks**
Call `get_tags` before `assign_tags` or `unassign_tags`. `get_crm_integrations` and `get_webhooks` are read-only. Syncing to a CRM or a webhook needs confirmation.
