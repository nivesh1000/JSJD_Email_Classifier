import logging
import re

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def classify_emails(emails, groups):
    """
    Classify emails into multiple groups based on matching keywords
    in the subject and body using regex for exact word matching.

    Args:
        emails (List[Dict]): List of emails with email details.
        groups (List[Dict]): List of group dictionaries with keywords.

    Returns:
        List[Dict]: List of emails with assigned groups and matched keyword IDs.
    """

    # Find the default group (group with no keywords)
    default_group = next((group for group in groups if not group.get("keywords")), None)

    # Find the unsubscribe group
    unsubscribe_group = next((group for group in groups if group.get("name") == "Unsubscribe Requests"), None)

    for email in emails:
        subject = email.get("subject", "").lower()
        body = email.get("body", "").lower()
        matched_groups = {}

        # Check if email belongs to the unsubscribe group first
        if unsubscribe_group:
            for keyword_data in unsubscribe_group.get("keywords", []):
                keyword = keyword_data["keyword"].lower()
                if re.search(rf"\b{re.escape(keyword)}\b", subject, re.IGNORECASE) or \
                   re.search(rf"\b{re.escape(keyword)}\b", body, re.IGNORECASE):
                    email["group"] = [{"group_id": unsubscribe_group["id"], "keyword_id": [keyword_data["id"]]}]
                    break  # Stop checking further groups

        if email.get("group"):
            continue  # Skip further processing if the email is already grouped

        # Check keywords in subject and body
        for group in groups:
            for keyword_data in group.get("keywords", []):
                keyword = keyword_data["keyword"].lower()
                
                if re.search(rf"\b{keyword}\b", subject, re.IGNORECASE) or \
                   re.search(rf"\b{keyword}\b", body, re.IGNORECASE):
                    if group["id"] not in matched_groups:
                        matched_groups[group["id"]] = []
                    if keyword_data["id"] not in matched_groups[group["id"]]:
                        matched_groups[group["id"]].append(keyword_data["id"])

        # Convert matched_groups dictionary to required format
        email["group"] = [{"group_id": group_id, "keyword_id": keyword_ids}
                          for group_id, keyword_ids in matched_groups.items()]

        # Assign default group if no match was found
        if not email["group"] and default_group:
            email["group"] = [{"group_id": default_group["id"], "keyword_id": []}]

    return emails
