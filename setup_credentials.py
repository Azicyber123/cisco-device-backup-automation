import keyring
import getpass
import sys

def setup_credentials():
    print("=" * 55)
    print("   Cisco Backup Credential Setup")
    print("=" * 55)
    print()

    service_name = "cisco_backup"

    # Device Credentials
    print("Device Credentials (used for all Cisco devices)")
    username = input("Enter device username: ").strip()
    if not username:
        print("❌ Username cannot be empty!")
        sys.exit(1)
    
    password = getpass.getpass("Enter device password: ")
    if not password:
        print("❌ Password cannot be empty!")
        sys.exit(1)

    keyring.set_password(service_name, "device_username", username)
    keyring.set_password(service_name, "device_password", password)

    print("\n✅ Device credentials saved successfully.")

    # Email Credentials
    print("\n" + "-" * 40)
    print("Email Credentials (for notifications)")
    email_user = input("Enter sender email address: ").strip()
    if not email_user:
        print("❌ Email address cannot be empty!")
        sys.exit(1)

    email_password = getpass.getpass("Enter email password / App Password: ")
    if not email_password:
        print("❌ Email password cannot be empty!")
        sys.exit(1)

    keyring.set_password(service_name, "email_user", email_user)
    keyring.set_password(service_name, "email_password", email_password)

    print("\n✅ Email credentials saved successfully.")
    print()
    print("=" * 55)
    print("🎉 All credentials have been securely stored using keyring!")
    print("You can now run the backup scripts.")
    print("=" * 55)


if __name__ == "__main__":
    try:
        setup_credentials()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)