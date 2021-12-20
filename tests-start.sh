#! /usr/bin/env bash
set -e

if [ $(uname -s) = "Linux" ]; then
    echo "Remove __pycache__ files"
    sudo find . -type d -name __pycache__ -exec rm -r {} \+
fi

docker-compose down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error
docker-compose -f docker-compose.yml -f docker-compose.solodev.yml build
docker-compose -f docker-compose.yml -f docker-compose.solodev.yml up -d
#docker-compose exec coproduction pytest --cov=app --cov-report=term-missing app/tests
docker-compose exec coproduction pytest app/tests