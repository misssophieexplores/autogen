from typing import Union
# queries_no_formatting_instructions = {
#     "easy": [
#         "Look for studio apartments in Liverpool City Centre with rent under £700 per month.",
#         "Search for furnished studio and 1-bedroom apartments in Los Angeles available for under $1,800 per month."
#     ],
#     "advanced": [
#         "Find pet-friendly studio flats for rent London within less than half a mile from the nearest metro station.",
#         "Find new-built detached houses for rent in Greater Manchester with at least 3 bedrooms and off-street parking.",
#         "Find furnished student apartments near the University of Texas at Austin for less than $1,500 per person per month, ranked by price per person."
#     ]
# }

def generate_query_and_instructions(query_num_listings:Union[int, None], query_num_websites:Union[int, None] = None, difficulty:str = "easy", id_query:int = 0):
    """
    Generate query and instructions based on the num_listings, num_pages, and query_template.

    Args:
        num_listings (int or None): Minimum number of listings required.
        num_pages (int or None): Minimum number of websites required.
        query_template (str or None): A specific query template to format and return.

    Returns:
        tuple: (query, instructions) where instructions can be None if undefined.

    Raises:
        ValueError: If the combination of num_listings and num_pages is undefined.
    """

    instructions = None
    # Handle undefined cases
    if (query_num_listings is None and query_num_websites == 1) or \
    (query_num_listings == 1 and query_num_websites is None) or \
    (query_num_listings is not None and query_num_listings > 1 and query_num_websites == 1) or \
    (query_num_listings is not None and query_num_websites is not None and query_num_websites > query_num_listings):
        raise ValueError("Invalid combination of num_listings and num_pages.")

    queries_no_formatting_instructions = {
        "easy": [
            "Look for studio apartments in Liverpool City Centre with rent under £700 per month.",
            "Search for furnished studio and 1-bedroom apartments in Los Angeles available for under $1,800 per month."
        ],
        "advanced": [
            "Find pet-friendly studio flats for rent London within less than half a mile from the nearest metro station.",
            "Find new-built detached houses for rent in Greater Manchester with at least 3 bedrooms and off-street parking.",
            "Find furnished student apartments near the University of Texas at Austin for less than $1,500 per person per month, ranked by price per person."
        ]
    }
    query_template = queries_no_formatting_instructions[difficulty][id_query]

    # Singular mappings (adjust when singular phrasing is needed)
    plural_to_singular = {
        "studio apartments": "a studio apartment",
        "furnished studio or 1-bedroom apartments": "a furnished studio or 1-bedroom apartment",
        "listings": "listing",
        "pet-friendly studio flats": "a pet-friendly studio flat",
        "new-built detached houses": "a new-built detached house",
        "furnished student apartments": "a furnished student apartment",
    }
    # Determine whether singular or plural phrasing is needed
    use_singular = (
        (query_num_listings == 1 or query_num_listings is None) and
        (query_num_websites == 1 or query_num_websites is None)
    )

    # Adjust the query
    if query_template:
        if use_singular:
            query = query_template
            for plural, singular in plural_to_singular.items():
                query = query.replace(plural, singular)
        else:
            query = query_template
    else:
        query = None

    # Determine the instructions
    if query_num_listings is not None or query_num_websites is not None:
        if query_num_listings == 1 and query_num_websites == 1:
            instructions = "Provide the address, price, and the direct link to the listing's detail page."
        elif query_num_listings and query_num_websites:
            instructions = (
                f"Find {query_num_listings} listings from {query_num_websites} different websites. "
                "Provide the address, price, and the direct link to the listing's detail page for each one."
            )
        elif query_num_listings:
            instructions = (
                f"Find {query_num_listings} listings. "
                "Provide the address, price, and the direct link to the listing's detail page for each one."
            )
        elif query_num_websites:
            instructions = (
                f"Find listings from {query_num_websites} websites. "
                "Provide the address, price, and the direct link to the listing's detail page for each one."
            )
    else:
        instructions = None
    prompt = query if instructions is None else f"{query} {instructions}"
    return prompt

