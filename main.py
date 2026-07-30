import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

# Replace this with the scan_clause you copied in Step 1
SCAN_CLAUSE	= "( {cash} ( daily close > 1 day ago max( 20 , daily high ) and daily volume > daily sma( daily volume , 20 ) * 1.5 and 1 day ago max( 30 , daily open / 2 days ago close ) > 1.03 and daily close > daily sma( daily close , 200 ) and daily close > 20 and market cap > 500 and market cap < 12000 ) )"

def get_chartink_data(scan_clause):
    url = "https://chartink.com/screener/process"
    
    with requests.Session() as s:
        # Get the CSRF token required by Chartink
        r = s.get("https://chartink.com/screener")
        soup = BeautifulSoup(r.text, "html.parser")
        csrf_token = soup.select_one("[name='csrf-token']")['content']
        
        # Prepare headers
        s.headers['x-csrf-token'] = csrf_token
        s.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        # Execute the scan
        payload = {'scan_clause': scan_clause}
        response = s.post(url, data=payload)
        
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data.get('data', []))
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return pd.DataFrame()

if __name__ == "__main__":
    print("Running Chartink Screen...")
    df = get_chartink_data(SCAN_CLAUSE)
    
    if not df.empty:
        os.makedirs("output", exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        file_name = f"output/scan_result_{date_str}.csv"
        
        df.to_csv(file_name, index=False)
        print(f"Success! Data saved to {file_name}")
    else:
        print("No stocks passed the criteria today.")
