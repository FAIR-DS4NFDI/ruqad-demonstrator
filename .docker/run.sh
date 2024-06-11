#!/bin/sh

docker-compose -f tester.yml run tester
rv=$?
echo $rv > result
