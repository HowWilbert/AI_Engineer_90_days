from groq import Groq 
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

# using the BaseModel object from the Pydantic Library to define a schema.
class Ticket(BaseModel):
    name:str 
    email:str
    phone:int
    issue:str

# model_json_schema() creates a python Dictionary that describes the expected JSON structure 
schema = Ticket.model_json_schema() 
# print(schema)

api_key = os.getenv('GROQ_API_KEY')

client = Groq(api_key=api_key)
model = 'openai/gpt-oss-120b'
response_format = {'type':'json_object'}
# building a ticket managment system

sys_role = 'system'
sys_content = f"""You will recieve customer complaints and you have to strcitly structure those complaints in the following json schema {schema}"""

sys_message = {'role':sys_role, 'content':sys_content}

# User Issues
prompt = "Hi my name is ansh, i have ordered an Iphone 19 pro Max 1TB dated : 32nd January 3012, order id - 90876HBDCX from your website dealclear.com, the phone has not been deliverd yet till today ( 7th December 3022 ) can you please check and revert back on my email - ansh@fake.com, phone = 985462154 wrong number issue "

message = {'role':'user','content':prompt}
messages = [sys_message,message]

response = client.chat.completions.create(model = model , messages = messages , temperature = 0,response_format = response_format)
response_json = response.choices[0].message.content

print(response_json)
# Reponse is of python String and when we try to do model_validate(response_json) this doesn't work as model_validate requires a pyhton Dictionary as an input. 
# so there are 2 fixes - import json library and use json.load(response_json) -> converts the Python String to Python Dictionary, when we can use model_validate -> ticket.name easily...... The 2nd Fix -> use model_validate_json(response_json) -> the BaseModel class has this feature of internally converting to the python Dictionary.  

ticket = Ticket.model_validate_json(response_json)
print(ticket)