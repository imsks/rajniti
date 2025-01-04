import requests
from pathlib import Path

# Define the URL and headers
webpage_url = "https://results.eci.gov.in/ResultAcGenNov2024/index.htm"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Referer": "https://results.eci.gov.in/ResultAcGenNov2024/index.htm",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
}


# Directory to save HTML files
output_dir = Path("html_files")
output_dir.mkdir(exist_ok=True)  # Create directory if it doesn't exist

def save_html_single_request(url, output_path):
    """Fetch and save HTML from a URL without retries."""
    try:
        print(f"Fetching URL: {url}")
        # Make a single request
        response = requests.get(url, headers=headers, timeout=10)

        # Log response status
        print(f"Received status code: {response.status_code}")

        if response.status_code == 200:
            # Save the HTML content to the specified file
            output_path.write_text(response.text, encoding="utf-8")
            print(f"HTML saved to: {output_path}")
        else:
            print(f"Failed to fetch {url}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")

# Save the HTML content of the specified page
output_file = output_dir / "partywisewinresult.html"
save_html_single_request(webpage_url, output_file)
