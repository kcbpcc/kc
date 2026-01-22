import os
import json
from fyers_apiv3 import fyersModel
from settings import APP_ID, SECRET_KEY, REDIRECT_URI, TOKEN_FILE


def save_token(data):
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return None


def get_fyers():
    print("🔐 FYERS LOGIN")

    # ---------- TRY SAVED TOKEN ----------
    token_data = load_token()

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
            print("⚠ Saved token invalid, deleting token file")
            os.remove(TOKEN_FILE)

    # ---------- FRESH LOGIN ----------
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

    auth_code = input("\nPaste AUTH CODE ➜ ").strip()
    if not auth_code:
        raise RuntimeError("❌ Auth code not provided")

    session.set_token(auth_code)

    token_response = session.generate_token()
    if "access_token" not in token_response:
        raise RuntimeError(f"❌ Token generation failed: {token_response}")

    save_token(token_response)

    fyers = fyersModel.FyersModel(
        client_id=APP_ID,
        token=token_response["access_token"],
        log_path=""
    )

    profile = fyers.get_profile()
    if profile.get("code") != 200:
        raise RuntimeError(f"❌ Profile fetch failed: {profile}")

    print("✅ Login successful")
    print(f"👤 User: {profile['data']['name']}")

    return fyers

