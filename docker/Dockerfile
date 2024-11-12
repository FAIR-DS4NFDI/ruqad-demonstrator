FROM python:3.13

RUN pip install pytest autopep8 pylint
COPY ./src /ruqad/src
COPY ./unittests /ruqad/unittests
COPY ./end-to-end-tests /ruqad/end-to-end-tests
COPY ./pyproject.toml /ruqad/
RUN cd /ruqad && pip install .
CMD python -m ruqad.monitor
