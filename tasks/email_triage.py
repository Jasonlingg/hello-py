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


def get_prompt() -> str:
    return """
You are building an email automation system.

Given:
- 25 emails in inbox (JSON format with subject, body, sender, date)
- Automation rules (JSON)

Task:
Write Python code that:
1. Reads all emails
2. Categorizes each email (urgent, normal, spam, newsletter)
3. Takes appropriate actions based on rules
4. Generates summary report

CATEGORIZATION RULES:
- Urgent: Contains "urgent", "asap", "deadline" + from boss/client
- Spam: From unknown sender + promotional language
- Newsletter: Has "unsubscribe" link + marketing content
- Normal: Everything else

ACTIONS TO TAKE:
- Urgent: Flag, move to "Urgent" folder, send notification
- Spam: Delete permanently
- Newsletter: Move to "Newsletters" folder
- Normal: Keep in inbox

ADVANCED RULES:
- If email chain has >5 messages, archive entire thread
- If sender is VIP list, always mark urgent
- If email is >7 days old and unread, archive
- If subject contains [TICKET-####], extract ticket number

OUTPUT FORMAT:
{
  "processed": 25,
  "categories": {
    "urgent": [...email_ids...],
    "normal": [...],
    "spam": [...],
    "newsletter": [...]
  },
  "actions_taken": {
    "flagged": 5,
    "deleted": 12,
    "archived": 8,
    "moved": 25
  },
  "tickets_found": ["TICKET-1234", "TICKET-5678"],
  "errors": []
}

REQUIREMENTS:
- Must categorize ALL 25 emails
- Must apply ALL rules correctly
- Must handle malformed emails gracefully
- Must extract ticket numbers with regex
- Must respect VIP list priority
- asnwer must be a valid python dictionary

Use get_email_data(name='inbox_v1') to fetch the email data and rules.
Then write and execute Python code to process all emails according to the rules.
Finally, call submit_answer with your results.
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


def get_grader() -> callable:
    # Cache email data to avoid repeated calls
    _cached_email_data = None
    
    def grade_email_triage_task(answer: Any) -> bool:
        """Grade the email triage task result"""
        nonlocal _cached_email_data
        try:
            # Parse the answer
            if isinstance(answer, str):
                result = json.loads(answer)
            else:
                result = answer
            
            if not isinstance(result, dict):
                return False
            
            # Get expected data for validation (cached)
            if _cached_email_data is None:
                _cached_email_data = get_email_data("inbox_v1")
            emails = _cached_email_data["emails"]
            rules = _cached_email_data["rules"]
            
            # Check 1: Must process all 25 emails
            if result.get("processed") != 25:
                print(f"Processed {result.get('processed')} emails, expected 25")
                return False
            
            # Check 2: Must have all required categories
            categories = result.get("categories", {})
            required_cats = {"urgent", "normal", "spam", "newsletter"}
            missing_cats = required_cats - set(categories.keys())
            if missing_cats:
                print(f"Missing categories: {missing_cats}")
                return False
            
            # Check 3: All email IDs must be categorized
            all_categorized = set()
            for cat_emails in categories.values():
                if isinstance(cat_emails, list):
                    all_categorized.update(cat_emails)
            
            expected_ids = {email["id"] for email in emails}
            missing_ids = expected_ids - all_categorized
            extra_ids = all_categorized - expected_ids
            if missing_ids or extra_ids:
                print(f"Missing IDs: {missing_ids}, Extra IDs: {extra_ids}")
                return False
            
            # Check 4: Categorization accuracy - simplified validation
            expected_urgent = set()
            expected_spam = set()
            expected_newsletter = set()
            
            for email in emails:
                subject_lower = email["subject"].lower()
                body_lower = email["body"].lower()
                sender = email["sender"]
                
                # VIP list check
                if sender in rules["vip_list"]:
                    expected_urgent.add(email["id"])
                # Urgent keywords (priority over spam)
                elif any(keyword in subject_lower or keyword in body_lower for keyword in rules["urgent_keywords"]):
                    expected_urgent.add(email["id"])
                # Spam keywords (only if not urgent)
                elif any(keyword in subject_lower or keyword in body_lower for keyword in rules["spam_keywords"]):
                    expected_spam.add(email["id"])
                # Newsletter keywords
                elif any(keyword in body_lower for keyword in rules["newsletter_keywords"]):
                    expected_newsletter.add(email["id"])
            
            # Check categorization accuracy (simplified)
            actual_urgent = set(categories.get("urgent", []))
            actual_spam = set(categories.get("spam", []))
            actual_newsletter = set(categories.get("newsletter", []))
            
            # Require at least 75% accuracy for urgent/newsletter, 60% for spam
            urgent_accuracy = len(actual_urgent & expected_urgent) / len(expected_urgent) if expected_urgent else 1.0
            spam_accuracy = len(actual_spam & expected_spam) / len(expected_spam) if expected_spam else 1.0
            newsletter_accuracy = len(actual_newsletter & expected_newsletter) / len(expected_newsletter) if expected_newsletter else 1.0
            
            if urgent_accuracy < 0.75:
                print(f"Urgent accuracy {urgent_accuracy:.1%} below 75% threshold")
                return False
            if spam_accuracy < 0.6:  # Lower threshold for more variation
                print(f"Spam accuracy {spam_accuracy:.1%} below 60% threshold")
                return False
            if newsletter_accuracy < 0.75:
                print(f"Newsletter accuracy {newsletter_accuracy:.1%} below 75% threshold")
                return False
            
            # Check 5: Basic structure validation
            actions = result.get("actions_taken", {})
            if not isinstance(actions, dict):
                print("Actions taken is not a dictionary")
                return False
            if not isinstance(result.get("tickets_found", []), list):
                print("Tickets found is not a list")
                return False
            
            # Check 6: Ticket extraction (simplified)
            tickets_found = result.get("tickets_found", [])
            expected_tickets = []
            for email in emails:
                ticket_match = re.search(r'\[TICKET-(\d+)\]', email["subject"])
                if ticket_match:
                    expected_tickets.append(f"TICKET-{ticket_match.group(1)}")
            
            # Must find at least 80% of expected tickets
            if len(tickets_found) < len(expected_tickets) * 0.8:
                print(f"Ticket accuracy {len(tickets_found)}/{len(expected_tickets)} below 80% threshold")
                return False
            
            print(" ALL CHECKS PASSED!")
            return True
            
        except Exception as e:
            print(f"Exception during grading: {e}")
            return False
    
    return grade_email_triage_task
