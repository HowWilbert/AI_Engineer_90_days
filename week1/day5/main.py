import argparse
import sys
from pathlib import Path
from groq import APIError
from agents.agent1_extractor import JD_parser, Resume_parser
from agents.agent2_comparision import evaluvate_candidates
from utils.read_resume import read_res

output_folder = Path('outputs')

def print_report(name, result):
    print(f"\n{name}")
    print(f"  Match: {result.score}%  ({result.recommendation})")
    print(f"  Experience: {result.candidate_years_of_experience} years")
    for category, value in result.category_scores.items():
        print(f"  {category}: {value}%")
    print(f"  Matched skills: {', '.join(result.matched_skills) or '-'}")
    print(f"  Missing skills: {', '.join(result.missing_skills) or '-'}")
    for line in result.details:
        print(f"  - {line}")

def main():
    parser = argparse.ArgumentParser(description='Match resumes against a Job Description')
    parser.add_argument('--jd', required=True, help='path to the Job Description (.pdf, .docx or .txt)')
    parser.add_argument('--resume', required=True, help='path to a resume (.pdf or .docx) or a folder of resumes')
    args = parser.parse_args()

    # the model can return characters the Windows console encoding cannot print
    sys.stdout.reconfigure(encoding='utf-8')

    for path in (args.jd, args.resume):
        if not Path(path).exists():
            parser.error(f"file not found: {path}")

    output_folder.mkdir(exist_ok=True)

    # Agent 1 on the Job Description, parsed once and used for every resume
    JD_json = JD_parser(read_res(args.jd))
    (output_folder / 'jd.json').write_text(JD_json.model_dump_json(indent=2), encoding='utf-8')

    resume_path = Path(args.resume)
    if resume_path.is_dir():
        resume_files = sorted(file for file in resume_path.iterdir() if file.suffix.lower() in ('.pdf', '.docx'))
    else:
        resume_files = [resume_path]

    results = []
    for resume_file in resume_files:
        try:
            # Agent 1 on the Resume, then Agent 2 compares the two
            resume_json = Resume_parser(read_res(resume_file))
            (output_folder / f"{resume_file.stem}_resume.json").write_text(resume_json.model_dump_json(indent=2), encoding='utf-8')
            result = evaluvate_candidates(JD_json, resume_json)
            (output_folder / f"{resume_file.stem}_match.json").write_text(result.model_dump_json(indent=2), encoding='utf-8')
        except (ValueError, APIError) as error:
            print(f"\nSkipping {resume_file.name}: {error}")
            continue
        results.append((resume_file.name, result))

    results.sort(key=lambda item: item[1].score, reverse=True)
    for name, result in results:
        print_report(name, result)

if __name__ == "__main__":
    main()
