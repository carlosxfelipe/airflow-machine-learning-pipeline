#!/bin/bash

# Garante que o script roda a partir da pasta onde ele esta localizado
cd "$(dirname "$0")"

echo "Configurando as variaveis de ambiente do Airflow..."
export AIRFLOW_HOME=$(pwd)
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags

echo "Executando a DAG no terminal..."
uv run airflow dags test ml_pipeline
