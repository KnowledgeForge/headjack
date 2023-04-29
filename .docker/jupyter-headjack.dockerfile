FROM jupyter/scipy-notebook

WORKDIR /code
COPY . /code
RUN pip install -e .

CMD ["start-notebook.sh"]
EXPOSE 8888
