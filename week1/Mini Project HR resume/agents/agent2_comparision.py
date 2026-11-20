import os
import json
from datetime import date, datetime
from dotenv import load_dotenv
from groq import Groq
from pydantic import ValidationError
from schemas.schema import Judgement_JD_resume, Matching_JD_resume

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

# weight of each category in the final score, categories the JD does not have are left out and the rest are re-scaled
weights = {'required_skills':40, 'experience':25, 'preferred_skills':10, 'education':10, 'responsibilities':15}
status_points = {'met':1, 'partial':0.5, 'not_met':0}

def month_index(value):
    if value.lower() == 'present':
        today = date.today()
        return today.year * 12 + today.month
    parsed = datetime.strptime(value, '%Y-%m')
    return parsed.year * 12 + parsed.month

def calculate_experience(work_history):
    '''
    Total years of experience from the dates in the work history, overlapping jobs are counted only once.
    '''
    periods = []
    for job in work_history:
        # jobs with a missing or badly formatted date are skipped
        if job.start_date is None or job.end_date is None:
            continue
        try:
            periods.append((month_index(job.start_date), month_index(job.end_date)))
        except ValueError:
            continue

    total_months = 0
    covered_until = None
    for start, end in sorted(periods):
        if covered_until is not None and start < covered_until:
            start = covered_until
        if end > start:
            total_months += end - start
            covered_until = end

    return round(total_months / 12, 1)

def evaluvate_candidates(JD_json, resume_json):
    '''
    Takes the parsed Job Description and the parsed Resume from Agent 1 and returns the match score.
    The LLM judges every requirement, the score itself is calculated here so it is repeatable.
    '''
    requirements = {
        'required_skills': JD_json.required_skills,
        'preferred_skills': JD_json.preferred_skills,
        'education': JD_json.education_requirements,
        'responsibilities': JD_json.responsibilities,
    }

    schema_judgement = json.dumps(Judgement_JD_resume.model_json_schema(), indent=2)
    sys_message = f"""
    You are a helper agent for an HR, you compare the requirements of a Job Description with the resume of a candidate.
    The output must be a single json object in the schema defined {schema_judgement}

    Check every requirement of required_skills, preferred_skills, education and responsibilities, copy the requirement text exactly.
    status is met when the resume clearly shows it, partial when the resume shows something related or weaker, not_met when there is nothing in the resume.
    A skill can be met by an equivalent or more specific one, for example PostgreSQL meets SQL.
    evidence is a short phrase taken from the resume, use null when the status is not_met.
    details are 3 to 6 short sentences about the main strengths and gaps of the candidate.
    Use only the resume, don't assume anything that is not written in it.
    """

    sys_message = {'role':'system', 'content':sys_message}

    # personal information is left out, the comparison does not need it
    prompt = f"""
    Compare the requirements with the resume.

    <requirements>
    {json.dumps(requirements, indent=2)}
    </requirements>

    <resume>
    {resume_json.model_dump_json(exclude={'personal_info'}, indent=2)}
    </resume>
    """

    message = {'role':'user','content':prompt}

    messages = [sys_message,message]

    for attempt in range(max_retries):
        # get response from the LLM ( gives raw json )
        response = client.chat.completions.create(model=model ,messages = messages, reasoning_effort = reasoning_effort , response_format = response_format, temperature = 0, max_completion_tokens = max_tokens)

        if response.choices[0].finish_reason == 'length':
            raise ValueError("The response was cut off, increase max_tokens")

        raw_judgement = response.choices[0].message.content or ""

        try:
            judgement = Judgement_JD_resume.model_validate_json(raw_judgement)
        except ValidationError as error:
            feedback = f"The json did not match the schema, return the corrected json only. Errors: {error}"
        else:
            # lookup of every check by its requirement text
            checks = {name: {check.requirement.strip().lower(): check for check in getattr(judgement, name)} for name in requirements}
            not_checked = [f"{name}: {requirement}" for name, items in requirements.items() for requirement in items if requirement.strip().lower() not in checks[name]]
            if not not_checked:
                break
            feedback = f"These requirements were not checked, include all of them with the exact text: {not_checked}"

        messages = messages + [{'role':'assistant','content':raw_judgement}, {'role':'user','content':feedback}]
    else:
        raise ValueError("Could not get a valid comparison from the model")

    category_scores = {}
    for name, items in requirements.items():
        if items:
            points = sum(status_points[checks[name][requirement.strip().lower()].status] for requirement in items)
            category_scores[name] = points / len(items)

    candidate_years = calculate_experience(resume_json.work_history)
    if JD_json.minimum_year_of_experience:
        category_scores['experience'] = min(candidate_years / JD_json.minimum_year_of_experience, 1)

    total_weight = sum(weights[name] for name in category_scores)
    if total_weight == 0:
        raise ValueError("The Job Description has no requirements to compare against")

    score = round(sum(weights[name] * value for name, value in category_scores.items()) / total_weight * 100)

    matched_skills = []
    missing_skills = []
    for name in ('required_skills', 'preferred_skills'):
        for skill in requirements[name]:
            status = checks[name][skill.strip().lower()].status
            if status == 'met':
                matched_skills.append(skill)
            elif status == 'not_met':
                missing_skills.append(skill)

    if score >= 75:
        recommendation = 'Strong fit'
    elif score >= 50:
        recommendation = 'Moderate fit'
    else:
        recommendation = 'Weak fit'

    return Matching_JD_resume(
        score = score,
        recommendation = recommendation,
        category_scores = {name: round(value * 100) for name, value in category_scores.items()},
        matched_skills = matched_skills,
        missing_skills = missing_skills,
        candidate_years_of_experience = candidate_years,
        details = judgement.details,
    )
