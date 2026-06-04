# Phone Number OSINT (PHINT)

## PhoneInfoga

PhoneInfoga is an advanced phone number scanning tool. Install:
```bash
# Download pre-built binary (no Go required)
curl -sL "https://github.com/sundowndev/phoneinfoga/releases/latest/download/phoneinfoga_Linux_x86_64.tar.gz" \
  -o /tmp/phoneinfoga.tar.gz
tar xzf /tmp/phoneinfoga.tar.gz -C /tmp/
cp /tmp/phoneinfoga ~/.local/bin/phoneinfoga
chmod +x ~/.local/bin/phoneinfoga
```

### Basic Scan
```bash
~/.local/bin/phoneinfoga scan -n "+4712345678"
~/.local/bin/phoneinfoga scan -n "+4712345678" -f E164
```

### Output includes:
- Number format (E.164, national, international)
- Country and region
- Carrier/line type
- Reputation and scam scores
- Social media links found via public footprints
- Google dork result counts

### List available scanners
```bash
~/.local/bin/phoneinfoga scanners
```

### Tor routing
PhoneInfoga supports SOCKS proxy:
```bash
~/.local/bin/phoneinfoga scan -n "+4712345678" --proxy "socks5://127.0.0.1:9050"
```

## ignorant

ignorant checks if a phone number is registered on social platforms.

```bash
pip3 install --break-system-packages ignorant
python3 -m ignorant --phone "+4712345678" --platform snapchat
python3 -m ignorant --phone "+4712345678" --platform instagram
python3 -m ignorant --phone "+4712345678" --platform whatsapp
python3 -m ignorant --phone "+4712345678" --platform facebook
```

## Phone Normalization (E.164)

When parsing phone numbers from breach dumps:
- Strip all non-numeric characters except leading `+`
- Norwegian: `+47` + 8 digits
- US/Canada: `+1` + 10 digits
- UK: `+44` + 10 digits
- If country code missing, flag as ambiguous

## Workflow

When given a phone number:
1. Run phoneinfoga scan for carrier/footprint
2. Run ignorant for platform registrations
3. Add to Graphviz graph as blue node
4. Save to ./data/phone_NUMBER.json
