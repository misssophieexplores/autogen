queries_no_formatting_instructions = {
    "easy": [
        "Look for studio apartments in Liverpool City Centre with rent under £700 per month.",
        "Search for furnished studio and 1-bedroom apartments in Los Angeles available for under $1,800 per month."
    ],
    "advanced": [
        "Find pet-friendly studio flats for rent London within less than half a mile from the nearest metro station.",
        "Find new-built detached houses for rent in Greater Manchester with at least 3 bedrooms and off-street parking.",
        "Find furnished student apartments near the University of Texas at Austin for less than $500 per person per month, ranked by price per person."
    ],
    "TEST": [
        "What is the weather like today in Cape Town?",
        "What is the weather forecast for Mannheim tomorrow?",
        "What is the URL of today's featured article on Wikipedia?"
    ]

}
def create_instructions(num_listings= None, num_pages= None)->str:
    details = "Provide the address, price, and URL of the detail page for each listing."
    if num_listings is None and num_pages is None:
        return f" Instructions: {details}"
    elif num_listings is None:
        return f" Instructions: Please find listings from at least {num_pages} different websites. {details}"
    elif num_pages is None:
        return f" Instructions: Please find at least {num_listings} listings. {details}"
    else: # both are not None
        return f" Instructions: Please find {num_listings} listings from at least {num_pages} different websites. {details}"
        
# instructions = " Instruction: Use 4 to 5 websites to find 5 relevant listings for each query (20-25 total listings). Provide the address, price, and URL of the detail page for each listing."

# I'm looking for a studio apartment in Liverpool City Centre with rent under £700 per month. I need the address, price, and URL of the detail page.