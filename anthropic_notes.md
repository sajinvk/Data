# 🧠 Anthropic – Building Components (Certification Notes)

---

## 🔍 Alignment & Interpretability

### 📌 What is Interpretability?
- Understanding how models make decisions  
- Similar to “brain scans” for AI systems  
- Reverse engineering internal reasoning  

🔗 https://www.anthropic.com/research/team/interpretability

---

## 🤖 Choosing Claude Models

- **Opus** → Best for complex reasoning
- **Sonnet** → Balanced performance
- **Haiku** → Fast & cost-efficient

### ✅ Key Features
- Large context (~1M tokens)
- Multimodal (text + image)
- API / Bedrock / Vertex AI support

---

## ⚙️ Working with API

```python
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="MODEL_NAME",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "Your prompt"}
    ],
    system="You are a helpful assistant",
    temperature=0.0
)

print(response.content[0].text)
```

---

## 💬 Chatbot Example

```python
messages = []

while True:
    user_input = input("You: ")

    if user_input.lower() == 'quit':
        break

    messages.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model="MODEL_NAME",
        max_tokens=200,
        messages=messages
    )

    reply = response.content[0].text
    print(reply)

    messages.append({"role": "assistant", "content": reply})
```

---

## 🎯 Prefilling Response

```python
response = client.messages.create(
    model="MODEL_NAME",
    max_tokens=500,
    messages=[
        {"role": "user", "content": "Tell a joke"},
        {"role": "assistant", "content": "Knock knock"}
    ]
)
```

---

## 🖼️ Multimodal

```python
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this image"}
        ]
    }
]
```

---

## ⚡ Streaming

```python
with client.messages.stream(
    model="MODEL_NAME",
    messages=[{"role": "user", "content": "Write a poem"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="")
```

---

## 🧠 Prompt Engineering

### Role

```python
role = "You are a sentiment analysis assistant"
```

### Structured Prompt

```python
prompt = """
<review>
{{TEXT}}
</review>

<instructions>
- Extract sentiment
- Identify complaints
</instructions>

<output>
Return JSON
</output>
"""
```

---

## 🚀 Prompt Caching

- Cache reusable prompt sections
- Write = expensive
- Read = ~90% cheaper

---

## 🔁 Multi-turn Caching

- Cache conversation history
- Only process new messages

---

## 🛠️ Tools

```python
tool = {
    "name": "get_user",
    "description": "Fetch user",
    "input_schema": {
        "type": "object",
        "properties": {
            "key": {"type": "string"},
            "value": {"type": "string"}
        },
        "required": ["key", "value"],
        "additionalProperties": False
    }
}
```

---

## ✅ Key Takeaways

- Use structured prompts (XML/JSON)
- Separate role, input, instructions, output
- Use caching to optimize cost
- Choose model based on complexity

---
