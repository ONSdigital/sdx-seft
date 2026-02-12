import re

from app.definitions.definitions import Metadata


def parse_metadata_from_filename(filename: str) -> Metadata | None:
    """Extract the metadata from an incoming SEFT filename.

    Args:
        filename (str): The filename to extract from.

    Returns:
        Metadata|None: The metadata if found, otherwise None.

    Example:
        Input: Filename 90826421137T_202112_266_20220920110706.xlsx.gpg
        Output: ru_ref: 90826421137
                ru_check: T
                period: 202112
                survey_id: 266
                tx_id: 20220920110706
    """
    pattern = r'^([0-9]{11})([A-Z0-9]{1})_([0-9]{6})_([0-9]{3})_([0-9]{14}).xlsx.*'
    match = re.match(pattern, filename)
    if not match:
        return None

    meta_dict: Metadata = {
        "ru_ref": match.group(1),
        "ru_check": match.group(2),
        "period": match.group(3),
        "survey_id": match.group(4),
        "tx_id": match.group(5),
        "filename": filename
    }

    return meta_dict
