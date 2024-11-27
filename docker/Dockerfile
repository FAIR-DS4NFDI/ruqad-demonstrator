FROM python:3.13

# development root: /ruqad
COPY ./src /ruqad/src
RUN ls -al /ruqad/
COPY ./unittests /ruqad/unittests
COPY ./end-to-end-tests /ruqad/end-to-end-tests
COPY ./pyproject.toml /ruqad/
COPY ./qualitycheck_config.toml /ruqad/
WORKDIR /ruqad/
RUN pip install --root-user-action=ignore .
CMD rq_monitor
