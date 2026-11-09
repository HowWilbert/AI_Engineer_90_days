# Flowchart: Application Execution Flow

How `continious_gpt.py` runs from start to exit.

```mermaid
flowchart TD
    A([Start: python continious_gpt.py]) --> B["load_dotenv()<br/>read .env file"]
    B --> C["os.getenv('GROQ_API_KEY')"]
    C --> D["client = Groq(api_key=...)"]
    D --> E["Set config<br/>model = 'openai/gpt-oss-120b'<br/>reasoning_effort = 'low'"]
    E --> F["Define system prompt<br/>(general knowledge persona, 2-3 sentences)"]
    F --> G["messages = [ {role: system, content: system_prompt} ]<br/><i>created once, OUTSIDE the loop</i>"]

    G --> H{{"while True"}}
    H --> I["Print banner<br/>'Enter your Message' / 'Press Ctrl + C'"]
    I --> J[/"content = input('Prompt: ')"/]
    J --> K{"Ctrl + C pressed?"}

    K -- Yes --> Z(["KeyboardInterrupt<br/>Program exits"])
    K -- No --> L["messages.append(<br/>{role: user, content: content})"]
    L --> M["client.chat.completions.create(<br/>model, messages, reasoning_effort)"]
    M --> N{"API call OK?"}
    N -- "No (bad key / rate limit / network)" --> X(["Exception raised<br/>Program crashes"])
    N -- Yes --> O["messages.append(<br/>{role: assistant, content: reply})"]
    O --> P[/"print(response.choices[0].message.content)"/]
    P --> H

    classDef stop fill:#fde2e2,stroke:#c0392b,color:#000
    classDef io fill:#e3f2fd,stroke:#1e88e5,color:#000
    classDef store fill:#e8f5e9,stroke:#43a047,color:#000
    class Z,X stop
    class J,P io
    class G,L,O store
```

**Legend:** green = writes to `messages` (the conversation history), blue = terminal input/output, red = the program ends.
