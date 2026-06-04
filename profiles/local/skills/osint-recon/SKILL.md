---
name: osint-recon
version: 1
category: reconnaissance
description: Conduct open-source intelligence gathering through domain analysis, social media profiling, network infrastructure checks, and public record searches using WHOIS, DNS tools, and API queries.
summary: Perform OSINT reconnaissance with environment setup and API credential handling

setup:
  - Check Python environment: If encountering 'externally managed' errors, create a virtual environment with `python3 -m venv` and install firecrawl-py via pip
  - Ensure API credentials are available for target platforms (OnlyFans, Pornhub, etc.)

constraints:
  - Requires specific platform API endpoints and credentials
  - Avoids ethical/privacy risks by requiring explicit user confirmation

workflow:
  1. Validate environment and install dependencies
  2. Use WHOIS and SSL analysis for domain verification
  3. When targeting adult directories, ask user to specify platforms first
  4. Execute API queries with proper authentication and error handling
---

## OSINT Reconnaissance Workflow

- **Ethical Note**: Avoid direct queries to adult platforms unless explicitly directed. Focus on public data and domain analysis.

1. **Domain Analysis**
   - Use `whois` command to gather domain registration details
   - Check for subdomains via DNS enumeration tools

2. **Social Media Profiling**
   - Search for public profiles on LinkedIn, Twitter, and GitHub
   - Use `search_files` to find patterns in publicly available documents

3. **Network Infrastructure**
   - Analyze SSL certificates for domain age and hosting providers
   - Use `web_extract` on known public repositories

4. **Public Records**
   - Search for legal filings, patents, or corporate records
   - Use `terminal` to run `curl` commands against public APIs

1. **Domain Analysis**
   - Use `whois` command to gather domain registration details
   - Check for subdomains via DNS enumeration tools

2. **Social Media Profiling**
   - Search for public profiles on LinkedIn, Twitter, and GitHub
   - Use `search_files` to find patterns in publicly available documents

3. **Network Infrastructure**
   - Analyze SSL certificates for domain age and hosting providers
   - Use `web_extract` on known public repositories

4. **Public Records**
   - Search for legal filings, patents, or corporate records
   - Use `terminal` to run `curl` commands against public APIs

Would you like me to create this skill and save it to your local profile?