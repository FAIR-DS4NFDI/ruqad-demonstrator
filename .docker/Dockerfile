FROM debian:bookworm
RUN apt-get update && \
    apt-get install \
    curl \
    git \
    openjdk-17-jdk-headless \
    python3-pip \
    -y

COPY .docker/wait-for-it.sh /wait-for-it.sh
ARG PYLIB
ARG ADVANCED
# Version files
ADD https://gitlab.indiscale.com/api/v4/projects/97/repository/commits/${PYLIB} \
    pylib_version.json
ADD https://gitlab.indiscale.com/api/v4/projects/104/repository/commits/${ADVANCED} \
  advanced_version.json
# Install pylib and advanced user tools
RUN pip install --break-system-packages -U \
  git+https://gitlab.indiscale.com/caosdb/src/caosdb-pylib.git@${PYLIB} \
  git+https://gitlab.indiscale.com/caosdb/src/caosdb-advanced-user-tools.git@${ADVANCED}

# Install Ruqad
COPY . /git
RUN rm -r /git/.git
RUN cd /git/ && pip3 install --break-system-packages .[all]

WORKDIR /git/integrationtests
# wait for server,
CMD /wait-for-it.sh caosdb-server:10443 -t 120 --strict -- \
    # ... install pycaosdb.ini the server-side scripts
    cp /git/.docker/sss_pylinkahead.ini /scripting/home/.pylinkahead.ini && \
    # ... and run tests
    pytest-3 .
