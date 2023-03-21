FROM python:3.8-slim
COPY . /app
WORKDIR /app
ENV PORT 5000
RUN python -m pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile
CMD ["python", "./run.py"]
