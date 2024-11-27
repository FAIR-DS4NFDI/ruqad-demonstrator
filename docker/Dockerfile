FROM python:3.13

# development root: /ruqad
COPY ./src /ruqad/src
RUN ls -al /ruqad/
COPY ./unittests /ruqad/unittests
COPY ./end-to-end-tests /ruqad/end-to-end-tests
COPY ./pyproject.toml /ruqad/

# static configuration
COPY ./qualitycheck_config.toml /ruqad/
COPY ./pylinkahead.ini /ruqad/

# Installing the package
WORKDIR /ruqad/
RUN pip install --root-user-action=ignore .[all]

CMD rq_monitor
