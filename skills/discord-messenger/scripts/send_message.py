#!/usr/bin/env python3
import sys
import os
import json
import urllib.request
import urllib.error

def main():
    # Retrieve the Webhook URL from the environment variable
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL environment variable is not set.", file=sys.stderr)
        sys.exit(1)
        
    # Get message content from command line argument, or stdin if not provided
    if len(sys.argv) > 1:
        message = sys.argv[1]
    else:
        message = sys.stdin.read().strip()
        
    if not message:
        print("Error: Message content is empty.", file=sys.stderr)
        sys.exit(1)
        
    payload = {
        "content": message
    }
    
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "AntigravityDiscordAgent/1.0"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as res:
            # Discord Webhook returns 204 No Content on success
            if res.status == 204:
                print("Successfully sent message to Discord.")
                sys.exit(0)
            else:
                print(f"Error: Received unexpected status code {res.status} from Discord.", file=sys.stderr)
                sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}", file=sys.stderr)
        try:
            error_body = e.read().decode("utf-8")
            print(f"Response body: {error_body}", file=sys.stderr)
        except Exception:
            pass
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network Error: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
