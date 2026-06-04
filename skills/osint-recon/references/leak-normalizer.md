# Breach Data Normalizer

## Purpose

Parse unstructured text dumps, leak databases, pastebin scrapes, or chat logs to extract and normalize OSINT indicators.

## Extraction Targets

| Type | Pattern | Normalization |
|------|---------|---------------|
| Email | `[\w.+-]+@[\w-]+\.[\w.-]+` | Lowercase, group by domain |
| Phone (E.164) | Various formats | Strip to `+CCXXXXXXXX` |
| Username/Handle | Platform-specific patterns | Extract from URLs |
| Name/Surname | Paired with email/phone | Preserve original case |
| Crypto Wallet | `0x[A-Fa-f0-9]{40}` (ETH), `bc1` (BTC) | Exact match |
| System Path | `/home/user/...`, `C:\Users\...` | Flag as exposure risk |
| IP Address | `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}` | Validate range |

## Phone Normalization Rules

- Norwegian: 8 digits → `+47XXXXXXXX`
- US: 10 digits → `+1XXXXXXXXXX`
- UK: 10 digits → `+44XXXXXXXXXX`
- If country code present, preserve it
- If ambiguous (no CC, no area code pattern): flag as `UNKNOWN_CC`

## Output Format

### Markdown Table
```
| Type     | Value                | Domain/Carrier | Associated Name | Source Row |
|----------|----------------------|-----------------|-----------------|------------|
| email    | user@example.com     | example.com     | John Doe        | 1          |
| phone    | +4712345678          | Telenor NO      | John Doe        | 1          |
| handle   | @johndoe             | instagram.com   | -               | 3          |
| wallet   | 0xABC123...          | ETH             | Jane            | 5          |
| path     | /home/john/...       | LOCAL           | John            | 7          |
```

### JSON Output
```json
{
  "parsed_at": "2026-05-24T16:00:00Z",
  "source": "pastebin_leak_scrape",
  "indicators": [
    {
      "type": "email",
      "value": "user@example.com",
      "domain": "example.com",
      "associated_name": "John Doe",
      "row": 1
    },
    {
      "type": "phone",
      "value": "+4712345678",
      "carrier": "Telenor NO",
      "country_code": "+47",
      "associated_name": "John Doe",
      "row": 1
    },
    {
      "type": "system_path",
      "value": "/home/john/documents/",
      "associated_name": "John",
      "row": 7,
      "risk": "HIGH — exposes username and directory structure"
    }
  ],
  "stats": {
    "total_rows": 150,
    "emails_found": 45,
    "phones_found": 30,
    "handles_found": 12,
    "wallets_found": 3,
    "paths_found": 2,
    "unknown_cc_phones": 5
  }
}
```

## Filtering Rules

Strip these false positives:
- `example.com`, `test.com`, `localhost`, `sentry.io`
- Template emails: `noreply@`, `no-reply@`, `admin@`, `postmaster@`
- HTML artifacts: `href=`, `src=`, CSS class names
- Whitespace-only or single-character strings

## Correlation Logic

When multiple indicators share a row or adjacent rows:
- Link email + phone + name as belonging to same person
- Flag system paths with usernames as exposure risks
- Group by domain to identify corporate clusters
- Note disposable email providers (guerrillamail, tempmail, etc.)
