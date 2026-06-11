"""
Generate a bcrypt password hash to insert into the dashboard_users table.

Usage:
    python make_password.py

You'll be prompted for the plaintext password. The script prints the hash —
copy it into your Supabase INSERT statement.

This script runs locally; the plaintext is never sent anywhere.
"""
import getpass
import bcrypt


def main():
    pw1 = getpass.getpass("Password: ")
    pw2 = getpass.getpass("Confirm:  ")

    if pw1 != pw2:
        print("Passwords do not match.")
        return
    if len(pw1) < 8:
        print("Password must be at least 8 characters.")
        return

    hashed = bcrypt.hashpw(pw1.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    print("\nPaste this into your Supabase INSERT statement:")
    print(hashed)


if __name__ == "__main__":
    main()
