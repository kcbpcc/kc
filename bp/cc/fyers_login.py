import os
import json
from urllib.parse import urlparse, parse_qs
from fyers_apiv3 import fyersModel
from settings import APP_ID, SECRET_KEY, REDIRECT_URI, TOKEN_FILE


# ---------------- TOKEN HELPERS ----------------
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
        print("🗑️ Old token deleted")


# ---------------- AUTH CODE EXTRACTOR ----------------
def extract_auth_code(full_url: str) -> str:
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

    # ----------

