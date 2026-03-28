"""GetResponse MCP Server - connects GetResponse email marketing to Claude Code."""

import os
import json
import httpx
from mcp.server.fastmcp import FastMCP

API_KEY = os.environ.get("GETRESPONSE_API_KEY", "")
BASE_URL = "https://api.getresponse.com/v3"

mcp = FastMCP("getresponse")


def _headers():
    return {
        "X-Auth-Token": f"api-key {API_KEY}",
        "Content-Type": "application/json",
    }


def _get(endpoint: str, params: dict | None = None) -> dict | list:
    with httpx.Client(timeout=30) as client:
        r = client.get(f"{BASE_URL}{endpoint}", headers=_headers(), params=params)
        r.raise_for_status()
        return r.json()


def _get_with_headers(endpoint: str, params: dict | None = None) -> tuple[dict | list, dict]:
    with httpx.Client(timeout=30) as client:
        r = client.get(f"{BASE_URL}{endpoint}", headers=_headers(), params=params)
        r.raise_for_status()
        return r.json(), dict(r.headers)


def _post(endpoint: str, data: dict) -> dict:
    with httpx.Client(timeout=30) as client:
        r = client.post(f"{BASE_URL}{endpoint}", headers=_headers(), json=data)
        r.raise_for_status()
        return r.json()


# ── Tool 1: Account Info ─────────────────────────────────────────────

@mcp.tool()
def get_account_info() -> str:
    """Get GetResponse account information (name, email, plan, subscribers count)."""
    data = _get("/accounts")
    return json.dumps(data, indent=2, ensure_ascii=False)


# ── Tool 2: List Campaigns (mailing lists) ───────────────────────────

@mcp.tool()
def list_campaigns(page: int = 1, per_page: int = 25) -> str:
    """List all campaigns (mailing lists) in GetResponse.

    Args:
        page: Page number (default 1)
        per_page: Results per page (default 25, max 100)
    """
    data = _get("/campaigns", params={"page": page, "perPage": per_page})
    results = []
    for c in data:
        cid = c.get("campaignId")
        _, hdrs = _get_with_headers(f"/contacts", params={"query[campaignId]": cid, "perPage": 1})
        count = int(hdrs.get("TotalCount", hdrs.get("totalcount", hdrs.get("Total-Count", 0))))
        results.append({
            "id": cid,
            "name": c.get("name"),
            "subscribers": count,
            "is_default": c.get("isDefault", "false"),
            "created": c.get("createdOn"),
        })
    results.sort(key=lambda x: x["subscribers"], reverse=True)
    return json.dumps(results, indent=2, ensure_ascii=False)


# ── Tool 3: List Contacts ────────────────────────────────────────────

@mcp.tool()
def list_contacts(
    campaign_id: str = "",
    query: str = "",
    page: int = 1,
    per_page: int = 25,
) -> str:
    """List contacts (subscribers) with optional filtering.

    Args:
        campaign_id: Filter by campaign/list ID (optional)
        query: Search by name or email (optional)
        page: Page number (default 1)
        per_page: Results per page (default 25, max 100)
    """
    params = {"page": page, "perPage": per_page}
    if campaign_id:
        params["query[campaignId]"] = campaign_id
    if query:
        params["query[email]"] = query

    data = _get("/contacts", params=params)
    results = []
    for c in data:
        results.append({
            "id": c.get("contactId"),
            "email": c.get("email"),
            "name": c.get("name"),
            "campaign": c.get("campaign", {}).get("name"),
            "status": c.get("status"),
            "created": c.get("createdOn"),
            "engagement_score": c.get("engagementScore"),
        })
    return json.dumps(results, indent=2, ensure_ascii=False)


# ── Tool 4: Get Contact Details ──────────────────────────────────────

@mcp.tool()
def get_contact(contact_id: str) -> str:
    """Get detailed information about a specific contact.

    Args:
        contact_id: The contact ID to look up
    """
    data = _get(f"/contacts/{contact_id}")
    return json.dumps(data, indent=2, ensure_ascii=False)


# ── Tool 5: List Newsletters ─────────────────────────────────────────

@mcp.tool()
def list_newsletters(
    status: str = "",
    page: int = 1,
    per_page: int = 25,
) -> str:
    """List newsletters with optional status filter.

    Args:
        status: Filter by status: 'enabled', 'disabled', 'draft' (optional)
        page: Page number (default 1)
        per_page: Results per page (default 25, max 100)
    """
    params = {"page": page, "perPage": per_page}
    if status:
        params["query[status]"] = status

    data = _get("/newsletters")
    results = []
    for n in data:
        stats = n.get("statistics", {})
        results.append({
            "id": n.get("newsletterId"),
            "subject": n.get("subject"),
            "status": n.get("status"),
            "sent_on": n.get("sendOn"),
            "campaign": n.get("campaign", {}).get("name"),
            "delivered": stats.get("delivered"),
            "open_rate": stats.get("openRate"),
            "click_rate": stats.get("clickRate"),
        })
    return json.dumps(results, indent=2, ensure_ascii=False)


# ── Tool 6: Newsletter Statistics ─────────────────────────────────────

@mcp.tool()
def get_newsletter_stats(newsletter_id: str) -> str:
    """Get detailed statistics for a specific newsletter.

    Args:
        newsletter_id: The newsletter ID
    """
    data = _get(f"/newsletters/{newsletter_id}")
    return json.dumps(data, indent=2, ensure_ascii=False)


# ── Tool 7: Get Autoresponders ────────────────────────────────────────

@mcp.tool()
def list_autoresponders(
    campaign_id: str = "",
    page: int = 1,
    per_page: int = 25,
) -> str:
    """List autoresponders (automated email sequences).

    Args:
        campaign_id: Filter by campaign/list ID (optional)
        page: Page number (default 1)
        per_page: Results per page (default 25, max 100)
    """
    params = {"page": page, "perPage": per_page}
    if campaign_id:
        params["query[campaignId]"] = campaign_id

    data = _get("/autoresponders", params=params)
    results = []
    for a in data:
        stats = a.get("statistics", {})
        results.append({
            "id": a.get("autoresponderId"),
            "subject": a.get("subject"),
            "status": a.get("status"),
            "day_of_cycle": a.get("triggerSettings", {}).get("dayOfCycle"),
            "campaign": a.get("campaign", {}).get("name"),
            "delivered": stats.get("delivered"),
            "open_rate": stats.get("openRate"),
            "click_rate": stats.get("clickRate"),
        })
    return json.dumps(results, indent=2, ensure_ascii=False)


# ── Tool 8: Search Contacts ──────────────────────────────────────────

@mcp.tool()
def search_contacts(email: str = "", name: str = "", created_after: str = "") -> str:
    """Search contacts by email, name, or creation date.

    Args:
        email: Search by email (partial match)
        name: Search by name (partial match)
        created_after: Filter contacts created after this date (YYYY-MM-DD)
    """
    params = {"perPage": 50}
    if email:
        params["query[email]"] = email
    if name:
        params["query[name]"] = name
    if created_after:
        params["query[createdOn][from]"] = created_after

    data = _get("/contacts", params=params)
    results = []
    for c in data:
        results.append({
            "email": c.get("email"),
            "name": c.get("name"),
            "campaign": c.get("campaign", {}).get("name"),
            "status": c.get("status"),
            "created": c.get("createdOn"),
        })
    return json.dumps(results, indent=2, ensure_ascii=False)


# ── Tool 9: Subscriber Stats Summary ─────────────────────────────────

@mcp.tool()
def get_subscriber_stats() -> str:
    """Get a summary of subscriber statistics across all campaigns."""
    campaigns = _get("/campaigns", params={"perPage": 100})
    total = 0
    breakdown = []
    for c in campaigns:
        cid = c.get("campaignId")
        _, hdrs = _get_with_headers(f"/contacts", params={"query[campaignId]": cid, "perPage": 1})
        count = int(hdrs.get("TotalCount", hdrs.get("totalcount", hdrs.get("Total-Count", 0))))
        total += count
        breakdown.append({
            "campaign": c.get("name"),
            "subscribers": count,
        })
    breakdown.sort(key=lambda x: x["subscribers"], reverse=True)
    result = {"total_subscribers": total, "by_campaign": breakdown}
    return json.dumps(result, indent=2, ensure_ascii=False)


# ── Run ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
