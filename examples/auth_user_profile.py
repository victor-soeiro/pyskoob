"""Authenticate with Skoob and fetch the logged-in user profile.

Provide your ``PHPSESSID`` cookie in the ``session_token`` variable below
before running the script. It will authenticate the current session and
display basic information about the logged in user as a demonstration of
the authentication and user APIs.
"""

from pyskoob.client import SkoobClient


def main() -> None:
    """Login using a PHPSESSID cookie and show profile info."""
    # Replace with your PHPSESSID token obtained from browser cookies.
    session_token = "YOUR_PHPSESSID"

    with SkoobClient() as client:
        user = client.auth.login_with_cookies(session_token)
        print(f"Logged in as: {user.name} (id={user.id})")

        profile = client.users.get_by_id(user.id)
        print(f"Username: {profile.username}\nURL: {profile.profile_url}")


if __name__ == "__main__":
    main()
