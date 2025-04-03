from typing import TypedDict, NotRequired


class Metadata(TypedDict):
    tx_id: str
    survey_id: str
    period: str
    ru_ref: str
    filename: str
    md5sum: NotRequired[str]
    sizeBytes: NotRequired[int]
