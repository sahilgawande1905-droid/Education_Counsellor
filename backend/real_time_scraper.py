import requests
from bs4 import BeautifulSoup
import json

def fetch_real_time_cutoffs(url: str):
    """
    Fetches real-time HTML tables from an educational website 
    and converts them into structured JSON cutoff data.
    """
    print(f"🌐 [Scraper] Initiating connection to: {url}")
    
    # Use a realistic User-Agent to bypass basic anti-bot protections
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 403:
            return {"error": "Website is blocking scrapers (Cloudflare/403). Try another URL."}
        elif response.status_code != 200:
            return {"error": f"Failed to fetch. Status code: {response.status_code}"}

        print("✅ [Scraper] Page downloaded successfully. Parsing HTML tables...")
        
        # Parse the raw HTML using pure Python to avoid C++ compiler issues
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        
        if not tables:
            return {"error": "No data tables found on this page."}

        print(f"📊 [Scraper] Found {len(tables)} data tables. Extracting...")
        
        scraped_data = []
        for i, table in enumerate(tables):
            table_data = []
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                cols = [ele.text.strip() for ele in cols]
                if cols:
                    table_data.append(cols)
            
            scraped_data.append({
                "table_index": i + 1,
                "total_rows": len(table_data),
                "data": table_data[:5]  # Show top 5 rows for demo preview
            })

        return json.dumps(scraped_data, indent=4)

    except Exception as e:
        return {"error": f"Scraping failed: {str(e)}"}

# ==========================================
# TEST THE SCRAPER ON LIVE DATA
# ==========================================
if __name__ == "__main__":
    # Example: Scraping a Wikipedia table of IITs as a reliable demo target.
    # In reality, you can replace this with a CollegePravesh or Exam portal URL.
    TEST_URL = "https://en.wikipedia.org/wiki/Joint_Entrance_Examination_%E2%80%93_Advanced"
    
    print("\n🚀 Starting Real-Time Web Scraper...")
    result = fetch_real_time_cutoffs(TEST_URL)
    
    print("\n" + "="*50)
    print("📈 SCRAPED LIVE DATA (JSON OUTPUT):")
    print("="*50)
    print(result)
