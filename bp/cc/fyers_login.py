import os
import json
from urllib.parse import urlparse, parse_qs
from fyers_apiv3 import fyersModel
from settings import APP_ID, SECRET_KEY, REDIRECT_URI, TOKEN_FILE


# ---------------- TOKEN FILE HELPERS ----------------
def save_token(data):
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return None


def delete_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        print("🗑️ Old token removed")


# ---------------- URL PARSER ----------------
def extract_auth_code(full_url: str) -> str:
    """
    Extract auth_code from full redirect URL
    """
    parsed = urlparse(full_url)
    qs = parse_qs(parsed.query)

    if "auth_code" not in qs:
        raise ValueError("❌ auth_code not found in URL")

    return qs["auth_code"][0]


# ---------------- MAIN LOGIN ----------------
def get_fyers():
    print("🔐 FYERS LOGIN")

    token_data = load_token()

    # ---------- TRY EXISTING TOKEN ----------
    if token_data and "access_token" in token_data:
        fyers = fyersModel.FyersModel(
            client_id=APP_ID,
            token=token_data["access_token"],
            log_path=""
        )

        profile = fyers.get_profile()
        if profile.get("code") == 200:
            print("✅ Using saved token")
            print(f"👤 User: {profile['data']['name']}")
            return fyers
        else:
            print("⚠ Saved token invalid")
            delete_token()

    # ---------- NEW LOGIN ----------
    session = fyersModel.SessionModel(
        client_id=APP_ID,
        secret_key=SECRET_KEY,
        redirect_uri=REDIRECT_URI,
        response_type="code",
        grant_type="authorization_code"
    )

    auth_url = session.generate_authcode()
    print("\n🌐 Open this URL in browser:\n")
    print(auth_url)

    print("\n📌 After login, paste FULL redirect URL here:")
    full_url = input("REDIRECT URL ➜ ").strip()

    auth_code = extract_auth_code(full_url)
    session.set_token(auth_code)

    token_response = session.generate_token()

    if "access_token" not in token_response:
        raise Exception(f"❌ Token generation failed: {token_response}")

    save_token(token_response)

    fyers = fyersModel.FyersModel(
        client_id=APP_ID,
        token=token_response["access_token"],
        log_path=""
    )

    profile = fyers.get_profile()
    print("✅ Login successful")
    print(f"👤 User: {profile['data']['name']}")

    return fyers
