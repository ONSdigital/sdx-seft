import base64
import datetime
import json

from sdx_base.models.pubsub import Message, Envelope

from app.definitions.definitions import SurveyType, Context
from app.functions.zip_function import create_zip

MOCK_RECEIPT_DATE = datetime.datetime(2023, 4, 20, 12, 0, 0, 0)


class TestDataContainer:
    tx_id: str
    ru_ref: str
    ru_check: str
    period: str
    survey_id: str

    def __init__(self, tx_id: str, ru_ref: str, ru_check: str, period: str, survey_id: str):
        self.tx_id = tx_id
        self.ru_ref = ru_ref
        self.ru_check = ru_check
        self.period = period
        self.survey_id = survey_id
        self.seft_filename = f"{self.ru_ref}{self.ru_check}_{self.period}_{self.survey_id}_{self.tx_id}.xlsx.gpg"
        self.receipt_date = MOCK_RECEIPT_DATE.strftime("%d%m")
        self.receipt_filename = f"REC{self.receipt_date}_{self.tx_id}.DAT"
        self.receipt_bytes = bytes(f"{self.ru_ref}:{self.ru_check}:{self.survey_id}:{self.period}", "utf-8")
        self.receipt_zip_bytes = create_zip({self.receipt_filename: self.receipt_bytes})

        self.seft_context: Context = {
            "survey_id": self.survey_id,
            "period_id": self.period,
            "ru_ref": self.ru_ref,
            "tx_id": self.tx_id,
            "survey_type": SurveyType.SEFT.value,
            "context_type": "business_survey"
        }

        self.receipt_context: Context = {
            "survey_id": self.survey_id,
            "period_id": self.period,
            "ru_ref": self.ru_ref,
            "tx_id": self.tx_id,
            "survey_type": SurveyType.SEFT_RECEIPT.value,
            "context_type": "business_survey"
        }

        self.payload = {
            "tx_id": self.tx_id,
            "filename": self.seft_filename
        }

        self.encrypted_payload = base64.b64encode(
            json.dumps(self.payload).encode("utf-8")
        )

        self.attributes = {"tx_id": self.tx_id}

        self.message: Message = {
            "attributes": self.attributes,
            "data": self.encrypted_payload.decode("utf-8"),
            "message_id": "test-id",
            "publish_time": MOCK_RECEIPT_DATE.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        }

        self.envelope: Envelope = { "message": self.message, "subscription": "test-subscription" }
