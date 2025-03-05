import logging

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def classify_emails(emails, groups):
    """
    Classify emails into multiple groups based on matching keywords
    in the subject and body. Each matched group will have a list of keyword IDs.

    Args:
        emails (List[Dict]): List of emails with email details.
        groups_data (Dict): JSON containing group information and keywords.

    Returns:
        List[Dict]: List of emails with assigned groups and matched keyword IDs.
    """


    # Find the default group using a simple loop (group with no keywords)
    default_group = None
    for group in groups:
        if not group.get("keywords"):
            default_group = group
            break  # Stop looping once we find the default group

    for email in emails:
        subject = email.get("subject", "").lower()
        body = email.get("body", "").lower()

        # Convert subject and body into sets of words for fast lookup
        subject_words = set(subject.split())
        body_words = set(body.split())

        matched_groups = {}

        # Check keywords in subject
        for group in groups:
            for keyword_data in group.get("keywords", []):
                keyword = keyword_data["keyword"].lower()  # Extract keyword text
                if keyword in subject_words:  # Exact word match
                    if group["id"] not in matched_groups:
                        matched_groups[group["id"]] = []
                    if keyword_data["id"] not in matched_groups[group["id"]]:
                        matched_groups[group["id"]].append(keyword_data["id"])

        # Check keywords in body
        for group in groups:
            for keyword_data in group.get("keywords", []):
                keyword = keyword_data["keyword"].lower()
                if keyword in body_words:  # Exact word match
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
