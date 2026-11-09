'''
Understanding System Role and Temperature 

1. System Role - Simply tell the LLM how they need to behave, or give them a POST in which they need to act
2. Temperature - Tells how creative the LLM can be. 

How do LLM responds? 
- Firstly we need to understand this that a LLM doesn't know if the answer is right or not, the LLM tries to answer the safest and closest answer to a particular question
- In short an LLM tries to Predict your Questions answer. 

This is called being Creative ( Temperature which is set to 0 by default )

so by increasing the temperature the LLM tries to be more creative and takes Risky Predictions which may be completly out of context of the Question. 

So Why Do we need temperature ?
1. Multiple Usecases, a Newstelling Bot requires the Story to be creative. 
2. A company naming bot needs to be Creative or play safe

Thus Temepratures allows us to change the personality of a LLM. 
'''



import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# load Environment variables
load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

# register as a client

client = Groq(api_key= my_api_key)

# model selection and effort

model = 'openai/gpt-oss-120b'

# system Prompt
system_role = 'system'
system_prompt = 'You suggest names for a company, who happens to give 5 names at a time and just 5 names as output'

sys_message = {"role":system_role,"content":system_prompt}

# user input 
content = 'Provide me a unique name for my education tech company'

message = {"role":"user","content":content}

# list of messages
messages = [sys_message,message]

# get the response in the Python Object from Groq SDK
response = client.chat.completions.create(model=model,messages = messages  , temperature = 1.99, reasoning_effort = 'high')

#print the output 
print(response.choices[0].message.content)