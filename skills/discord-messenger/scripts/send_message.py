#!/usr/bin/env python3
import sys
import os
import json
import urllib.request
import urllib.error

def load_env_url():
    url = os.environ.get("DISCORD_WEBHOOK_URL")
    if url:
        return url
    
    # Search for .env file in current directory or parents
    current = os.getcwd()
    while True:
        env_path = os.path.join(current, ".env")
        if os.path.isfile(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("#") or not line:
                            continue
                        if "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip('"').strip("'")
                            if k == "DISCORD_WEBHOOK_URL" and v:
                                return v
            except Exception:
                pass
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

    # If in a git worktree, also check the main worktree root
    try:
        import subprocess
        res = subprocess.run(["git", "rev-parse", "--git-common-dir"], capture_output=True, text=True, check=False)
        if res.returncode == 0:
            common_git = os.path.abspath(res.stdout.strip())
            main_worktree = os.path.dirname(common_git)
            main_env = os.path.join(main_worktree, ".env")
            if os.path.isfile(main_env):
                with open(main_env, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("#") or not line:
                            continue
                        if "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip('"').strip("'")
                            if k == "DISCORD_WEBHOOK_URL" and v:
                                return v
    except Exception:
        pass

    return None

def main():
    # Retrieve the Webhook URL from the environment variable or .env
    webhook_url = load_env_url()
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL environment variable is not set (and not found in .env).", file=sys.stderr)
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
