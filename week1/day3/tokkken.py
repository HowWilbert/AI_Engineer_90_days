'''
Tokens. 

Token ? - Smaller units that are converted from text so a LLM can understand.
Tokens can be 
    a. An entire word 
    b. A part of a word
    c. A punctuation mark
    d. Sometimes even a space combined with a word.

2 types of Tokens 
    a. Prompt   - Input Tokens (Prompt Tokens)
    b. Response - Output Tokens(Output Tokens/Completion Tokens)
    c. Reasoning- Reasoning Tokens
'''


import os
from groq import Groq
from pathlib import Path
from dotenv import load_dotenv

# load environment variables 
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

ansh_client = Groq(api_key=api_key)

# model configurations
model = 'openai/gpt-oss-120b'
reasoning_effort = 'low'
# system Prompt
sys_role = 'system'
sys_prompt = 'You are a Token(in terms of usage) calculating agent, your role is only to give the output in this format, Input Tokens - <number of tokens consumed> Output tokens - <number of tokens consumed> Total Tokens'

sys_message = {'role':sys_role,'content':sys_prompt}

# message 
role = 'user'
content = 'I want to understand how many tokens this message take'

message = {'role':role , 'content':content}

# list of messages 

messages = [sys_message,message]

# get response

response = ansh_client.chat.completions.create(model=model,messages = messages,reasoning_effort=reasoning_effort)

print(response.choices[0].message.content)
print("******************* Response About Tokens ******************\n")
print()
print("Completion Tokens: ",response.usage.completion_tokens)
print("Prompt Tokens: ",response.usage.prompt_tokens)
print("Total Tokens: ",response.usage.total_tokens)
print("Reasoning Tokens: ",response.usage.completion_tokens_details.reasoning_tokens)
