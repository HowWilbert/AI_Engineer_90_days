from typing import Literal
from pydantic import BaseModel


# Defining the Struture of the Required Schema
class Schema_JD(BaseModel):
    role_title : str | None = None
    required_skills: list[str] = []
    preferred_skills : list[str] = []
    minimum_year_of_experience : int | None = None
    education_requirements : list[str] = []
    responsibilities : list[str] = []
    domain_keywords : list[str] = []

class personalinfo(BaseModel):
    name : str | None = None
    email : str | None = None
    phone : str | None = None
    github_url : str | None = None
    linkedin_url : str | None = None

class workhistory(BaseModel):
    company : str
    role : str
    start_date : str | None = None
    end_date : str | None = None
    description : list[str] = []

class Schema_Resume(BaseModel):
    personal_info : personalinfo | None = None
    skills : list[str] = []
    work_history : list[workhistory] = []
    education : list[str] = []
    projects : list[str] = []
    certifications : list[str] = []

# What the LLM returns in Agent 2, the score itself is calculated in code
class requirement_check(BaseModel):
    requirement : str
    status : Literal['met', 'partial', 'not_met']
    evidence : str | None = None

class Judgement_JD_resume(BaseModel):
    required_skills : list[requirement_check] = []
    preferred_skills : list[requirement_check] = []
    education : list[requirement_check] = []
    responsibilities : list[requirement_check] = []
    details : list[str] = []

# Final output of Agent 2
class Matching_JD_resume(BaseModel):
    score : int
    recommendation : str
    category_scores : dict[str, int]
    matched_skills : list[str]
    missing_skills : list[str]
    candidate_years_of_experience : float
    details : list[str]
