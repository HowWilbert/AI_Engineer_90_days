import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

my_api_key = os.getenv('GROQ_API_KEY')

if not my_api_key:
    raise ValueError("Api Key not found!")

# Register as a client
client = Groq(api_key = my_api_key)

# Model
model = 'openai/gpt-oss-120b'

# Define ROLE and PROMPT
role = 'user'
prompt = 'Who is Virat Kohli'

# Creating a dictionary of a message

message = {"role" : role,
           "content": prompt}

# Groq responds to only list of messages not dictionary

messages = [message]

# Response

response = client.chat.completions.create(model = model,
                                           messages= messages)

print(response.choices[0].message.content)