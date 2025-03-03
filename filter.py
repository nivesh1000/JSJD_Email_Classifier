import logging
import re

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

 
def classify_emails(emails, groups_data):
    """
    Classify emails into multiple groups based on matching keywords
    in the subject and body. Each matched group will have a list of keyword IDs.
 
    Args:
        emails (List[Dict]): List of emails with email details.
        groups_data (Dict): JSON containing group information and keywords.
 
    Returns:
        List[Dict]: List of emails with assigned groups and matched keyword IDs.
    """
    groups = groups_data["data"]["groups"]
 
    # Find the default group (group with no keywords)
    default_group = next((group for group in groups if not group.get("keywords")), None)
 
    for email in emails:
        subject = email.get("subject", "").lower()
        body = email.get("body", "").lower()
        matched_groups = {}
 
        # Check keywords in subject
        for group in groups:
            for keyword_data in group.get("keywords", []):
                keyword = re.escape(keyword_data["keyword"].lower())  # Escape special characters
                if re.search(rf"\b{keyword}\b", subject, re.IGNORECASE):  # Exact word match
                    if group["id"] not in matched_groups:
                        matched_groups[group["id"]] = []
                    if keyword_data["id"] not in matched_groups[group["id"]]:    
                        matched_groups[group["id"]].append(keyword_data["id"])
 
        # Check keywords in body
        for group in groups:
            for keyword_data in group.get("keywords", []):
                keyword = re.escape(keyword_data["keyword"].lower())  # Escape special characters
                if re.search(rf"\b{keyword}\b", body, re.IGNORECASE):  # Exact word match
                    if group["id"] not in matched_groups:
                        matched_groups[group["id"]] = []
                    if keyword_data["id"] not in matched_groups[group["id"]]:
                        matched_groups[group["id"]].append(keyword_data["id"])
 
        # Convert matched_groups dictionary to the required format
        email["group"] = [{"group_id": group_id, "keyword_id": keyword_ids}
                          for group_id, keyword_ids in matched_groups.items()]
 
        # If no group was assigned, use the default group
        if not email["group"] and default_group:
            email["group"] = [{"group_id": default_group["id"], "keyword_id": []}]
 
    return emails
 
 