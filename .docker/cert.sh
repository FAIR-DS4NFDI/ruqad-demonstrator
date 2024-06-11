#!/bin/bash

# ** header v3.0
# This file is a part of the CaosDB Project.
#
# Copyright (C) 2019 Daniel Hornung, Göttingen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# ** end header


# Creates a directory `cert` and certificates in this directory.
#
# The hostname for which the certificate is created can be changed by setting
# the environment variable CAOSHOSTNAME.
#
# ## Overview of variables ##
#
# - CAOSHOSTNAME :: Hostname for the key (localhost)
# - KEYPW :: Password for the key (default ist CaosDBSecret)
# - KEYSTOREPW :: Password for the key store (same as KEYPW)
function cert() {
    mkdir -p cert
    cd cert
    KEYPW="${KEYPW:-CaosDBSecret}"
    CAOSHOSTNAME="${CAOSHOSTNAME:-localhost}"
    KEYSTOREPW="${KEYPW:-}"
    # NOTE: KEYPW and KEYSTOREPW are the same, due to Java limitations.
    KEYPW="${KEYPW}" openssl genrsa -aes256 -out caosdb.key.pem \
         -passout env:KEYPW 2048
    # Certificate is for localhost
    KEYPW="${KEYPW}" openssl req -new -x509 -key caosdb.key.pem \
         -out caosdb.cert.pem -passin env:KEYPW \
         -subj "/C=/ST=/L=/O=example/OU=example/CN=${CAOSHOSTNAME}" \
         -days 365 \
         -addext "subjectAltName = DNS:${CAOSHOSTNAME}" \
         -addext "certificatePolicies = 1.2.3.4"
    KEYPW="${KEYPW}" KEYSTOREPW="$KEYSTOREPW" openssl pkcs12 -export \
         -inkey caosdb.key.pem -in caosdb.cert.pem -out all-certs.pkcs12 \
         -passin env:KEYPW -passout env:KEYPW

    keytool -importkeystore -srckeystore all-certs.pkcs12 -srcstoretype PKCS12 \
            -deststoretype pkcs12 -destkeystore caosdb.jks \
            -srcstorepass "${KEYPW}" \
            -destkeypass "${KEYPW}" -deststorepass "$KEYSTOREPW"
    echo "Certificates successfuly created."
}

cert
