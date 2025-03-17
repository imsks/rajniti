import requests
from pathlib import Path

# Define the URL and headers
# webpage_url = "https://results.eci.gov.in/ResultAcGenNov2024/partywiseresult-S13.htm"
# headers = {
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
#     "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
#     "Cache-Control": "max-age=0",
#     "Referer": "https://results.eci.gov.in/ResultAcGenNov2024/partywiseresult-S13.htm",
#     "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
# }


# Directory to save HTML files
# output_dir = Path("html_files")
# output_dir.mkdir(exist_ok=True)

def save_html_file(output_file, response):
    """Fetch and save HTML from a URL without retries."""
    try:
        output_file.write_text(response, encoding="utf-8")
        print(f"HTML saved to: {output_file}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {output_file}: {e}")

# # Save the HTML content of the specified page
# output_file = output_dir / "partywisewinresult.html"
# save_html_file(webpage_url, output_file)

def init():
    # Define the URL and headers
    webpage_url = "https://results.eci.gov.in/ResultAcGenNov2024/partywiseresult-S13.htm"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Cache-Control": "max-age=0",
        "Referer": "https://results.eci.gov.in/ResultAcGenNov2024/partywiseresult-S13.htm",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
    }

    # Make a single request
    response = requests.get(webpage_url, headers=headers)

    if response.status_code == 200:
            output_file = Path("html_files") / "partywisewinresult.html"
            save_html_file(output_file, response.text)
    else:
        print(f"Failed to fetch {webpage_url}. Status code: {response.status_code}")

    # Directory to save HTML files