---
name: each-sense
description: Generate images, videos, 3D models, and marketing assets using each::sense AI — a unified generative media platform with 500+ AI models. Use for product photos, ad creatives, UGC-style clips, avatar generation, 3D model creation, YouTube videos, and creative content production.
---

# each::sense — Generative Media AI Platform

Generate images, videos, 3D models, and marketing assets using each::sense — a unified AI agent that orchestrates 500+ generative models.

## What is each::sense?

each::sense is an intelligent layer for generative media that:
- Routes requests across 500+ specialized AI models
- Automatically selects the best model for each task
- Supports images, videos, 3D models, audio, and creative content
- Provides a single REST API for all generative tasks
- Uses Claude for natural language understanding and model orchestration

## API Reference

### Base URL
```
https://sense.eachlabs.run
```

### Authentication
```
X-API-Key: your-api-key-here
```

### Core Endpoints

#### Generate Image
```bash
curl -X POST https://sense.eachlabs.run/v1/generate \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Professional product photo of a white sneaker on marble background",
    "mode": "max",
    "width": 1024,
    "height": 1024,
    "model": "auto",
    "safety_checker": true
  }'
```

#### Generate Video
```bash
curl -X POST https://sense.eachlabs.run/v1/generate/video \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Cinematic drone shot of a mountain landscape at sunset",
    "duration": 5,
    "fps": 24,
    "resolution": "1080p"
  }'
```

#### Generate 3D Model
```bash
curl -X POST https://sense.eachlabs.run/v1/generate/3d \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Low-poly 3D model of a cartoon robot, game-ready",
    "format": "glb",
    "style": "lowpoly"
  }'
```

#### Edit Image
```bash
curl -X POST https://sense.eachlabs.run/v1/edit \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Change background to beach sunset",
    "image_url": "https://example.com/input.jpg",
    "strength": 0.8
  }'
```

### Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | required | Natural language description |
| `mode` | string | `max` | `max` (best quality) or `eco` (faster/cheaper) |
| `model` | string | `auto` | Model ID or `auto` for automatic selection |
| `width` | int | 1024 | Image width (px) |
| `height` | int | 1024 | Image height (px) |
| `image_urls` | array | [] | Input images for editing |
| `strength` | float | 0.7 | Edit strength (0.0-1.0) |
| `safety_checker` | bool | true | Enable content filtering |
| `session_id` | string | null | Session ID for multi-turn |
| `behavior` | string | `agent` | `agent`, `plan`, or `ask` |
| `web_search` | bool | false | Enable web search for context |
| `workflow_id` | string | null | Custom workflow ID |
| `version_id` | string | null | Workflow version ID |

### Streaming Response (SSE)
```bash
curl -X POST https://sense.eachlabs.run/v1/generate \
  -H "X-API-Key: your-api-key" \
  -H "Accept: text/event-stream" \
  -d '{"prompt": "A futuristic city at night"}'

# Response stream:
# event: progress
# data: {"percent": 25, "status": "selecting_model"}
#
# event: progress
# data: {"percent": 50, "status": "generating"}
#
# event: complete
# data: {"url": "https://cdn.eachlabs.ai/...", "model_used": "flux-1.1-pro"}
```

## Python SDK

```python
import requests, json, time

class EachSense:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://sense.eachlabs.run"
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        }
    
    def generate_image(self, prompt, width=1024, height=1024, mode="max", model="auto"):
        """Generate an image from text prompt."""
        resp = requests.post(
            f"{self.base_url}/v1/generate",
            headers=self.headers,
            json={
                "prompt": prompt,
                "width": width,
                "height": height,
                "mode": mode,
                "model": model,
            },
        )
        data = resp.json()
        return data.get("url") or data.get("image_url")
    
    def generate_video(self, prompt, duration=5, resolution="1080p"):
        """Generate a video from text prompt."""
        resp = requests.post(
            f"{self.base_url}/v1/generate/video",
            headers=self.headers,
            json={
                "prompt": prompt,
                "duration": duration,
                "resolution": resolution,
            },
        )
        return resp.json().get("url")
    
    def generate_3d(self, prompt, format="glb"):
        """Generate a 3D model from text prompt."""
        resp = requests.post(
            f"{self.base_url}/v1/generate/3d",
            headers=self.headers,
            json={"prompt": prompt, "format": format},
        )
        return resp.json().get("url")
    
    def edit_image(self, prompt, image_url, strength=0.7):
        """Edit an existing image."""
        resp = requests.post(
            f"{self.base_url}/v1/edit",
            headers=self.headers,
            json={
                "prompt": prompt,
                "image_url": image_url,
                "strength": strength,
            },
        )
        return resp.json().get("url")
    
    def generate_with_streaming(self, prompt, callback=None):
        """Generate with real-time progress streaming."""
        resp = requests.post(
            f"{self.base_url}/v1/generate",
            headers={**self.headers, "Accept": "text/event-stream"},
            json={"prompt": prompt},
            stream=True,
        )
        
        for line in resp.iter_lines():
            if line.startswith(b"event:"):
                event = line.decode().split(": ", 1)[1]
            elif line.startswith(b"data:"):
                data = json.loads(line.decode().split(": ", 1)[1])
                if callback:
                    callback(event, data)
                if event == "complete":
                    return data.get("url")

# Usage
sense = EachSense("your-api-key")

# Generate product photo
url = sense.generate_image(
    "Professional product photo of wireless headphones on white background, studio lighting",
    width=1024, height=1024, mode="max"
)
print(f"Image: {url}")

# Generate with streaming
def on_progress(event, data):
    if event == "progress":
        print(f"{data['percent']}% - {data['status']}")

url = sense.generate_with_streaming("A futuristic city at night", callback=on_progress)
```

## Use Cases & Prompt Templates

### Product Photography
```python
prompt = f"""
Professional product photo of {product_name}
Background: {background}
Lighting: {lighting_style}
Angle: {camera_angle}
Style: Commercial e-commerce, high-end
Resolution: 4K, sharp focus
"""
```

### Marketing Ad Creative
```python
prompt = f"""
Social media ad creative for {brand}
Product: {product}
Style: {style} (modern, playful, luxury, minimalist)
Text overlay: "{headline}"
Call to action: "{cta}"
Aspect ratio: {ratio} (1:1 for Instagram, 9:16 for Stories)
"""
```

### UGC-Style Video
```python
prompt = f"""
UGC-style video of {person_description}
Action: {action}
Setting: {setting}
Duration: 15 seconds
Style: Authentic, smartphone-quality, natural lighting
Music: Upbeat background track
"""
```

### 3D Model Generation
```python
prompt = f"""
3D model of {object}
Style: {style} (low-poly, realistic, cartoon, stylized)
Format: glb (game-ready)
Poly count: {poly_count}
Textures: PBR materials included
"""
```

### AI Avatar / Headshot
```python
prompt = f"""
Professional headshot of {description}
Style: {style} (corporate, creative, casual)
Background: {background}
Lighting: Studio lighting, soft shadows
Resolution: 4K
"""
```

## Available Models (Selection)

each::sense automatically selects from 500+ models. Key categories:

| Category | Example Models | Best For |
|----------|---------------|----------|
| **Image** | FLUX 1.1 Pro, SDXL, Midjourney v6, DALL-E 3 | Photos, illustrations, art |
| **Video** | Kling, Runway Gen-3, Pika, Sora | Short clips, animations |
| **3D** | Meshy, Luma AI, Tripo3D | Game assets, product viz |
| **Audio** | ElevenLabs, Bark, MusicGen | Voice, music, SFX |
| **Code** | Claude, GPT-4o | Code generation |

## Pricing

| Mode | Quality | Speed | Cost |
|------|---------|-------|------|
| `max` | Best | Slower | Higher |
| `eco` | Good | Faster | Lower |

Check current pricing at: https://eachlabs.ai/pricing

## Error Handling

```python
try:
    url = sense.generate_image("A beautiful sunset")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Invalid API key")
    elif e.response.status_code == 429:
        print("Rate limited — retry after delay")
    elif e.response.status_code >= 500:
        print("Server error — retry with backoff")
```

## Common Issues

| Problem | Solution |
|---------|----------|
| `401 Unauthorized` | Check API key is valid and has credits |
| `429 Rate Limited` | Add exponential backoff, reduce request frequency |
| `500 Server Error` | Retry with backoff, check status.eachlabs.ai |
| Poor quality results | Use `mode: "max"`, add more detail to prompt |
| Slow generation | Use `mode: "eco"` for faster results |
| Content filtered | Adjust `safety_checker: false` (if allowed) or rephrase prompt |
| Model not found | Use `model: "auto"` or check available models |

## Related Skills

- `ai-headshot-generation` — Professional headshot generation
- `product-photo-generation` — E-commerce product photography
- `meta-ad-creative-generation` — Social media ad creatives
- `youtube-video-generation` — YouTube video creation
- `3d-model-generation` — 3D asset creation
- `ai-avatar-generation` — Avatar and character creation

## Source

- **API Docs:** https://docs.eachlabs.ai
- **each::sense Overview:** https://docs.eachlabs.ai/sense/overview
- **GitHub:** https://github.com/openclaw/skills
- **LobeHub:** https://lobehub.com/skills/openclaw-skills-each-sense
