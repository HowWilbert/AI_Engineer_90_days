# Goal - take input from user continiously unitil they press Ctrl + C to quit the code,  give response through groq ka llm
# workflow - 1. API KEY, CLient, Model, Message ( Role, Content ) [ ye lete rhena hai ] -> pass it into a list , Response -> print 


'''
Summary of this foundation code: 
1. Created a simple ChatGPT input output model using Groq API
2. MOAT - Remembers the Context ( basic LLM calling and stores the output and sends it back again to the LLM )
3. WORKFLOW 
    a. API KEY ( groq )
    b. Regesterd as a client
    c. Provided with the model and the reasoning effort
    d. provided the System prompt
    e. initialized the messages list outside the while loop [previous error was i initialized the list inside the while loop]
    f. the Continous Chat feature until we press Ctrl + C to kill the code itself 
         i. take the user input prompt 
        ii. store that input in the list before giving the output
       iii. get the response from the API by sending the list of messages ( This is the CONTEXT )
        iv. store that response in the same list in a dictionary ( role , content )
    
4. Few Things which can be remebered: 
    a. the response is an output in the form of a JSON 
    b. contains choices, usage, and id to distinguish
    c. Choices - contains index, message
    d. Message contains - role and content
    
so to print a response we write response.choices[0].message.content
choice[0] is the LLM first choice.


5. to Get a response we write 

response = client.chat.completions.create(model=,message=,reasoning_effort=,etc etc)

client - Connection interface to groq's Api
chat -  client gets access to the chat related API functionality
completions - chat completion resourse ( wo chat ko chalu karne ke liye kya kya chaiye )
create - method that creates a completion ( this performs the API request , and sends a completion request )

Next steps - 
'''
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# load environment variables 
load_dotenv()

# API KEY 
my_api_key = os.getenv("GROQ_API_KEY")

# Register as a client
client = Groq(api_key = my_api_key)

# Model Configurations
model = 'openai/gpt-oss-120b'
reasoning_effort = 'low' 

# Never Ending Prompt and response until you press Ctrl + C to kill the code

# since this is my chat bot i want it to be a general assistant bot which helps in normal conversations
# I provide application specific Instructions

system_role = "system"
system_prompt = "You are an excellent general knowledge persona, when asked general knowledge questions you give output in 2–3 concise sentences"
# this is my context window for my LLM
messages = [{"role":system_role , "content": system_prompt}] 
while True:
    print("#"*50,"Enter your Message","#"*50,"\nTo kill code Press Ctrl + C")
    
    content = input("Prompt: ")
    
    messages.append({"role":"user","content":content})
    response = client.chat.completions.create(model=model , messages = messages,reasoning_effort= reasoning_effort)
    
    # Context Window Live = Append the output of the LLM into the same list so every new output knows the context of the previous conversation 
    messages.append({"role":response.choices[0].message.role,"content":response.choices[0].message.content})
    print(response.choices[0].message.content)

