"""
4) Email Triage Automation Task

Task: Automate email triage - read inbox, categorize, and take actions
Domain: Email Management & Automation
"""

import json
import re
from typing import Any, Dict, List
from datetime import datetime, timedelta


def get_email_data(name: str) -> dict:
    """Returns email inbox data and automation rules"""
    if name == "inbox_v1":
        # 20 emails with varied content, senders, and edge cases
        # I had LLM generate some of these emails, and tried adding my own emails
        # I tried a grading scheme where I would look at key words
        emails = [
            {
                "id": "email_001",
                "subject": "URGENT: Project deadline moved to Friday",
                "body": "Hi team, we need to finish the project ASAP. The deadline has been moved to this Friday. Please prioritize this work.",
                "sender": "boss@company.com",
                "date": "2025-01-15T10:30:00Z",
                "read": False
            },
            {
                "id": "email_002", 
                "subject": "Weekly Newsletter - Tech Updates",
                "body": "Check out our latest tech news and updates. Click here to unsubscribe from this newsletter.",
                "sender": "newsletter@techcorp.com",
                "date": "2025-01-14T08:00:00Z",
                "read": True
            },
            {
                "id": "email_003",
                "subject": "WIN $1000 NOW! Limited Time Offer",
                "body": "You've won $1000! Click here to claim your prize. Act now before it's too late!",
                "sender": "winner@spam.com",
                "date": "2025-01-13T15:45:00Z",
                "read": False
            },
            {
                "id": "email_004",
                "subject": "Meeting tomorrow at 2pm",
                "body": "Don't forget about our meeting tomorrow at 2pm in conference room A.",
                "sender": "colleague@company.com",
                "date": "2025-01-14T16:20:00Z",
                "read": True
            },
            {
                "id": "email_005",
                "subject": "[TICKET-1234] Server down - need immediate attention",
                "body": "The production server is down. This is urgent and needs immediate attention.",
                "sender": "alerts@company.com",
                "date": "2025-01-15T09:15:00Z",
                "read": False
            },
            {
                "id": "email_006",
                "subject": "VIP Client Request - Priority Support",
                "body": "Our VIP client needs immediate assistance with their account.",
                "sender": "vip@client.com",
                "date": "2025-01-15T11:00:00Z",
                "read": False
            },
            {
                "id": "email_007",
                "subject": "Regular project update",
                "body": "Here's the weekly update on the project progress. Everything is on track.",
                "sender": "pm@company.com",
                "date": "2025-01-14T10:00:00Z",
                "read": True
            },
            {
                "id": "email_008",
                "subject": "ASAP: Budget approval needed",
                "body": "We need budget approval as soon as possible for the new project.",
                "sender": "finance@company.com",
                "date": "2025-01-15T12:00:00Z",
                "read": False
            },
            {
                "id": "email_009",
                "subject": "Marketing Newsletter - January 2025",
                "body": "Our monthly marketing newsletter with industry insights. Unsubscribe here.",
                "sender": "marketing@newsletter.com",
                "date": "2025-01-13T10:00:00Z",
                "read": True
            },
            {
                "id": "email_010",
                "subject": "Free iPhone! Click now!",
                "body": "Congratulations! You've been selected to receive a free iPhone. Click here to claim.",
                "sender": "free@scam.com",
                "date": "2025-01-12T20:00:00Z",
                "read": False
            },
            {
                "id": "email_011",
                "subject": "Regular project update",
                "body": "Here's the weekly update on the project progress.",
                "sender": "pm@company.com",
                "date": "2025-01-14T09:00:00Z",
                "read": True
            },
            {
                "id": "email_012",
                "subject": "URGENT: Please update your profile picture",
                "body": "This is an urgent request to update your profile picture in the system. Please do this as soon as possible.",
                "sender": "hr@company.com",
                "date": "2025-01-15T08:30:00Z",
                "read": False
            },
            {
                "id": "email_013",
                "subject": "Deadline approaching - need status update",
                "body": "The project deadline is approaching. Please provide a status update.",
                "sender": "manager@company.com",
                "date": "2025-01-15T13:45:00Z",
                "read": False
            },
            {
                "id": "email_014",
                "subject": "Company Newsletter - Q1 Updates",
                "body": "Quarterly company updates and news. Unsubscribe from this newsletter.",
                "sender": "hr@company.com",
                "date": "2025-01-12T11:00:00Z",
                "read": True
            },
            {
                "id": "email_015",
                "subject": "You've won a vacation!",
                "body": "Congratulations! You've won a free vacation to Hawaii. Claim now!",
                "sender": "vacation@spam.net",
                "date": "2025-01-11T18:30:00Z",
                "read": False
            },
            {
                "id": "email_016",
                "subject": "Team lunch tomorrow",
                "body": "Don't forget about the team lunch tomorrow at noon.",
                "sender": "teammate@company.com",
                "date": "2025-01-14T17:00:00Z",
                "read": True
            },
            {
                "id": "email_017",
                "subject": "[TICKET-9999] Critical security vulnerability",
                "body": "Critical security vulnerability detected. Immediate action required.",
                "sender": "security@company.com",
                "date": "2025-01-15T07:00:00Z",
                "read": False
            },
            {
                "id": "email_018",
                "subject": "URGENT: Client meeting cancelled",
                "body": "The client meeting has been cancelled. Please update your calendar.",
                "sender": "admin@company.com",
                "date": "2025-01-15T14:20:00Z",
                "read": False
            },
            {
                "id": "email_019",
                "subject": "Product Newsletter - New Features",
                "body": "Check out our latest product features and updates. Unsubscribe here.",
                "sender": "product@newsletter.com",
                "date": "2025-01-13T12:00:00Z",
                "read": True
            },
            {
                "id": "email_020",
                "subject": "CRITICAL: Coffee machine needs refill",
                "body": "This is a critical issue - the coffee machine is empty and needs immediate attention. Please refill it as soon as possible.",
                "sender": "office@company.com",
                "date": "2025-01-10T22:00:00Z",
                "read": False
            },
            {
                "id": "email_021",
                "subject": "Work from home opportunity",
                "body": "Earn $3000 per month working from home. No experience required!",
                "sender": "work@scam.com",
                "date": "2025-01-04T17:00:00Z",
                "read": False
            },
            {
                "id": "email_022",
                "subject": "URGENT: Newsletter subscription expiring",
                "body": "Your newsletter subscription is expiring soon. Renew now to continue receiving updates. Unsubscribe here.",
                "sender": "newsletter@company.com",
                "date": "2025-01-15T14:00:00Z",
                "read": False
            },
            {
                "id": "email_023",
                "subject": "ASAP: Free consultation offer",
                "body": "Limited time offer! Get a free consultation worth $500. Act now before it's too late!",
                "sender": "consultant@business.com",
                "date": "2025-01-15T13:00:00Z",
                "read": False
            },
            {
                "id": "email_024",
                "subject": "Deadline approaching for newsletter",
                "body": "Don't miss out on our weekly newsletter. Subscribe now and unsubscribe anytime.",
                "sender": "marketing@newsletter.org",
                "date": "2025-01-15T12:00:00Z",
                "read": False
            },
            {
                "id": "email_025",
                "subject": "VIP Client Newsletter - Special Edition",
                "body": "Exclusive content for our VIP clients. This newsletter contains special offers. Unsubscribe here.",
                "sender": "vip@client.com",
                "date": "2025-01-15T11:00:00Z",
                "read": False
            },
            {
                "id": "email_026",
                "subject": "URGENT: System maintenance tonight",
                "body": "We need to perform critical system maintenance tonight. This is urgent and will affect all users.",
                "sender": "it@company.com",
                "date": "2025-01-15T14:00:00Z",
                "read": False
            },
            {
                "id": "email_027",
                "subject": "Congratulations! You've been selected",
                "body": "Congratulations! You've been selected for our exclusive program. Click here to claim your reward now!",
                "sender": "rewards@external.com",
                "date": "2025-01-15T13:30:00Z",
                "read": False
            },
            {
                "id": "email_028",
                "subject": "Monthly Newsletter - February 2025",
                "body": "Here's your monthly newsletter with company updates and news. Unsubscribe if you no longer wish to receive these.",
                "sender": "newsletter@company.com",
                "date": "2025-01-15T12:00:00Z",
                "read": True
            },
            {
                "id": "email_029",
                "subject": "Deadline extension request",
                "body": "Can we extend the deadline for the project? We need more time to complete the work.",
                "sender": "pm@company.com",
                "date": "2025-01-15T11:30:00Z",
                "read": False
            },
            {
                "id": "email_030",
                "subject": "URGENT: Security breach detected",
                "body": "We have detected a critical security breach. Immediate action required. This is urgent and affects all systems.",
                "sender": "security@company.com",
                "date": "2025-01-15T10:45:00Z",
                "read": False
            }
        ]
        
        # VIP list and automation rules
        vip_list = ["vip@client.com", "boss@company.com", "ceo@company.com"]
        
        rules = {
            "vip_list": vip_list,
            "old_email_days": 7,
            "long_thread_messages": 5,
            "urgent_keywords": ["urgent", "asap", "deadline", "critical", "immediate", "issue", "vulnerability", "down", "problem"],
            "spam_keywords": ["win", "congratulations", "click here", "act now", "limited time"],
            "newsletter_keywords": ["unsubscribe", "newsletter"]
        }
        
        return {
            "emails": emails,
            "rules": rules
        }
    
    return {"emails": [], "rules": {}}

# This prompt is kinda long, the more rows the more tokens i would use so need to be careful with that
def get_prompt() -> str:
    return """
You are building an email automation system.

IMPORTANT: You have exactly 12 steps maximum to complete this task. Plan your approach carefully and work efficiently.

STEP-BY-STEP APPROACH:
1. Use get_email_data(name='inbox_v1') to fetch the email data and rules
2. Analyze the emails and apply categorization rules
3. Generate the required output format
4. Submit your final answer

TASK:
Process 30 emails and categorize them into 4 categories: urgent, normal, spam, newsletter.

STRICT CATEGORIZATION RULES:
- URGENT: Must contain urgent keywords AND be from company domain OR be from VIP list
  * Urgent keywords: "urgent", "asap", "deadline", "critical", "immediate"
  * Company domain: @company.com
  * VIP list: ["vip@client.com", "boss@company.com", "ceo@company.com"]
- SPAM: Must contain spam keywords AND be from external domain (not @company.com)
  * Spam keywords: "win", "congratulations", "click here", "act now", "limited time"
- NEWSLETTER: Must contain "unsubscribe" in body
- NORMAL: Everything else that doesn't fit above categories

CRITICAL REQUIREMENTS:
- Must process EXACTLY 30 emails (no more, no less)
- Must categorize ALL emails into exactly one category
- Must use exact email IDs from the dataset
- Must follow categorization rules precisely
- Must handle edge cases correctly

OUTPUT FORMAT (must be exact):
{
  "processed": 30,
  "categories": {
    "urgent": ["email_001", "email_012", ...],
    "normal": ["email_002", "email_011", ...],
    "spam": ["email_003", "email_015", ...],
    "newsletter": ["email_002", "email_014", ...]
  }
}

VALIDATION CRITERIA:
- processed: Must equal 30
- categories: Must contain exactly 4 keys: urgent, normal, spam, newsletter
- Each email ID must appear in exactly one category
- All 30 email IDs must be present
- No extra or missing email IDs

WORK EFFICIENTLY:
- Use python_expression tool for processing
- Validate each step before proceeding
- Don't repeat the same operations
- Focus on accuracy over speed

Then call submit_answer with your complete result.
"""


def get_tools() -> List[Dict[str, Any]]:
    return [
        {
            "name": "python_expression",
            "description": "Execute Python code and return the result",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Python code to execute"
                    }
                },
                "required": ["expression"]
            }
        },
        {
            "name": "get_email_data",
            "description": "Get email inbox data and automation rules",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the email dataset to retrieve"
                    }
                },
                "required": ["name"]
            }
        },
        {
            "name": "submit_answer",
            "description": "Submit the final answer for grading",
            "input_schema": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "object",
                        "description": "The processed email results"
                    }
                },
                "required": ["answer"]
            }
        }
    ]


def get_tool_handlers() -> Dict[str, callable]:
    from task_framework import python_expression_tool, submit_answer_tool
    return {
        "python_expression": python_expression_tool,
        "get_email_data": get_email_data,
        "submit_answer": submit_answer_tool
    }

# A parital score grader will probalby work better for this task since there are more valid solutions 
def get_grader() -> callable:
    # Cache email data to avoid repeated calls
    _cached_email_data = None
    
    def grade_email_triage_task(answer: Any) -> Dict[str, Any]:
        """Intelligent grader with partial scoring and detailed feedback"""
        nonlocal _cached_email_data
        try:
            # Parse the answer
            if isinstance(answer, str):
                result = json.loads(answer)
            else:
                result = answer
            
            if not isinstance(result, dict):
                return {
                    "passed": False,
                    "score": 0,
                    "feedback": "Answer is not a valid dictionary"
                }
            
            # Get expected data for validation (cached)
            if _cached_email_data is None:
                _cached_email_data = get_email_data("inbox_v1")
            emails = _cached_email_data["emails"]
            rules = _cached_email_data["rules"]
            
            # Initialize scoring
            scores = {
                "structure": 0,
                "categorization": 0,
                "actions": 0,
                "tickets": 0,
                "completeness": 0
            }
            
            feedback = {
                "errors": [],
                "warnings": [],
                "suggestions": []
            }
            
            # 1. Structure Validation (30 points)
            structure_score = validate_structure(result, feedback)
            scores["structure"] = structure_score
            
            # 2. Completeness Check (40 points)
            completeness_score = validate_completeness(result, emails, feedback)
            scores["completeness"] = completeness_score
            
            # 3. Categorization Accuracy (30 points)
            categorization_score = validate_categorization(result, emails, rules, feedback)
            scores["categorization"] = categorization_score
            
            # Calculate overall score
            total_score = sum(scores.values())
            
            # Determine PASS OR FAIL based on total score only
            passed = total_score >= 80
            
            
            return {
                "passed": passed,
                "score": total_score,
                "breakdown": scores,
                "feedback": feedback,
                "detailed_analysis": generate_detailed_analysis(result, emails, rules)
            }
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0,
                "feedback": {"errors": [f"Exception during grading: {e}"]}
            }
    
    return grade_email_triage_task

def validate_structure(result: Dict, feedback: Dict) -> int:
    """Validate basic structure (30 points)"""
    score = 30
    
    # Check required fields
    required_fields = ["processed", "categories"]
    for field in required_fields:
        if field not in result:
            feedback["errors"].append(f"Missing required field: {field}")
            score -= 15
    
    # Check data types
    if not isinstance(result.get("categories", {}), dict):
        feedback["errors"].append("Categories must be a dictionary")
        score -= 15
    
    # Check processed count is integer
    if not isinstance(result.get("processed"), int):
        feedback["errors"].append("Processed count must be an integer")
        score -= 10
    
    return max(0, score)

def validate_completeness(result: Dict, emails: List[Dict], feedback: Dict) -> int:
    """Validate completeness (40 points)"""
    score = 40
    
    # Check processed count - moderately stricter penalties
    expected_count = len(emails)
    actual_count = result.get("processed", 0)
    if actual_count != expected_count:
        diff = abs(actual_count - expected_count)
        if diff == 1:
            score -= 8  # Moderate penalty for 1 off
            feedback["warnings"].append(f"Processed {actual_count} emails, expected {expected_count}")
        elif diff <= 3:
            score -= 12  # Medium penalty for 2-3 off
            feedback["warnings"].append(f"Processed {actual_count} emails, expected {expected_count}")
        else:
            score -= 20  # Large penalty for 4+ off
            feedback["errors"].append(f"Processed {actual_count} emails, expected {expected_count}")
    
    # Check all emails are categorized - partial credit
    categories = result.get("categories", {})
    all_categorized = set()
    for cat_emails in categories.values():
        if isinstance(cat_emails, list):
            all_categorized.update(cat_emails)
    
    expected_ids = {email["id"] for email in emails}
    missing_ids = expected_ids - all_categorized
    extra_ids = all_categorized - expected_ids
    
    # Partial credit for missing emails
    if missing_ids:
        missing_count = len(missing_ids)
        if missing_count == 1:
            score -= 3  # Small penalty
            feedback["warnings"].append(f"Missing 1 email: {list(missing_ids)[0]}")
        elif missing_count <= 3:
            score -= 6  # Medium penalty
            feedback["warnings"].append(f"Missing {missing_count} emails: {list(missing_ids)[:3]}")
        else:
            score -= 10  # Large penalty
            feedback["errors"].append(f"Missing {missing_count} emails: {list(missing_ids)[:3]}")
    
    # Partial credit for extra emails
    if extra_ids:
        extra_count = len(extra_ids)
        if extra_count == 1:
            score -= 2  # Small penalty
            feedback["warnings"].append(f"Extra 1 email: {list(extra_ids)[0]}")
        elif extra_count <= 3:
            score -= 4  # Medium penalty
            feedback["warnings"].append(f"Extra {extra_count} emails: {list(extra_ids)[:3]}")
        else:
            score -= 8  # Large penalty
            feedback["errors"].append(f"Extra {extra_count} emails: {list(extra_ids)[:3]}")
    
    return max(0, score)

def validate_categorization(result: Dict, emails: List[Dict], rules: Dict, feedback: Dict) -> int:
    """Validate categorization accuracy (30 points)"""
    score = 30
    
    categories = result.get("categories", {})
    required_cats = {"urgent", "normal", "spam", "newsletter"}
    missing_cats = required_cats - set(categories.keys())
    
    if missing_cats:
        feedback["errors"].append(f"Missing categories: {missing_cats}")
        score -= 8  # Reduced penalty
    
    # Calculate expected categorizations
    expected_categories = calculate_expected_categories(emails, rules)
    
    # Score each category with partial credit
    total_correct = 0
    total_expected = 0
    category_scores = {}
    
    for category in required_cats:
        if category in categories:
            expected = expected_categories[category]
            actual = set(categories[category])
            
            correct = len(actual & expected)
            total_correct += correct
            total_expected += len(expected)
            
            # Calculate category accuracy
            if len(expected) > 0:
                category_accuracy = correct / len(expected)
                category_scores[category] = category_accuracy
                
                # Moderately stricter scoring based on accuracy
                if category_accuracy >= 0.9:
                    # Full credit for good accuracy
                    pass
                elif category_accuracy >= 0.75:
                    # Small penalty for moderate accuracy
                    score -= 3
                    feedback["warnings"].append(f"{category} accuracy: {category_accuracy:.1%}")
                elif category_accuracy >= 0.6:
                    # Medium penalty for poor accuracy
                    score -= 6
                    feedback["warnings"].append(f"{category} accuracy: {category_accuracy:.1%}")
                else:
                    # Major penalty for very poor accuracy
                    score -= 8
                    feedback["errors"].append(f"{category} accuracy: {category_accuracy:.1%}")
            
            # Check for major errors (emails in wrong category)
            incorrect = actual - expected
            if incorrect:
                feedback["warnings"].append(f"{category} incorrectly includes: {list(incorrect)[:3]}")
                score -= 1  # Small penalty per error
    
    # Overall accuracy bonus/penalty - moderately stricter
    if total_expected > 0:
        accuracy = total_correct / total_expected
        if accuracy >= 0.95:
            # Bonus for excellent accuracy
            score += 2
        elif accuracy >= 0.85:
            # Good accuracy
            pass
        elif accuracy >= 0.75:
            # Moderate penalty
            score -= 4
            feedback["warnings"].append(f"Overall accuracy: {accuracy:.1%}")
        else:
            # Major penalty
            score -= 8
            feedback["errors"].append(f"Overall accuracy: {accuracy:.1%}")
    
    return max(0, score)


def calculate_expected_categories(emails: List[Dict], rules: Dict) -> Dict[str, set]:
    """Calculate expected email categorizations"""
    expected = {
        "urgent": set(),
        "spam": set(),
        "newsletter": set(),
        "normal": set()
    }
    
    for email in emails:
        subject_lower = email["subject"].lower()
        body_lower = email["body"].lower()
        sender = email["sender"]
        
        # VIP list check (highest priority)
        if sender in rules["vip_list"]:
            expected["urgent"].add(email["id"])
        # Urgent keywords
        elif any(keyword in subject_lower or keyword in body_lower for keyword in rules["urgent_keywords"]):
            expected["urgent"].add(email["id"])
        # Spam keywords (only if not urgent)
        elif any(keyword in subject_lower or keyword in body_lower for keyword in rules["spam_keywords"]):
            expected["spam"].add(email["id"])
        # Newsletter keywords
        elif any(keyword in body_lower for keyword in rules["newsletter_keywords"]):
            expected["newsletter"].add(email["id"])
        # Everything else is normal
        else:
            expected["normal"].add(email["id"])
    
    return expected

def calculate_expected_actions(categories: Dict, rules: Dict) -> Dict[str, int]:
    """Calculate expected action counts"""
    return {
        "flagged": len(categories.get("urgent", [])),
        "deleted": len(categories.get("spam", [])),
        "moved": len(categories.get("newsletter", [])),
        "archived": 0  # Based on age rules
    }

def generate_detailed_analysis(result: Dict, emails: List[Dict], rules: Dict) -> Dict:
    """Generate detailed analysis for feedback"""
    analysis = {
        "email_breakdown": {},
        "rule_application": {},
        "performance_metrics": {}
    }
    
    # Analyze each email
    for email in emails:
        email_id = email["id"]
        analysis["email_breakdown"][email_id] = {
            "subject": email["subject"],
            "sender": email["sender"],
            "categorized_as": "unknown",
            "expected_category": "unknown",
            "correct": False
        }
    
    # Fill in actual categorizations
    categories = result.get("categories", {})
    for category, email_ids in categories.items():
        for email_id in email_ids:
            if email_id in analysis["email_breakdown"]:
                analysis["email_breakdown"][email_id]["categorized_as"] = category
    
    # Calculate expected categorizations
    expected_categories = calculate_expected_categories(emails, rules)
    for category, email_ids in expected_categories.items():
        for email_id in email_ids:
            if email_id in analysis["email_breakdown"]:
                analysis["email_breakdown"][email_id]["expected_category"] = category
                analysis["email_breakdown"][email_id]["correct"] = (
                    analysis["email_breakdown"][email_id]["categorized_as"] == category
                )
    
    return analysis

