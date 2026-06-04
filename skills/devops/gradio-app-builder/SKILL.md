---
name: gradio-app-builder
description: Build, launch, and deploy Gradio web apps — demos, dashboards, ML UIs. Handles local dev, HF Spaces, Colab, and Docker deployment.
---

# Gradio App Builder

Build interactive web UIs for Python functions, ML models, APIs, and tools.

## When to Use

- User wants a web UI for a Python function/model
- Building demos, dashboards, calculators, or tools
- Deploying to HuggingFace Spaces (permanent, free)
- Creating Colab notebooks with public share links

## NOT For

- Complex multi-page apps → use Streamlit or Flask
- Production APIs → use FastAPI

## Install

```bash
pip install gradio>=4.0
```

## Core Patterns

### 1. Quick Interface

```python
import gradio as gr

def greet(name, intensity):
    return "Hello " * intensity + name + "!"

demo = gr.Interface(
    fn=greet,
    inputs=["text", gr.Slider(1, 10)],
    outputs=["text"],
)
demo.launch()
```

### 2. Blocks (flexible layouts)

```python
import gradio as gr

with gr.Blocks(title="My App") as demo:
    gr.Markdown("# My App")
    with gr.Row():
        input_text = gr.Textbox(label="Input")
        output_text = gr.Textbox(label="Output")
    btn = gr.Button("Run")
    btn.click(fn=process, inputs=input_text, outputs=output_text)

demo.launch()
```

### 3. Chat Interface

```python
import gradio as gr

def chat(message, history):
    response = model.generate(message)
    return response

demo = gr.ChatInterface(fn=chat)
demo.launch()
```

### 4. State

```python
with gr.Blocks() as demo:
    state = gr.State(value=0)
    counter = gr.Number(label="Count")
    btn = gr.Button("+1")
    btn.click(lambda s: s+1, inputs=state, outputs=[state, counter])
```

### 5. File Upload

```python
with gr.Blocks() as demo:
    file_input = gr.File(label="Upload", file_types=[".pdf", ".txt"])
    file_output = gr.File(label="Download")
    btn = gr.Button("Process")
    btn.click(fn=process_file, inputs=file_input, outputs=file_output)
```

### 6. Plotting

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def plot_sine(frequency):
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 1000)
    ax.plot(x, np.sin(frequency * x))
    return fig

demo = gr.Interface(plot_sine, gr.Slider(1, 10), gr.Plot())
demo.launch()
```

## Launch Options

### Local

```python
demo.launch(server_name="0.0.0.0", server_port=7860, show_error=True)
```

### Public Share Link (temporary)

```python
demo.launch(share=True)  # *.gradio.live URL
```

**⚠️ Share links expire** when the script stops. For permanent links, use HF Spaces.

### Colab

```python
demo.launch(share=True, debug=True)
```

## HuggingFace Spaces (Permanent Free Hosting)

### Project Structure

```
my-space/
├── app.py
├── requirements.txt
├── README.md
```

### requirements.txt

```
gradio>=4.0
```

### README.md

```markdown
---
title: My App
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.0.0
pinned: false
license: mit
---
```

### app.py

```python
import gradio as gr

def process(input_data):
    return f"Processed: {input_data}"

demo = gr.Interface(fn=process, inputs="text", outputs="text")
demo.launch(server_name="0.0.0.0", server_port=7860)
```

### Push

```bash
huggingface-cli login --token $HF_TOKEN
cd my-space && git init && git add . && git commit -m "init"
git remote add origin https://huggingface.co/spaces/USER/SPACE
git push -u origin main
```

## Common Components

| Component | Use For |
|-----------|---------|
| `gr.Textbox()` | Text input |
| `gr.Number()` | Numeric input |
| `gr.Slider()` | Range selection |
| `gr.Dropdown()` | Selection |
| `gr.Radio()` | Single choice |
| `gr.Checkbox()` | Boolean |
| `gr.File()` | File upload |
| `gr.Image()` | Image upload |
| `gr.Audio()` | Audio upload |
| `gr.Dataframe()` | Table editing |
| `gr.Plot()` | Matplotlib |
| `gr.Label()` | Classification |
| `gr.Chatbot()` | Chat display |
| `gr.Gallery()` | Image gallery |
| `gr.Markdown()` | Rich text |

## Events

```python
btn.click(fn=handler, inputs=[inp], outputs=[out])
slider.change(fn=update, inputs=slider, outputs=output)
textbox.submit(fn=process, inputs=textbox, outputs=output)
# Chain
btn.click(step1, inputs=a, outputs=b).then(step2, inputs=b, outputs=c)
```

## Streaming Chat

```python
def stream_chat(message, history):
    messages = []
    for user_msg, bot_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})
    messages.append({"role": "user", "content": message})
    
    stream = client.chat.completions.create(
        model="gpt-4o-mini", messages=messages, stream=True,
    )
    response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            response += chunk.choices[0].delta.content
            yield response

demo = gr.ChatInterface(fn=stream_chat)
```

## Theming

```python
demo = gr.Blocks(theme=gr.themes.Soft())
demo = gr.Blocks(css=""".gradio-container { max-width: 1200px; }""")
```

## Error Handling

```python
def safe_process(data):
    try:
        return do_work(data)
    except Exception as e:
        raise gr.Error(f"Failed: {e}")
```

## Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 7860
CMD ["python", "app.py"]
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Port in use | Change `server_port` or kill process on 7860 |
| Share link broken | Use HF Spaces for permanent URLs |
| HF Spaces build fails | Check `requirements.txt` and build logs |
| CORS errors | Add `cors_allowed_origins` to launch() |
| Slow first load | Model loading — add loading indicator |

## Permanent Tunnel Alternatives

```bash
cloudflared tunnel --url http://localhost:7860   # free, permanent
ngrok http 7860                                    # free tier
```
