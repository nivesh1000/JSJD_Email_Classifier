import logging
import re
from typing import List, Dict
# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
def classify_emails(emails: List[Dict], groups: List[Dict]) -> List[Dict]:
    """
    Classify emails into multiple groups based on matching keywords
    in the subject and body using the keywordmatcher function.

    Args:
        emails (List[Dict]): List of emails with email details.
        groups (List[Dict]): List of group dictionaries with keywords.

    Returns:
        List[Dict]: List of emails with assigned groups and matched keyword IDs.
    """
    try:
        # Validate input types
        if not isinstance(emails, list):
            logger.error("Emails parameter must be a list")
            raise TypeError("Emails parameter must be a list")
        if not isinstance(groups, list):
            logger.error("Groups parameter must be a list")
            raise TypeError("Groups parameter must be a list")
        # print(groups)
        # exit(1)
        # Find the default group (group with no keywords)
        default_group = None
        try:
            for group in groups:
                if not group.get("keywords"):
                    default_group = group
                    break
        except Exception as e:
            logger.error(f"Error finding default group: {str(e)}")
            default_group = None

        # Find the unsubscribe group
        unsubscribe_group = None
        try:
            for group in groups:
                if group.get("name") == "Unsubscribe Requests":
                    unsubscribe_group = group
                    break
        except Exception as e:
            logger.error(f"Error finding unsubscribe group: {str(e)}")
        # print(f"Unsubscribe group: {unsubscribe_group}")
        # print(f"Default group: {default_group}")
        # exit(1)    
        # Process each email
        for email in emails:
            try:
                subject = email.get("subject", "").lower()
                body = email.get("body", "").lower()
                matched_groups = {}

                # Check if email belongs to the unsubscribe group first
                if unsubscribe_group:
                    try:
                        positive_keywords = unsubscribe_group.get("keywords", [])
                        negative_keywords = unsubscribe_group.get("negative_keywords", [])
                        for positive_keyword in positive_keywords:
                            keyword_id = positive_keyword["id"]
                            if keywordmatcher(subject, positive_keyword["keyword"]) or keywordmatcher(body, positive_keyword["keyword"]):
                                flag = True
                                for negative_keyword_data in negative_keywords:
                                    negative_keyword = negative_keyword_data["keyword"]
                                    if keywordmatcher(subject, negative_keyword) or keywordmatcher(body, negative_keyword):
                                        flag = False
                                        break
                                if flag:
                                    email["group"] = [{"group_id": unsubscribe_group["id"], "keyword_id": [keyword_id]}]
                                    break
                    except Exception as e:
                        logger.error(f"Error processing unsubscribe group for email: {subject}. Error: {str(e)}")

                # Skip further processing if the email is already grouped
                if email.get("group"):
                    continue

                # Check keywords in subject and body for other groups
                for group in groups:
                    try:
                        group_id = group["id"]
                        positive_keywords = group.get("keywords", [])
                        negative_keywords = group.get("negative_keywords", [])
                        for positive_keyword in positive_keywords:
                            keyword_id = positive_keyword.get("id")
                            if keywordmatcher(subject, positive_keyword["keyword"]) or keywordmatcher(body, positive_keyword["keyword"]):
                                flag = True
                                for negative_keyword_data in negative_keywords:
                                    negative_keyword = negative_keyword_data["keyword"]
                                    if keywordmatcher(subject, negative_keyword) or keywordmatcher(body, negative_keyword):
                                        flag = False
                                        break
                                if flag:
                                    if group_id not in matched_groups:
                                        matched_groups[group_id] = []
                                    if keyword_id not in matched_groups[group_id]:
                                        matched_groups[group_id].append(keyword_id)

                    except Exception as e:
                        logger.error(f"Error processing group :{group.get('id', 'unknown')} for email :{subject}: {str(e)}")

                email["group"] = [{"group_id": group_id, "keyword_id": keyword_ids}
                                    for group_id, keyword_ids in matched_groups.items()]

                # Assign default group if no match was found
                if not email["group"] and default_group:
                    email["group"] = [{"group_id": default_group["id"], "keyword_id": []}]

            except Exception as e:
                logger.error(f"Unexpected error processing email: {email.get('subject', 'unknown')}: {str(e)}")
                email["group"] = []

        return emails

    except Exception as e:
        logger.error(f"Error in classify_emails: {str(e)}")

def keywordmatcher(text: str, keyword: str) -> bool:
    """
    Match a keyword in text using regex with word boundaries.

    Args:
        text (str): The text to search in.
        keyword (str): The keyword to search for.

    Returns:
        bool: True if the keyword matches, False otherwise.
    """
    return bool(re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE))