import requests
from bs4 import BeautifulSoup
import json


url = "https://kb.bullseyelocations.com/article/60-india-state-codes"

response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')


table = soup.find('table')


if table:
    rows = table.find_all('tr')
    
    states_data = []
    
    # Loop through the rows and extract the data
    for row in rows[1:]:  # Skip the header row
        cols = row.find_all('td')
        if len(cols) >= 3:
            state_name = cols[0].get_text(strip=True)
            state_id = cols[1].get_text(strip=True)
            
            # Add the data to the list
            states_data.append({
                'state_name': state_name,
                'state_id': state_id,
            })

    # Save the data into a JSON file
    with open('states_data.json', 'w') as json_file:
        json.dump(states_data, json_file, indent=4)


    print("Data has been saved to 'states_data.json'")
else:
    print("Table not found. Please check the HTML structure.")
