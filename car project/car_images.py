# car_images.py - GOOGLE SEARCH VERSION
import urllib.parse

def get_car_image(brand, model, year=None):
    """Generate Google search URL for car image"""
    if not brand or not model:
        return None
    
    # Create search query
    search_query = f"{brand} {model} car"
    if year:
        search_query = f"{brand} {model} {year} car"
    
    # URL encode the query
    encoded_query = urllib.parse.quote_plus(search_query)
    
    # Google Images search URL
    google_url = f"https://www.google.com/search?q={encoded_query}&tbm=isch"
    
    print(f"🔍 Google Search: {search_query}")
    return google_url

def get_car_image_direct(brand, model, year=None):
    """Alternative: Direct image search (more specific)"""
    if not brand or not model:
        return None
    
    search_query = f"{brand} {model} car exterior front view"
    if year:
        search_query = f"{brand} {model} {year} car exterior"
    
    encoded_query = urllib.parse.quote_plus(search_query)
    google_url = f"https://www.google.com/search?q={encoded_query}&tbm=isch"
    
    return google_url