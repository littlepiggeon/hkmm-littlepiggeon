from typing import Optional, Tuple


OWNER_AND_REPO=...



def get_owner_and_repo(url: str) -> Optional[Tuple[str, str]]:
    """Get the owner and repo from the URL.

    Args:
        url (str): URL of the GitHub repository.

    Returns:
        Optional[Tuple[str, str]]: (owner, repo) if the URL is valid, None otherwise.
    """
    ...

def get_latest_release(owner: str, repo: str) -> dict | None:
    """Get the latest release version.

    Args:
        owner (str): Username or organization name.
        repo (str): Repository name.

    Returns:
        dict | None: Latest release data if successful, None otherwise.
    """
    ...

def get_latest_release_asset(owner: str, repo: str,name:str) -> str | None:
    """Get the latest release asset.

    Args:
        owner (str): Username or organization name.
        repo (str): Repository name.
        name (str): Asset name.

    Returns:
        str | None: The download URL of the asset if found, None otherwise.
    """
    ...