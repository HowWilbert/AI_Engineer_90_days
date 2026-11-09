# Architecture: Python Application → Groq SDK → Groq API → LLM

```mermaid
flowchart LR
    subgraph LOCAL["Local Machine"]
        direction TB
        U(["User<br/>(Terminal)"])
        ENV[(".env<br/>GROQ_API_KEY")]

        subgraph APP["Python Application: continious_gpt.py"]
            direction TB
            CFG["Config<br/>model = openai/gpt-oss-120b<br/>reasoning_effort = low"]
            LOOP["Chat Loop<br/>while True: input → call → print"]
            HIST[("messages list<br/>(conversation history)")]
        end

        subgraph SDK["Groq Python SDK (groq package)"]
            direction TB
            CL["Groq(api_key)<br/>client"]
            CC["client.chat.completions.create()"]
            HTTP["HTTP layer<br/>builds JSON request,<br/>adds Authorization header,<br/>parses JSON response"]
        end
    end

    subgraph CLOUD["Groq Cloud"]
        direction TB
        API["Groq API<br/>POST https://api.groq.com/openai/v1/chat/completions<br/>(OpenAI-compatible)"]
        LLM{{"LLM<br/>openai/gpt-oss-120b<br/>(served on Groq LPU hardware)"}}
    end

    U <-- "prompt / reply" --> LOOP
    ENV -- "load_dotenv() + os.getenv()" --> CL
    CFG --> CC
    LOOP <--> HIST
    LOOP -- "messages" --> CC
    CL --> CC --> HTTP
    HTTP -- "HTTPS request<br/>Bearer API key + JSON body" --> API
    API -- "inference" --> LLM
    LLM -- "generated tokens" --> API
    API -- "HTTPS response<br/>JSON: id, choices, usage" --> HTTP
    HTTP -- "ChatCompletion object" --> LOOP
```

| Layer | Responsibility |
|---|---|
| **Python Application** | Reads user input, keeps the `messages` history, prints replies |
| **Groq SDK** | Wraps the REST API: auth, request building, response parsing into Python objects |
| **Groq API** | Authenticates the key, routes the request to the model, returns JSON |
| **LLM** | Generates the assistant reply using the *entire* message history as context |
