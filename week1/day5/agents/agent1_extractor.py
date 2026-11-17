import os
import json
from dotenv import load_dotenv
from groq import Groq
from pydantic import ValidationError
from schemas.schema import Schema_JD, Schema_Resume

load_dotenv()

# register as a client
api_key = os.getenv('GROQ_API_KEY')

client = Groq(api_key=api_key)

# model configurations
model = "openai/gpt-oss-120b"
reasoning_effort = "low"
response_format = {'type':'json_object'}
max_retries = 3
max_tokens = 8000

def JD_parser(JD):
    '''
    reads the Text from the Job Description and get the output in the form of a Json format
    '''

    schema_JD = json.dumps(Schema_JD.model_json_schema(), indent=2)
    sys_message = f"""
    You are a helper agent for an HR, you are to extract explicit information from the Job Description provided in the json format.
    The Job Description will be provided and the output must be a single json object in the schema defined {schema_JD}.

    Use an empty list for list fields and null for single values that are not mentioned.
    minimum_year_of_experience is the overall minimum years of professional experience the role asks for, as a number.
    When the job description gives alternatives, for example "Python, Java or C++", keep them as one entry in the list.
    don't Invent any information on your own.
    be specific to the Job Description provided.
    """

    sys_message = {'role': 'system', 'content': sys_message}

    # User Input

    prompt = f"""
    here is the Job Description, kindly extract relevant information.
    Don't Invent anything new.
    be specific to the Job Description

    <job_description>
    {JD}
    </job_description>
    """

    message = {'role':'user','content':prompt}

    messages = [sys_message,message]

    for attempt in range(max_retries):
        # get response from the LLM ( gives raw json )
        response = client.chat.completions.create(model=model ,messages = messages, reasoning_effort = reasoning_effort , response_format = response_format, temperature = 0, max_completion_tokens = max_tokens)

        # a cut off response is never valid json, retrying will not fix it
        if response.choices[0].finish_reason == 'length':
            raise ValueError("The response was cut off, increase max_tokens")

        raw_JD = response.choices[0].message.content or ""

        try:
            JD_json = Schema_JD.model_validate_json(raw_JD)
            return JD_json
        except ValidationError as error:
            # send the error back so the model can correct its own output
            feedback = {'role':'user','content':f"The json did not match the schema, return the corrected json only. Errors: {error}"}
            messages = messages + [{'role':'assistant','content':raw_JD}, feedback]

    raise ValueError("Could not get a valid Job Description json from the model")

def Resume_parser(resume_text):
    '''
    Give the text input from the resume, and return the resume Schema.
    '''
    schema_Res = json.dumps(Schema_Resume.model_json_schema(), indent=2)

    sys_message = f"""
    You are to explicitly extract information from the text in json format in the specified schema {schema_Res}

    Use an empty list for list fields and null for single values that are not mentioned.
    Every job, internship and project must be a separate entry.
    For every job, description is the list of the work the candidate did there, taken from the resume.
    Write dates as YYYY-MM, use the word Present as end_date for a current job, use null if the date is not mentioned.
    Don't Invent any information.
    Be very Specific with the text.
    """

    sys_message = {'role':'system', 'content':sys_message}

    # user Prompt

    prompt = f"""
    Extract relevant information from the following Text.
    Don't Invent anything new.

    <resume>
    {resume_text}
    </resume>
    """

    message = {'role':'user','content':prompt}

    messages = [sys_message,message]

    for attempt in range(max_retries):
        # get response from the LLM ( gives raw json )
        response = client.chat.completions.create(model=model ,messages = messages, reasoning_effort = reasoning_effort , response_format= response_format, temperature = 0, max_completion_tokens = max_tokens)

        if response.choices[0].finish_reason == 'length':
            raise ValueError("The response was cut off, increase max_tokens")

        raw_resume = response.choices[0].message.content or ""

        try:
            # using Pydantic model itself to get json output
            resume_json = Schema_Resume.model_validate_json(raw_resume)
            return resume_json
        except ValidationError as error:
            feedback = {'role':'user','content':f"The json did not match the schema, return the corrected json only. Errors: {error}"}
            messages = messages + [{'role':'assistant','content':raw_resume}, feedback]

    raise ValueError("Could not get a valid Resume json from the model")
