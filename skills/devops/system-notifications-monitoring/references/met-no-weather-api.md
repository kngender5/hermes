# MET Norway Locationforecast API

Free weather API, no key required. Rate limit for reasonable use.

## Endpoint

```
GET https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={LAT}&lon={LON}
```

**Required header:** `User-Agent: <app name>` (without it, you get 403)

## Norwegian City Coordinates

| City | Lat | Lon |
|------|-----|-----|
| Oslo | 59.9139 | 10.7522 |
| Tromsø | 69.6492 | 18.9553 |
| Bergen | 60.3913 | 5.3221 |
| Trondheim | 63.4305 | 10.3951 |
| Stavanger | 58.9700 | 5.7331 |

## JSON Parsing (python3)

```python
import json, sys
d = json.load(sys.stdin)

ts = d['properties']['timeseries'][0]
details = ts['data']['instant']['details']

temp = details['air_temperature']
wind = details['wind_speed']
humidity = details['relative_humidity']

next1h = ts['data']['next_1_hours']
summary = next1h['summary']['symbol_code']
try:
    rain = next1h['details']['precipitation_amount']
except KeyError:
    rain = 0
```

## Symbol Codes (partial)

- `clearsky_day` / `clearsky_night`
- `fair_day` / `fair_night`
- `partlycloudy_day` / `partlycloudy_night`
- `cloudy`
- `rainshowers_day` / `rainshowers_night`
- `rain`
- `heavyrain`
- `snow`
- `sleet`
- `fog`
