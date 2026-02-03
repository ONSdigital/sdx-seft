from enum import StrEnum
from typing import TypedDict, NotRequired


class Metadata(TypedDict):
    tx_id: str
    survey_id: str
    period: str
    ru_ref: str
    ru_check: str
    filename: str


class ParsedFilename(TypedDict):
    ru_ref: str
    ru_check: str
    period: str
    survey_id: str


class SurveyType(StrEnum):
    SEFT = "seft"
    SEFT_RECEIPT = "seft_receipt"
