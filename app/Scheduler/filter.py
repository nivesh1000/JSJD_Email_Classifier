import logging
import re
from typing import List, Dict
from app.Logger.logger import JsJdLogger, LineFileProvider

logger = JsJdLogger()

def classify_emails(emails: List[Dict], groups: List[Dict]) -> List[Dict]:
    """
    Classify emails into multiple groups based on matching keywords
    in the subject and body using regex for exact word matching.

    Args:
        emails (List[Dict]): List of emails with email details.
        groups (List[Dict]): List of group dictionaries with keywords.

    Returns:
        List[Dict]: List of emails with assigned groups and matched keyword IDs.
    """
    try:
        # Validate input types
        if not isinstance(emails, list):
            logger.error("Emails parameter must be a list", LineFileProvider().get_file_info())
            raise TypeError("Emails parameter must be a list")
        if not isinstance(groups, list):
            logger.error("Groups parameter must be a list", LineFileProvider().get_file_info())
            raise TypeError("Groups parameter must be a list")

        # Find the default group (group with no keywords)
        default_group = None
        try:
            for group in groups:
                if not isinstance(group, dict):
                    logger.warning(f"Invalid group format: {group}", LineFileProvider().get_file_info())
                    continue
                if not group.get("keywords"):
                    default_group = group
                    logger.debug(f"Default group found: {default_group['id']}", LineFileProvider().get_file_info())
                    break
        except Exception as e:
            logger.error(f"Error finding default group: {str(e)}", LineFileProvider().get_file_info())

        # Find the unsubscribe group
        unsubscribe_group = None
        try:
            for group in groups:
                if not isinstance(group, dict):
                    logger.warning(f"Invalid group format: {group}", LineFileProvider().get_file_info())
                    continue
                if group.get("name") == "Unsubscribe Requests":
                    unsubscribe_group = group
                    logger.debug(f"Unsubscribe group found: {unsubscribe_group['id']}", LineFileProvider().get_file_info())
                    break
        except Exception as e:
            logger.error(f"Error finding unsubscribe group: {str(e)}", LineFileProvider().get_file_info())
            unsubscribe_group = None  # Proceed without unsubscribe group if error occurs

        # Process each email
        for email in emails:
            try:
                if not isinstance(email, dict):
                    logger.warning(f"Skipping invalid email format: {email}", LineFileProvider().get_file_info())
                    continue

                subject = str(email.get("subject", "")).lower()
                body = str(email.get("body", "")).lower()
                matched_groups = {}

                # Check if email belongs to the unsubscribe group first
                if unsubscribe_group:
                    try:
                        for keyword_data in unsubscribe_group.get("keywords", []):
                            if not isinstance(keyword_data, dict):
                                logger.warning(f"Invalid keyword data: {keyword_data}", LineFileProvider().get_file_info())
                                continue
                            keyword = str(keyword_data.get("keyword", "")).lower()
                            keyword_id = keyword_data.get("id")
                            if not keyword or not keyword_id:
                                # logger.warning(f"Missing keyword or ID in: {keyword_data}", LineFileProvider().get_file_info())
                                continue

                            if keywordmatcher(subject, keyword) or keywordmatcher(body, keyword):
                                email["group"] = [{"group_id": unsubscribe_group["id"], "keyword_id": [keyword_id]}]
                                # logger.info(f"Email classified as unsubscribe: {subject}", LineFileProvider().get_file_info())
                                break  # Stop checking further groups
                    except Exception as e:
                        logger.error(f"Error processing unsubscribe group for email: {subject}. Error: {str(e)}", LineFileProvider().get_file_info())

                # Skip further processing if the email is already grouped
                if email.get("group"):
                    continue

                # Check keywords in subject and body for other groups
                for group in groups:
                    try:
                        if not isinstance(group, dict) or "id" not in group:
                            logger.warning(f"Skipping invalid group: {group}", LineFileProvider().get_file_info())
                            continue
                        group_id = group["id"]

                        for keyword_data in group.get("keywords", []):
                            if not isinstance(keyword_data, dict):
                                logger.warning(f"Invalid keyword data: {keyword_data}", LineFileProvider().get_file_info())
                                continue
                            keyword = str(keyword_data.get("keyword", "")).lower()
                            keyword_id = keyword_data.get("id")
                            if not keyword or not keyword_id:
                                logger.warning(f"Missing keyword or ID in: {keyword_data}", LineFileProvider().get_file_info())
                                continue

                            if keywordmatcher(subject, keyword) or keywordmatcher(body, keyword):
                                if group_id not in matched_groups:
                                    matched_groups[group_id] = []
                                if keyword_id not in matched_groups[group_id]:
                                    matched_groups[group_id].append(keyword_id)
                                    logger.debug(f"Matched keyword '{keyword}' for group {group_id} in email: {subject}", LineFileProvider().get_file_info())
                    except Exception as e:
                        logger.error(f"Error processing group {group.get('id', 'unknown')} for email {subject}: {str(e)}", LineFileProvider().get_file_info())

                # Convert matched_groups dictionary to required format
                try:
                    email["group"] = [{"group_id": group_id, "keyword_id": keyword_ids}
                                    for group_id, keyword_ids in matched_groups.items()]
                except Exception as e:
                    logger.error(f"Error formatting groups for email {subject}: {str(e)}", LineFileProvider().get_file_info())
                    email["group"] = []  # Reset to empty list on error

                # Assign default group if no match was found
                if not email["group"] and default_group:
                    try:
                        email["group"] = [{"group_id": default_group["id"], "keyword_id": []}]
                        logger.info(f"Assigned default group to email: {subject}", LineFileProvider().get_file_info())
                    except Exception as e:
                        logger.error(f"Error assigning default group to email {subject}: {str(e)}", LineFileProvider().get_file_info())
                        email["group"] = []  # Reset to empty list on error

            except Exception as e:
                logger.error(f"Unexpected error processing email {email.get('subject', 'unknown')}: {str(e)}", LineFileProvider().get_file_info())
                email["group"] = []  # Ensure email has a group key even on failure

        return emails

    except Exception as e:
        logger.error(f"Critical error in classify_emails: {str(e)}", LineFileProvider().get_file_info())
        raise  # Re-raise critical errors to alert the caller

def keywordmatcher(text: str, keyword: str) -> bool:
    """
    Match a keyword in text using regex with word boundaries.

    Args:
        text (str): The text to search in.
        keyword (str): The keyword to search for.

    Returns:
        bool: True if the keyword matches, False otherwise.
    """
    try:
        if not isinstance(text, str) or not isinstance(keyword, str):
            logger.warning(f"Invalid input to keywordmatcher - text: {type(text)}, keyword: {type(keyword)}", LineFileProvider().get_file_info())
            return False
        return bool(re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE))
    except re.error as e:
        logger.error(f"Regex error in keywordmatcher with keyword '{keyword}': {str(e)}", LineFileProvider().get_file_info())
        return False
    except Exception as e:
        logger.error(f"Unexpected error in keywordmatcher with keyword '{keyword}': {str(e)}", LineFileProvider().get_file_info())
        return False