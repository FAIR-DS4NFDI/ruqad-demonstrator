FROM python:3.13

# development root: /ruqad
COPY ./src /ruqad/src
COPY ./unittests /ruqad/unittests
COPY ./end-to-end-tests /ruqad/end-to-end-tests
COPY ./pyproject.toml /ruqad/

# static configuration
COPY ./qualitycheck_config.toml /ruqad/
COPY ./pylinkahead.ini /ruqad/

# Installing the package
WORKDIR /ruqad/
# TODO Remove this manual crawler installation after the crawler has been released in version 0.10.2
RUN pip install --root-user-action=ignore \
  git+https://gitlab.indiscale.com/caosdb/src/caosdb-crawler.git@ruqad

RUN pip install --root-user-action=ignore .[all]

CMD rq_monitor
