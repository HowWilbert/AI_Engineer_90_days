# Data Flow Diagram

## 1. How data moves through the application

```mermaid
flowchart LR
    ENV[(".env file")] -- "GROQ_API_KEY (string)" --> CLIENT["Groq client"]

    USER(["User"]) -- "raw text<br/>(input())" --> P1["Wrap as dict<br/>{role: 'user', content: text}"]
    P1 -- "user message" --> HIST[("messages list<br/>HISTORY")]

    SYS["system_prompt"] -- "{role: 'system', ...}<br/>(added once at startup)" --> HIST

    HIST -- "FULL list of messages<br/>+ model + reasoning_effort" --> CLIENT
    CLIENT -- "JSON request over HTTPS" --> GROQ{{"Groq API + LLM"}}
    GROQ -- "JSON response<br/>{id, choices, usage}" --> CLIENT
    CLIENT -- "ChatCompletion object" --> P2["Extract<br/>choices[0].message<br/>(.role, .content)"]

    P2 -- "{role: 'assistant', content: reply}<br/>UPDATED HISTORY" --> HIST
    P2 -- "reply text<br/>print()" --> USER

    classDef store fill:#e8f5e9,stroke:#43a047,color:#000
    classDef ext fill:#fff3e0,stroke:#fb8c00,color:#000
    class HIST,ENV store
    class USER,GROQ ext
```

`messages` is read on every API call and written twice per turn: once with the user's message before the call, and once with the assistant's reply after it.

## 2. How the history grows turn by turn

```mermaid
flowchart TB
    subgraph T0["Startup: len = 1"]
        direction LR
        a0["system"]
    end

    subgraph T1["After turn 1: len = 3"]
        direction LR
        b0["system"] --> b1["user #1"] --> b2["assistant #1"]
    end

    subgraph T2["After turn 2: len = 5"]
        direction LR
        c0["system"] --> c1["user #1"] --> c2["assistant #1"] --> c3["user #2"] --> c4["assistant #2"]
    end

    subgraph TN["After turn N: len = 1 + 2N"]
        direction LR
        d0["system"] --> d1["... all previous turns ..."] --> d2["user #N"] --> d3["assistant #N"]
    end

    T0 -- "user types, append user,<br/>call API (sends 2 msgs),<br/>append assistant" --> T1
    T1 -- "call API (sends 4 msgs)" --> T2
    T2 -- "..." --> TN
```

**Notes on the updated history**
- Each API call sends the whole list. Turn N sends `2N` messages: the system message, all earlier pairs, and the new user message.
- The history lives only in RAM. Pressing Ctrl + C wipes it, and nothing is saved to disk.
- The history grows without limit. In a long chat it will eventually exceed the model's context window and cost more tokens on every turn, so trimming or summarizing it is a natural next step.
