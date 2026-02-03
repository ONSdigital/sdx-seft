from app import get_logger
from app.definitions.definitions import Metadata, SurveyType
from app.functions.datetime_function import get_current_datetime_in_dm
from app.functions.zip_function import create_zip
from app.services.deliver_service import DeliverService

logger = get_logger()

NO_RECEIPT_SEFT = ["141", "200"]


class ReceiptService:

    def __init__(self,
                 deliver_service: DeliverService,
                 ):
        self._deliver_service = deliver_service

    def process_receipt(self, meta_dict: Metadata):
        """
        Process the receipt for a SEFT submission.

        Steps:
        - Check if receipt is required for the survey ID
        - Extract RU check from filename
        - Generate the receipt content (Filename: REC<DDMM>_<TX_ID>.DAT)
        - Create a zip file containing the receipt (Filename: <TX_ID>_receipt)
        - Deliver the receipt via the delivery service
        """
        if meta_dict.get('survey_id') in NO_RECEIPT_SEFT:
            logger.info(f"No receipt required for survey {meta_dict.get('survey_id')}. Skipping receipt generation.")
            return

        receipt_filename = self._formulate_idbr_receipt_name(meta_dict['tx_id'])
        receipt_bytes = self._create_receipt_file(
            meta_dict['survey_id'],
            meta_dict['ru_ref'],
            meta_dict['ru_check'],
            meta_dict['period']
        )

        zip_receipt_file = create_zip([{receipt_filename, receipt_bytes}])
        zip_receipt_filename = self._formulate_zip_receipt_name(meta_dict['tx_id'])

        # Deliver the zipped SEFT receipt file
        self._deliver_service.deliver(SurveyType.SEFT_RECEIPT, meta_dict, zip_receipt_filename, zip_receipt_file)

        logger.info("SEFT receipt file process completed successfully")

    def _create_receipt_file(self, survey_id: str, ru_ref: str, ru_check: str, period: str) -> bytes:
        return bytes(self._format_idbr_receipt(survey_id, ru_ref, ru_check, period), "utf-8")

    def _formulate_zip_receipt_name(self, tx_id: str) -> str:
        return tx_id

    def _formulate_idbr_receipt_name(self, tx_id: str) -> str:
        dm = get_current_datetime_in_dm()
        return "REC{0}_{1}.DAT".format(dm, tx_id)

    def _format_idbr_receipt(self, survey_id: str, ru_ref: str, ru_check: str, period: str):
        """Format a receipt in IDBR format."""
        return "{0}:{1}:{2:03}:{3}".format(ru_ref, ru_check, int(survey_id), period)
