# Deep Email OSINT

## holehe — Platform Registration Check

holehe checks if an email is registered on 120+ platforms by testing authorization endpoints.

```bash
holehe user@example.com
holehe user@example.com --no-clear --only-used  # only show confirmed registrations
```

**Caveat**: Many platforms (Google, Facebook, Instagram, etc.) have added CAPTCHAs and rate-limiting that make holehe return false negatives. Treat "not found" as inconclusive, not as confirmation of absence.

## maigret — Username from Email Prefix

The part before `@` in an email is often a username/handle. Run maigret on it:

```bash
maigret username --timeout 5
maigret username --timeout 5 --proxy socks5://127.0.0.1:9050
```

## Google Dork Queries (via SearXNG)

When investigating an email, run these SearXNG queries:

```
site:pastebin.com "user@example.com"
site:github.com "user@example.com"
site:gitlab.com "user@example.com"
site:stackoverflow.com "user@example.com"
filetype:pdf "user@example.com"
filetype:xlsx "user@example.com"
filetype:csv "user@example.com"
"user@example.com" filetype:txt
intitle:"user@example.com"
```

Also search the email prefix as a handle:
```
"username" site:instagram.com
"username" site:twitter.com
"username" site:github.com
```

## Corporate Domain Analysis

If the email uses a custom domain (not gmail/yahoo/etc):

```bash
# MX records — reveals mail provider
dig MX example.com +short

# Whois — domain registration data
whois example.com

# crt.sh — SSL certificate transparency
curl -s "https://crt.sh/?q=example.com&output=json"

# Subdomain enumeration
dig example.com ANY +short
```

## ProtonMail PKS — PGP Key Lookup

ProtonMail runs a public PGP key server. You can check if a ProtonMail address
has a registered PGP key (confirms the address exists):

```bash
curl -s "https://api.protonmail.ch/pks/lookup?op=get&search=user@protonmail.com"
```

- If the response contains `BEGIN PGP PUBLIC KEY BLOCK`, the address has a
  registered PGP key → **confirms the email exists**.
- If the response is empty or contains `No results`, the address has no key
  registered → **inconclusive** (the address may still exist without a key).
- Also check `user@proton.me` (short domain) as ProtonMail supports both.

This is one of the few reliable ways to verify a ProtonMail address without
sending an email, since ProtonMail does not support traditional mailbox
pinging.

## Workflow

When given an email address:
1. Run `holehe EMAIL` for platform registrations
2. Extract prefix, run `maigret PREFIX` in parallel
3. Run Google Dork queries via SearXNG for the full email
4. If custom domain: dig MX, whois, crt.sh
5. Cross-reference all findings with existing target dossier
6. Save to `./data/email_EMAIL.json`
