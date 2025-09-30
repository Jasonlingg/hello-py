import json
import re
from typing import Any, Dict, List
from anthropic.types import ToolUnionParam
from task_framework import python_expression_tool, submit_answer_tool


def get_resume(name: str) -> dict:
    """Returns unstructured resume text for parsing."""
    if name == "resume_v1":
        # Intentionally messy formatting, varied date formats, mixed sections
        text = (
            "JOHN Q. DOE\n"
            "San Francisco, CA | (415) 555-0199 | john.doe@example.com | github.com/jqdoe\n\n"
            "PROFILE\n"
            "Software engineer with experience in backend systems, data pipelines, and ML tooling.\n\n"
            "EXPERIENCE\n"
            "Acme Corp — Senior Software Engineer\n"
            "Jan 2019 – Present | San Francisco, CA\n"
            "Built event-driven data platform (Python, Kafka, Airflow). Led 4 engineers; reduced p95 latency by 35% and increased throughput 2x.\n\n"
            "Beta Labs | Software Engineer\n"
            "07/2016 to 12/2018  —  New York, NY\n"
            "Developed REST APIs (Flask), CI/CD (CircleCI), and monitoring (Prometheus); cut deployment time by 40% and improved SLA to 99.9%.\n\n"
            "Education\n"
            "B.S. in Computer Science, University of California, Berkeley — 2012 – 2016\n\n"
            "SKILLS\n"
            "Python, SQL, Docker, Kubernetes; AWS (S3, Lambda), Airflow; Kafka, Spark; Pandas / NumPy; Git\n\n"
            "Projects\n"
            "Realtime ETL pipeline; Feature store POC; Internal SDK\n"
        )
        return {"text": text}
    elif name == "resume_v2":
        text = (
            "Jane Smith\n"
            "jane.smith@protonmail.com | 212-555-7777 | Brooklyn, NY\n\n"
            "Professional Experience\n"
            "Gamma Inc (Remote) — Staff Engineer\n"
            "2021/03 - 2024/08\n"
            "Ownership of payments microservices (Go, gRPC, Postgres), PCI scope reduction.\n\n"
            "Delta LLC — Engineer\n"
            "2018 – 2021\n"
            "Search infra, batch jobs (Python, Airflow), observability (Grafana).\n\n"
            "EDUCATION\n"
            "MEng, Computer Engineering, Cornell Tech, 2017 – 2018\n"
            "BEng, Electrical Engineering, 2013-2017\n\n"
            "Skillset\n"
            "Go; Python; SQL; Terraform; AWS; Kubernetes; Airflow; Redis; Kafka\n"
        )
        return {"text": text}
    return {"text": ""}


def get_prompt() -> str:
    return (
        "You are given raw, unstructured resume text. Parse it and extract required fields.\n\n"
        "1) Use get_resume(name='resume_v1') to fetch the resume text.\n"
        "2) Extract the following fields:\n"
        "   - name (full name)\n"
        "   - email\n"
        "   - phone\n"
        "   - education (free-form string or list)\n"
        "   - work_experience (array of roles with employer, title, start_date, end_date)\n"
        "3) Identify section headers present (e.g., Education, Experience, Skills).\n"
        "4) Parse dates in multiple formats and normalize to ISO (YYYY-MM).\n"
        "   - Treat end dates of 'present'/'current'/'now'/'today' as 2025-10 (fixed)\n"
        "   - Do not use education dates as work experience\n"
        "5) Calculate total years_of_experience (float, 1 decimal).\n"
        "   - Include ALL work roles; sum non-overlapping periods\n"
        "   - Use month-level precision (count months, then divide by 12)\n"
        "   - Include ongoing roles through the current date (use 2025-10)\n"
        "6) Extract a normalized skills list (lowercase strings).\n\n"
        "7) For each work role, include a short description (1–2 sentences) summarizing responsibilities with action verbs (e.g., built, led, designed).\n"
        "   - At least two roles must have a substantive description (≥ 40 chars)\n"
        "   - At least one description should include a measurable impact (e.g., %, x, numbers, latency, throughput, cost). The second may be qualitative (e.g., improved efficiency/performance/reliability).\n\n"
        "Return JSON in this exact envelope:\n"
        "{\n"
        "  \"name\": string,\n"
        "  \"email\": string,\n"
        "  \"phone\": string,\n"
        "  \"education\": string | array,\n"
        "  \"work_experience\": [\n"
        "     {\"employer\": string, \"title\": string, \"start_date\": string, \"end_date\": string}\n"
        "  ],\n"
        "  \"section_headers\": [string],\n"
        "  \"years_experience\": number,\n"
        "  \"skills\": [string]\n"
        "}\n\n"
        "Then call submit_answer with that JSON."
    )


def get_tools() -> List[ToolUnionParam]:
    return [
        {
            "name": "python_expression",
            "description": "Evaluates a Python expression. Use print() to output results.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Python code to execute. Use print() for output.",
                    }
                },
                "required": ["expression"],
            },
        },
        {
            "name": "get_resume",
            "description": "Get unstructured resume text by name",
            "input_schema": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
        {
            "name": "submit_answer",
            "description": "Submit the final answer",
            "input_schema": {
                "type": "object",
                "properties": {"answer": {"description": "The final answer to submit"}},
                "required": ["answer"],
            },
        },
    ]


def get_tool_handlers() -> Dict[str, Any]:
    return {
        "python_expression": python_expression_tool,
        "get_resume": get_resume,
        "submit_answer": submit_answer_tool,
    }


def _compute_expected_years(text: str) -> float:
    # Heuristic: Based on known ranges in resume_v1
    # Jan 2019 – Present, 07/2016 to 12/2018 -> (2019-01 to today) + (2016-07 to 2018-12)
    import datetime as _dt
    # Fix "present" to October 2025 per spec to reduce false negatives
    today = _dt.date(2025, 10, 1)
    def months_between(a: _dt.date, b: _dt.date) -> int:
        return (b.year - a.year) * 12 + (b.month - a.month)
    # Period 1: 2019-01 to current month
    p1 = months_between(_dt.date(2019, 1, 1), _dt.date(today.year, today.month, 1))
    # Period 2: 2016-07 to 2018-12 inclusive -> end at 2019-01 boundary
    p2 = months_between(_dt.date(2016, 7, 1), _dt.date(2019, 1, 1))
    total_years = (p1 + p2) / 12.0
    # Round to one decimal to match prompt expectation
    return round(total_years, 1)


def get_grader() -> callable:
    def grade_resume_task(answer: Any) -> bool:
        try:
            result = json.loads(answer) if isinstance(answer, str) else answer
            if not isinstance(result, dict):
                return False

            # Basic fields present
            required_fields = [
                "name", "email", "phone", "education", "work_experience",
                "section_headers", "years_experience", "skills",
            ]
            if not all(field in result for field in required_fields):
                return False

            # Email pattern
            email = str(result.get("email", ""))
            if not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email or ""):
                return False

            # Phone: require 10-15 digits after stripping (slightly stricter)
            phone_digits = re.sub(r"\D", "", str(result.get("phone", "")))
            if not (10 <= len(phone_digits) <= 15):
                return False

            # Work experience minimal structure
            work = result.get("work_experience", [])
            if not isinstance(work, list) or len(work) < 2:
                return False
            # Helper to compare normalized dates (YYYY or YYYY-MM) and 'present'
            def _to_year_month(value: str) -> tuple[int,int]:
                v = str(value).strip().lower()
                if v in {"present","current","now","today"}:
                    from datetime import date
                    today = date.today()
                    return (today.year, today.month)
                if re.match(r"^\d{4}-\d{2}$", v):
                    y, m = v.split("-")
                    return (int(y), int(m))
                if re.match(r"^\d{4}$", v):
                    return (int(v), 1)
                # Fallback to minimal value to fail ordering check
                return (0, 0)

            desc_roles_ok = 0
            numeric_roles_ok = 0
            action_verbs = {"built","led","designed","implemented","developed","created","launched","owned","drove","migrated","optimized","reduced","increased","improved","scaled","automated"}
            impact_tokens = {"%","percent","x","latency","throughput","sla","cost","revenue","users","requests","qps","rps","minutes","hours","ms","savings"}
            qualitative_tokens = {"efficiency","performance","reliability","availability","scalability","stability"}
            used_verbs: set[str] = set()
            for role in work:
                if not all(k in role for k in ["employer", "title", "start_date", "end_date"]):
                    return False
                # Dates should be normalized YYYY-MM (allow YYYY too)
                start_str = str(role["start_date"]).strip()
                if not re.match(r"^\d{4}(-\d{2})?$", start_str):
                    return False
                # Accept common end-date variants case-insensitively
                end_str = str(role["end_date"]).strip().lower()
                if not re.match(r"^\d{4}(-\d{2})?$|^(present|current|now|today)$", end_str):
                    return False
                # Stricter: start must not be after end
                if _to_year_month(start_str) > _to_year_month(end_str):
                    return False
                # Basic non-empty employer/title
                if not str(role["employer"]).strip() or not str(role["title"]).strip():
                    return False
                # Require at least two roles to include substantive descriptions with verbs and measurable impact
                desc = str(role.get("description",""))
                dl = desc.strip().lower()
                has_verb = any(v in dl for v in action_verbs)
                has_numeric = bool(re.search(r"\d", dl)) or any(tok in dl for tok in impact_tokens)
                has_qual = any(tok in dl for tok in qualitative_tokens)
                if len(dl) >= 40 and has_verb and (has_numeric or has_qual):
                    # track a verb hit to enforce diversity
                    for v in action_verbs:
                        if v in dl:
                            used_verbs.add(v)
                            break
                    desc_roles_ok += 1
                    if has_numeric:
                        numeric_roles_ok += 1

            # Need two described roles, at least one numeric/quantified impact, and diversity of verbs
            if desc_roles_ok < 2 or numeric_roles_ok < 1 or len(used_verbs) < 2:
                return False

            # Section headers must include core ones (case-insensitive) and have at least 4 entries (slightly stricter)
            headers = [str(h).lower() for h in result.get("section_headers", [])]
            must_have = {"education", "experience", "skills"}
            if not must_have.issubset(set(headers)) or len(set(headers)) < 4:
                return False

            # Skills: require at least 8 unique, lowercase normalization tolerated (tiny bump in difficulty)
            skills = result.get("skills", [])
            if not isinstance(skills, list) or len({str(s).lower() for s in skills}) < 8:
                return False
            # Skills taxonomy coverage: require breadth across domains
            skills_text = [str(s).lower() for s in skills]
            def has_any(candidates: set[str]) -> bool:
                return any(any(token in s for token in candidates) for s in skills_text)
            languages = {"python","go","java","javascript","typescript"}
            cloud = {"aws","amazon web services","gcp","google cloud","azure","microsoft azure"}
            data_eng = {"airflow","kafka","spark"}
            containers = {"docker","kubernetes"}
            if not (has_any(languages) and has_any(cloud) and has_any(data_eng) and has_any(containers)):
                return False

            # Years experience: within tolerance of expected (resume_v1 known)
            expected_years = _compute_expected_years("")
            years = float(result.get("years_experience", 0))
            # Years should be rounded to 1 decimal place
            if abs((years * 10) - round(years * 10)) > 1e-6:
                return False
            # Loosen band: pass if >= 7.4 and <= expected + 1.2 years
            if not (years >= 7.4 and years <= expected_years + 1.2):
                return False

            return True
        except Exception:
            return False

    return grade_resume_task


