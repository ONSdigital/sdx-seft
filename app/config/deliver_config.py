from typing import TypedDict

from app.definitions.definitions import SurveyType


class DeliverConfigDetails(TypedDict):
    endpoint: str
    file_key: str


deliver_config: dict[SurveyType, DeliverConfigDetails] = {
    SurveyType.SEFT: {
        "endpoint": "deliver/v2/seft",
        "file_key": "seft_file"
    },
    SurveyType.SEFT_RECEIPT: {
        "endpoint": "deliver/v2/seft_receipt",
        "file_key": "zip_file"
    }
}
