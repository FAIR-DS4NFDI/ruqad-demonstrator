FROM debian:bookworm
RUN apt-get update && \
    apt-get install \
    curl \
    git \
    openjdk-17-jdk-headless \
    python3-autopep8 \
    python3-pip \
    python3-pytest \
    python3-sphinx \
    -y
RUN pip3 install --break-system-packages pylint recommonmark sphinx-rtd-theme tox
COPY .docker/wait-for-it.sh /wait-for-it.sh
ARG PYLIB
ADD https://gitlab.indiscale.com/api/v4/projects/97/repository/commits/${PYLIB} \
    pylib_version.json
RUN git clone https://gitlab.indiscale.com/caosdb/src/caosdb-pylib.git && \
    cd caosdb-pylib && git checkout ${PYLIB} && pip3 install --break-system-packages .
ARG ADVANCED
ADD https://gitlab.indiscale.com/api/v4/projects/104/repository/commits/${ADVANCED} \
    advanced_version.json
RUN git clone https://gitlab.indiscale.com/caosdb/src/caosdb-advanced-user-tools.git && \
    cd caosdb-advanced-user-tools && git checkout ${ADVANCED} && pip3 install --break-system-packages .[h5-crawler]
COPY . /git

# Delete .git because it is huge.
RUN rm -r /git/.git

RUN cd /git/ && pip3 install --break-system-packages .

WORKDIR /git/integrationtests
# wait for server,
CMD /wait-for-it.sh caosdb-server:10443 -t 500 -- \
    # ... install pycaosdb.ini the server-side scripts
    cp /git/.docker/sss_pycaosdb.ini /scripting/home/.pycaosdb.ini && \
    # ... and run tests
    pytest-3 .
