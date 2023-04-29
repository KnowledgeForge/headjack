FROM python:3.10

WORKDIR /code
COPY . /code
RUN pip install -e .

CMD ["uvicorn", "headjack_server.api.app:app", "--host", "0.0.0.0", "--port", "16400"]
EXPOSE 8000
