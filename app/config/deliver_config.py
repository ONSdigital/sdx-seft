from typing import TypedDict

from app.definitions.definitions import SurveyType

deliver_config: TypedDict = {
    SurveyType.SEFT: {
        "endpoint": "deliver/v2/seft",
        "file_key": "seft_file"
    },
    SurveyType.SEFT_RECEIPT: {
        "endpoint": "deliver/v2/seft_receipt",
        "file_key": "zip_file"
    }
}
