FROM python:3.10

WORKDIR /code
COPY . /code
RUN pip install -e .

CMD ["headjack", "--port", "8679", "--log-config", "/code/log-config.ini"]
