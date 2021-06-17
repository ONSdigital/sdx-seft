# sdx-seft


[![Build Status](https://github.com/ONSdigital/sdx-seft/workflows/Build/badge.svg)](https://github.com/ONSdigital/sdx-seft) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/0d8f1899b0054322b9d0ec8f2bd62d86)](https://www.codacy.com/app/ons-sdc/sdx-seft?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ONSdigital/sdx-seft&amp;utm_campaign=Badge_Grade)

SDX-Seft service is responsible for SEFT submissions that are received from RAS-RM.

## Process

SEFT submissions are large, encrypted xml files that do not require any validation or transformation. RAS-RM put all SEFTs
within a `{proj_id}-seft-responses` GCP bucket in the ons-sdx project space (encrypted). A PubSub message is then sent notifying SDX-Seft of a new submission. 
The SEFT service reads from the bucket and sends the data to SDX-Deliver via HTTP <POST> request: `/deliver/seft`

## Getting started
Install pipenv:
```shell
$ pip install pipenv
```

Create a virtualenv and install dependencies
```shell
$ make build
```

Testing:
Install all test requirements and run tests:
```shell
$ make test
```

Running:
ensure you have installed all requirements with above `make build` command then:
```shell
$ make start
```

## GCP

#### Pubsub

SDX-Seft receives message from `seft-subscription`. This message contains only metadata about
the seft submission.

**Message Structure Example**
```python
    Message {
      data: b'{"filename": "11110000014H_202009_057_202101211435...'
      ordering_key: ''
      attributes: {
        "tx_id": "a288d481-52e8-4bc6-9265-9d93029239ed"
      }
    }
```

**Message Data field Example**
```python
    Data : {
        'filename': '11110000014H_202009_057_20210121143526',
        'md5sum': '12345',
        'period': '202009',
        'ru_ref': '20210121143526',
        'sizeBytes': 42,
        'survey_id': '057',
        'tx_id': 'd8cfc292-90bc-4e2f-8cf9-3e5d5da5a1ff'
    }
```

#### Bucket
SEFT submissions are too large to be sent via pubsub message. Therefore RAS-RM put submissions
into a `{proj_id}-seft-responses` bucket within the SDX gcp project, under their tx_id. SDX-Seft
uses the tx_id within the PubSub message to read the right data.

## Configuration

| Environment Variable       | Description
|----------------------------|------------------------------------
| PROJECT_ID                 | Name of project
| DELIVER_SERVICE_URL        | sdx-deliver URL `sdx-deliver:80`
| BUCKET_NAME                | Name of the bucket: `{project_id}-seft-responses`
| BUCKET                     | Bucket client object
| SEFT_SUBSCRIPTION_ID       | Subscription name: `seft-subscription`
| SEFT_SUBSCRIBER            | Subscriber object
| QUARANTINE_SEFT_TOPIC_ID   | Topic name: `quarantine-seft-topic`
| QUARANTINE_SEFT_PUBLISHER  | Quarantine publisher object

## License

Copyright © 2016, Office for National Statistics (https://www.ons.gov.uk)

Released under MIT license, see [LICENSE](LICENSE) for details.


