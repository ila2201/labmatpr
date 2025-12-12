#!/bin/bash
echo "Generating diagrams..."
# Команда запуска Structurizr (заглушка)
docker run -it --rm -p 8080:8080 -v $PWD:/usr/local/structurizr structurizr/lite

echo "Generating Server Code..."
# Команда генерации кода из методички
docker run --rm -v ${PWD}:/local openapitools/openapi-generator-cli generate -i /local/openapi.yaml -g python-flask -o /local/server_code