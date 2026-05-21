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
"
from anthropic import Anthropic

client = Anthropic()  # uses API key from environment

response = client.messages.create(
    model=""MODEL_NAME"",              # Required
    max_tokens=INTEGER,              # Required
    messages=[                       # Required
        {""role"": ""user"", ""content"": ""Your prompt""},
        {""role"": ""assistant"", ""content"": ""Previous response (optional)""}
    ],
    system=""SYSTEM_PROMPT"",          # Optional (instructions for behavior)
    temperature=0.0,                 # Optional (0–1 randomness)
    stop_sequences=[""STOP_TEXT""],    # Optional
)
"
```

---

## 💬 Chatbot Example

```python
print("Simple Chatbot (type 'quit' to exit)")
# Store conversation history
messages = []
while True:
    # Get user input
    user_input = input("You: ")
    # Check for quit command
    if user_input.lower() == 'quit':
        print("Goodbye!")
        break
    # Add user message to history
    messages.append({"role": "user", "content": user_input})
    try:
        # Get response from Claude
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=200,
            messages=messages
        )
        # Extract and print Claude's response
        asst_message = response.content[0].text
        print("Assistant:", asst_message)
        
        # Add assistant response to history
        messages.append({"role": "assistant", "content": asst_message})
        
    except Exception as e:
        print(f"An error occurred: {e}")
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
        "content": [{
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": base64_string
            },
        },
        {
            "type": "text",
            "text": """How many to-go containers of each type 
            are in this image?"""
        }]
    }
]
```

---

## ⚡ Streaming

```python
with client.messages.stream(
    max_tokens=1024,
    messages=[{"role": "user", "content": "write a poem"}],
    model=MODEL_NAME,
) as stream:
  for text in stream.text_stream:
      print(text, end="", flush=True)
```

---

## 🧠 Prompt Engineering

### Role

```python
setting_the_role = """
You are an AI assistant specialized in analyzing customer reviews. 
Your task is to determine the overall sentiment of a given review 
and extract any specific complaints mentioned. 
Please follow these instructions carefully:
"""
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
{
  "sentiment_score": "Positive|Negative|Neutral",
  "sentiment_analysis": "Explanation of sentiment classification",
  "complaints": [
    "Complaint 1",
    "Complaint 2",
    "..."
  ]
}
</output>
"""
```

---

## 🚀 Prompt Caching

- Cache reusable prompt sections

cache a prefix of your prompt so that repeated requests reuse it instead of reprocessing it from scratch.

You mark part of your prompt as cacheable.
First request (cache write): cache_creation_input_tokens
Subsequent requests (cache read): cache_read_input_tokens

**ephemeral_5m_input_tokens**: 108428
→ 108K tokens reused from 5‑minute cache (cheap + fast)


**ephemeral_1h_input_tokens**: 0
→ No usage of 1‑hour cacheephemeral_5m_input_tokens: 108428


Prompt Caching Pricing

Cache write tokens are 25% more expensive than base input tokens
Cache read tokens are 90% cheaper than base input tokens
Regular input and output tokens are priced at standard rates 
- Write = expensive
- Read = ~90% cheaper

---


```python
def make_cached_api_call():
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "<book>" + book_content + "</book>",
                    "cache_control": {"type": "ephemeral"}
                },
                {
                    "type": "text",
                    "text": "What happens in chapter 5?"
                }
            ]
        }
    ]

    start_time = time.time()
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=500,
        messages=messages,
    )
    end_time = time.time()

    return response, end_time - start_time
```

**Output will look like:**
usage=Usage(cache_creation_input_tokens=108428, cache_read_input_tokens=0, input_tokens=10, output_tokens=351, cache_creation={'ephemeral_5m_input_tokens': 108428, 'ephemeral_1h_input_tokens': 0}, service_tier='standard', inference_geo='not_available'), stop_details=None)

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

## Stop reasons 
