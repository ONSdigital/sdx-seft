import re


def get_ru_check_from_filename(filename: str) -> str | None:
    """Extract the RU check characters from an incoming SEFT filename.

    Args:
        filename (str): The filename to extract from.

    Returns:
        str|None: The RU check characters if found, otherwise None.
    """
    # Filename like 90826421137T_202112_266_20220920110706.xlsx.gpg
    # Check letter return T
    pattern = r'^[0-9]{11}([A-Z0-9]{1})_[0-9]{6}_[0-9]{3}_.*'
    match = re.match(pattern, filename)
    if match:
        return match.group(1)
    return None
