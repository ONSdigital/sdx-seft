# sdx-seft


![Version](https://ons-badges-752336435892.europe-west2.run.app/api/badge/custom?left=Python&right=3.13)


SDX-Seft service is responsible for SEFT submissions that are received from RAS-RM.

## Process

SEFT submissions are large, encrypted xml files that do not require any validation or transformation. RAS-RM put all SEFTs
within a `{proj_id}-seft-responses` GCP bucket in the ons-sdx project space (encrypted). A PubSub message is then sent notifying SDX-Seft of a new submission. 
The SEFT service reads from the bucket and sends the data to SDX-Deliver via HTTP <POST> request: `/deliver/seft`

## Getting Started

### Prerequisites

- Python 3.13
- UV (a command line tool for managing Python environments)
- make

### Installing Python 3.13

If you don't have Python 3.13 installed, you can install it via brew:

```bash
brew install python@3.13
```

### Install UV:
   - This project uses UV for dependency management. Ensure it is installed on your system.
   - If UV is not installed, you can install it using:
```bash

curl -LsSf https://astral.sh/uv/install.sh | sh

OR 

brew install uv
```
- Use the official UV installation guide for other installation methods: https://docs.astral.sh/uv/getting-started/installation/
- Verify the installation by using the following command:
```bash
uv --version
```

### Install dependencies

This command will install all the dependencies required for the project, including development dependencies:

```bash
uv sync
```

If you ever need to update the dependencies, you can run:

```bash
uv sync --upgrade
```

### Running tests
To run the tests, use the following command:

```bash
make test
```

### Running the service

```bash
make dev
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
    data : {
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
| QUARANTINE_SEFT_TOPIC_ID   | Topic name: `quarantine-seft-topic`




