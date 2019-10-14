#!/bin/bash

export HEADLESS="true"

cd docker
docker-compose -f docker-compose.test.yml down --volumes
docker-compose -f docker-compose.test.yml build
docker-compose -f docker-compose.test.yml up -d --force-recreate

wait_output=$(docker wait docker_test_1)

docker-compose -f docker-compose.yml logs

retVal=$wait_output
echo "retVal:"
echo "$retVal"

if [ $retVal -ne 0 ]; then
    echo "itest failed"
else
    echo "itest passed"
fi
exit $retVal
