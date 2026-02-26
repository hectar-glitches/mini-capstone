from datetime import datetime
import requests
import io


def fetch_data():
    """
    Fetches CSV data from TEPCO and returns a file-like object.
    
    Args:
        None
        
    Returns:
        File-like object (io.BytesIO) that can be read by pandas, or None if error
    """
    
    # Example URLs for reference:
    # https://www.tepco.co.jp/forecast/html/images/eria_jukyu_202601_03.csv
    # https://www.tepco.co.jp/forecast/html/images/eria_jukyu_202512_03.csv
    
    try:
        # Get today's date
        today = datetime.now()
        
        # Use provided values or default to previous month
        year = today.year
        month = today.month - 1 if today.month > 1 else 12
        if month == 1:
            year -= 1
            month = 12
            
        else:
            month = today.month - 1
        
        # Build the link
        dynamic_url = f"https://www.tepco.co.jp/forecast/html/images/eria_jukyu_{year}{month:02d}_03.csv"
        
        print(f"Fetching data from: {dynamic_url}")
        
        # Make the request
        response = requests.get(dynamic_url, timeout=30)
        
        # Check if successful
        response.raise_for_status()
        
        print(f"Successfully fetched data (Status: {response.status_code})")
        
        # Convert response bytes to file-like object
        file_like = io.BytesIO(response.content)
        
        return file_like
        
    except requests.exceptions.Timeout:
        print("Error: Request timed out")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"  (Status code: {response.status_code})")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None