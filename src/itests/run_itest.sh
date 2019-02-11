#!/bin/bash

export HEADLESS = "true"

cd docker
docker-compose -f docker-compose.yml -f docker-compose.test.yml down
docker-compose -f docker-compose.yml -f docker-compose.test.yml build
docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d

wait_output=$(docker wait docker_test_1)

docker-compose -f docker-compose.yml -f docker-compose.test.yml logs

retVal=$wait_output
if [ $retVal -ne 0 ]; then
    echo "itest failed"
else
    echo "itest passed"
fi
exit $retVal
