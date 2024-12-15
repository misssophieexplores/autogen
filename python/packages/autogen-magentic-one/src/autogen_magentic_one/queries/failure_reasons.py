import json
# list of observed failure reasons
FAILURE_REASONS = [
    "accepting_cookies",
    "captcha",
    "code_error_action_specification",
    "code_error_answer_formatting",
    "early_stopping",
    "limit_reached",
    "repetitive_steps",
    "repetitive_steps_with_new_links",
    "results_incomplete",
    "step_failure",
    "token_limitation",
    "tool_use",
    "tool_use_IamUnableTO",
    "interrupted",
    "guarded_content",
    "new_window_unaccessible",
    "listing_detail_url",
    "listing_detail_address",
    "listing_detail_price",
    "filter_use",
    "google_query_too_specific"
    ]
def modify_metrics(file_path, updates):
    """
    Modify the metrics JSON file with new values, validating specific fields.

    Args:
        file_path (str): Path to the metrics JSON file.
        updates (dict): A dictionary of key-value pairs to update in the metrics.

    Returns:
        dict: The updated metrics dictionary.
    """
    # Step 1: Read the existing metrics
    with open(file_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    # Step 2: Update the metrics with validation for failure reasons
    for key, value in updates.items():
        if key == "primary_failure":
            # Validate primary failure
            assert value in FAILURE_REASONS, f"Invalid {key}: {value}. Must be one of {FAILURE_REASONS}."
        elif key == "secondary_failure":
            # Validate secondary failure
            if value is not None:
                assert isinstance(value, list), f"{key} must be a list or None. Got: {type(value).__name__}."
                invalid_reasons = [reason for reason in value if reason not in FAILURE_REASONS]
                assert not invalid_reasons, f"Invalid entries in {key}: {invalid_reasons}. Must be in {FAILURE_REASONS}."
        if key in metrics:
            metrics[key] = value
        else:
            print(f"Warning: Key '{key}' not found in metrics. Adding it.")
            metrics[key] = value

    # Step 3: Save the updated metrics
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4, ensure_ascii=False)

    return metrics