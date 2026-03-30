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


def _delete(endpoint: str) -> bool:
    with httpx.Client(timeout=30) as client:
        r = client.delete(f"{BASE_URL}{endpoint}", headers=_headers())
        r.raise_for_status()
        return True


def _patch(endpoint: str, data: dict) -> dict:
    with httpx.Client(timeout=30) as client:
        r = client.patch(f"{BASE_URL}{endpoint}", headers=_headers(), json=data)
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


# ── Tool 10: Create Contact ──────────────────────────────────────────

@mcp.tool()
def create_contact(email: str, campaign_id: str, name: str = "", day_of_cycle: int = 0) -> str:
    """Add a new contact to a campaign (mailing list).

    Args:
        email: Contact email address
        campaign_id: Campaign/list ID to add the contact to
        name: Contact name (optional)
        day_of_cycle: Autoresponder day of cycle (default 0)
    """
    payload = {
        "email": email,
        "campaign": {"campaignId": campaign_id},
        "dayOfCycle": day_of_cycle,
    }
    if name:
        payload["name"] = name
    data = _post("/contacts", payload)
    return json.dumps(data, indent=2, ensure_ascii=False)


# ── Tool 11: Update Contact ─────────────────────────────────────────

@mcp.tool()
def update_contact(
    contact_id: str,
    name: str = "",
    campaign_id: str = "",
    note: str = "",
) -> str:
    """Update an existing contact's details.

    Args:
        contact_id: The contact ID to update
        name: New name (optional)
        campaign_id: Move to a different campaign/list (optional)
        note: Add a note to the contact (optional)
    """
    payload = {}
    if name:
        payload["name"] = name
    if campaign_id:
        payload["campaign"] = {"campaignId": campaign_id}
    if note:
        payload["note"] = note
    data = _post(f"/contacts/{contact_id}", payload)
    return json.dumps(data, indent=2, ensure_ascii=False)


# ── Tool 12: Delete Contact ─────────────────────────────────────────

@mcp.tool()
def delete_contact(contact_id: str) -> str:
    """Delete a contact permanently.

    Args:
        contact_id: The contact ID to delete
    """
    _delete(f"/contacts/{contact_id}")
    return json.dumps({"status": "deleted", "contact_id": contact_id}, indent=2)


# ── Tool 13: Create Campaign ────────────────────────────────────────

@mcp.tool()
def create_campaign(name: str, language_code: str = "PL") -> str:
    """Create a new campaign (mailing list).

    Args:
        name: Campaign name
        language_code: Two-letter language code (default PL)
    """
    payload = {
        "name": name,
        "languageCode": language_code,
    }
    data = _post("/campaigns", payload)
    return json.dumps(data, indent=2, ensure_ascii=False)


# ── Tool 14: Update Campaign ────────────────────────────────────────

@mcp.tool()
def update_campaign(campaign_id: str, name: str = "", language_code: str = "") -> str:
    """Update a campaign's settings.

    Args:
        campaign_id: The campaign ID to update
        name: New campaign name (optional)
        language_code: New language code (optional)
    """
    payload = {}
    if name:
        payload["name"] = name
    if language_code:
        payload["languageCode"] = language_code
    data = _post(f"/campaigns/{campaign_id}", payload)
    return json.dumps(data, indent=2, ensure_ascii=False)


# ── Tool 15: Delete Campaign ────────────────────────────────────────

@mcp.tool()
def delete_campaign(campaign_id: str) -> str:
    """Delete a campaign (mailing list) permanently.

    Args:
        campaign_id: The campaign ID to delete
    """
    _delete(f"/campaigns/{campaign_id}")
    return json.dumps({"status": "deleted", "campaign_id": campaign_id}, indent=2)


# ── Tool 16: List Tags ──────────────────────────────────────────────

@mcp.tool()
def list_tags(page: int = 1, per_page: int = 25) -> str:
    """List all tags.

    Args:
        page: Page number (default 1)
        per_page: Results per page (default 25, max 100)
    """
    data = _get("/tags", params={"page": page, "perPage": per_page})
    results = []
    for t in data:
        results.append({
            "id": t.get("tagId"),
            "name": t.get("name"),
            "created": t.get("createdOn"),
        })
    return json.dumps(results, indent=2, ensure_ascii=False)


# ── Tool 17: Create Tag ─────────────────────────────────────────────

@mcp.tool()
def create_tag(name: str) -> str:
    """Create a new tag.

    Args:
        name: Tag name
    """
    data = _post("/tags", {"name": name})
    return json.dumps(data, indent=2, ensure_ascii=False)


# ── Tool 18: Assign Tag to Contact ──────────────────────────────────

@mcp.tool()
def assign_tag_to_contact(contact_id: str, tag_id: str) -> str:
    """Assign a tag to a contact.

    Args:
        contact_id: The contact ID
        tag_id: The tag ID to assign
    """
    data = _post(f"/contacts/{contact_id}/tags", {"tags": [{"tagId": tag_id}]})
    return json.dumps(data, indent=2, ensure_ascii=False)


# ── Tool 19: Remove Tag from Contact ────────────────────────────────

@mcp.tool()
def remove_tag_from_contact(contact_id: str, tag_id: str) -> str:
    """Remove a tag from a contact.

    Args:
        contact_id: The contact ID
        tag_id: The tag ID to remove
    """
    _delete(f"/contacts/{contact_id}/tags/{tag_id}")
    return json.dumps({"status": "removed", "contact_id": contact_id, "tag_id": tag_id}, indent=2)


# ── Tool 20: List Custom Fields ─────────────────────────────────────

@mcp.tool()
def list_custom_fields(page: int = 1, per_page: int = 25) -> str:
    """List all custom fields.

    Args:
        page: Page number (default 1)
        per_page: Results per page (default 25, max 100)
    """
    data = _get("/custom-fields", params={"page": page, "perPage": per_page})
    results = []
    for f in data:
        results.append({
            "id": f.get("customFieldId"),
            "name": f.get("name"),
            "type": f.get("fieldType"),
            "format": f.get("format"),
            "values": f.get("values", []),
        })
    return json.dumps(results, indent=2, ensure_ascii=False)


# ── Tool 21: Create Custom Field ────────────────────────────────────

@mcp.tool()
def create_custom_field(name: str, field_type: str = "text", values: list[str] | None = None) -> str:
    """Create a new custom field.

    Args:
        name: Field name
        field_type: Field type: 'text', 'textarea', 'radio', 'checkbox', 'select' (default 'text')
        values: Predefined values for radio/checkbox/select fields (optional)
    """
    payload = {"name": name, "type": field_type}
    if values:
        payload["values"] = values
    data = _post("/custom-fields", payload)
    return json.dumps(data, indent=2, ensure_ascii=False)


# ── Run ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
