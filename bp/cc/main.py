from fyers_login import get_fyers

def main():
    fyers = get_fyers()   # MUST return a valid object
    print("\n🚀 FYERS OBJECT READY")
    print(fyers.get_profile())

if __name__ == "__main__":
    main()
