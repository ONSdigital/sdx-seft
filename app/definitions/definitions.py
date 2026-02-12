from enum import StrEnum
from typing import TypedDict


class Metadata(TypedDict):
    tx_id: str
    survey_id: str
    period: str
    ru_ref: str
    ru_check: str
    filename: str


class SurveyType(StrEnum):
    SEFT = "seft"
    SEFT_RECEIPT = "seft_receipt"


class Context(TypedDict):
    survey_id: str
    period_id: str
    ru_ref: str
    tx_id: str
    survey_type: SurveyType
    context_type: str
