# Sequence Diagram: User → Python → Groq → Python → User

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Py as Python App<br/>(continious_gpt.py)
    participant H as messages list<br/>(history)
    participant SDK as Groq SDK
    participant API as Groq API
    participant LLM as LLM<br/>(gpt-oss-120b)

    Note over Py: Startup
    Py->>Py: load_dotenv() + os.getenv("GROQ_API_KEY")
    Py->>SDK: Groq(api_key=...)
    Py->>H: init [ {system, system_prompt} ]

    loop Every turn, until Ctrl + C
        Py-->>User: print banner "Enter your Message"
        User->>Py: types prompt (input)
        Py->>H: append {role: "user", content}
        Py->>SDK: chat.completions.create(model, messages=H, reasoning_effort="low")
        SDK->>API: HTTPS POST /openai/v1/chat/completions<br/>(Bearer key + full history as JSON)
        API->>LLM: run inference on full history
        LLM-->>API: generated reply
        API-->>SDK: JSON {id, choices[0].message, usage}
        SDK-->>Py: ChatCompletion object
        Py->>H: append {role: "assistant", content: reply}
        Py-->>User: print(choices[0].message.content)
    end

    User->>Py: Ctrl + C
    Py-->>User: KeyboardInterrupt → program exits
```

**Key point:** in step 5, the *whole* history goes to Groq every turn, not just the newest prompt. That's how the model "remembers" earlier turns. The API itself keeps no state between calls.
