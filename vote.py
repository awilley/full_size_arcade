import re
import requests
import time

# Define the number of iterations and delay between them
n = 5000         # Number of times to run the loop
tdly = 12         # Delay in seconds between iterations

# 1) Create a session to hold cookies across requests
session = requests.Session()

# Common headers to look more like a real browser
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    # If you get unreadable (compressed) output, you could switch to "identity":
    "Accept-Encoding": "identity",
    # "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.usatodaynetworkservice.com/",  # Or the *exact* page hosting the poll
}

# URLs used in the process
poll_js_url = "https://secure.polldaddy.com/p/14877450.js"  # Poll JS
vote_url = "https://polls.polldaddy.com/vote-js.php"

for i in range(1, n + 1):
    print(f"\n--- Iteration {i}/{n} ---")
    try:
        # ----------------------------------------------------------------------
        # STEP A: Load the poll JavaScript (or the page embedding it).
        # ----------------------------------------------------------------------
        resp1 = session.get(poll_js_url, headers=headers, verify=False)
        print("[Step A] Poll JS:", resp1.status_code, len(resp1.content), "bytes")
        print("[Step A] First 500 characters of response:\n", resp1.text[:500], "...\n")

        # ----------------------------------------------------------------------
        # STEP B: Build a new "n" URL with a fresh timestamp, then extract n.
        # ----------------------------------------------------------------------
        timestamp = int(time.time() * 1000)  # current time in ms
        n_url = f"https://poll.fm/n/7b092bc7153e3e2975b8f23a61511995/14877450?{timestamp}"
        print("[Step B] Using n_url:", n_url)

        resp2 = session.get(n_url, headers=headers, verify=False)
        print("[Step B] n-url:", resp2.status_code, len(resp2.content), "bytes")
        print("[Step B] Full response from n-url:\n", resp2.text, "\n")

        # Example response: PDV_n14877450='686aaa13d6|686'; PD_vote14877450(0);
        pattern = re.compile(r"PDV_n14877450='([^']+)';")
        match = pattern.search(resp2.text)
        if not match:
            print("[Error] Could not find n in the second response.")
            continue  # Skip to the next iteration

        dynamic_n = match.group(1)  # e.g. "686aaa13d6|686"
        print("[Step B] Extracted n value:", dynamic_n, "\n")

        # ----------------------------------------------------------------------
        # STEP C: Make the final "vote-js.php" request, including the dynamic n.
        # ----------------------------------------------------------------------
        params = {
            "p": "14877450",           # poll ID
            "b": "1",                  # maybe "button" or something else
            "a": "66005815,",          # which answer(s) is being voted for
            "o": "",
            "va": "16",
            "cookie": "0",
            "tags": "14877450-src:poll-embed",
            "n": dynamic_n,            # The extracted n
            "url": (
                "https://www.usatodaynetworkservice.com/tangstatic/html/pbur/"
                "sf-q1a2z330306dc3.min.html"
            ),
        }

        resp3 = session.get(vote_url, params=params, headers=headers, verify=False)
        print("[Step C] Vote attempt:", resp3.status_code)
        print("[Step C] First 500 characters of response:\n", resp3.text[:500], "...")

    except requests.exceptions.RequestException as e:
        print(f"[Exception] An error occurred: {e}")
    except Exception as ex:
        print(f"[Exception] An unexpected error occurred: {ex}")

    # Delay before the next iteration, except after the last one
    if i < n:
        print(f"Waiting for {tdly} seconds before next iteration...\n")
        time.sleep(tdly)

print("\nVoting loop completed.")
