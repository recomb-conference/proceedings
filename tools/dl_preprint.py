import os
import time
import argparse
from curl_cffi import requests

def download_biorxiv(doi, filepath):
    # Base URL for the landing page
    landing_page = f"https://www.biorxiv.org/content/{doi}"
    
    # We use a Session to capture cookies (like 'cc_cookie' or 'cf_clearance')
    with requests.Session() as s:
        print(f"[*] Visiting landing page for session cookies...")
        s.get(landing_page, impersonate="chrome120")
        
        # bioRxiv PDF URLs often require the 'v1' or 'v2' suffix for direct access.
        # We try the DOI.full.pdf first, then a common fallback.
        pdf_urls = [
            f"https://www.biorxiv.org/content/{doi}.full.pdf",
            f"https://www.biorxiv.org/content/{doi}v1.full.pdf"
        ]

        for url in pdf_urls:
            print(f"[*] Trying: {url}")
            # The 'referer' is CRITICAL for bioRxiv
            headers = {"Referer": landing_page}
            
            response = s.get(url, impersonate="chrome120", headers=headers, timeout=30)
            
            if response.status_code == 200 and b'%PDF' in response.content[:10]:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return True
            elif response.status_code == 403:
                print(f"[!] Blocked (403) on {url}")
            
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", default="downloads")
    args = parser.parse_args()

    if not os.path.exists(args.out):
        os.makedirs(args.out)

    with open(args.input, "r") as f:
        items = [line.strip() for line in f if line.strip()]

    for item in items:
        doi = item.split("doi.org/")[-1].strip().strip('/')
        filename = doi.replace("/", "_") + ".pdf"
        filepath = os.path.join(args.out, filename)

        print(f"\n>>> Processing {doi}")
        
        if "10.48550" in doi or "arxiv" in doi.lower():
            # ArXiv is usually fine with the previous logic
            # [Insert ArXiv logic here if needed]
            pass
        else:
            success = download_biorxiv(doi, filepath)
            if success:
                print(f"[+] Successfully saved {filename}")
            else:
                print(f"[!] Could not download {doi}")
        
        time.sleep(5) # Increased delay to look more human

if __name__ == "__main__":
    main()
