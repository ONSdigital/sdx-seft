FROM python:3.11-slim
COPY . /app
WORKDIR /app
EXPOSE 5000
RUN python -m pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile
CMD ["python", "./run.py"]
