# Airflow Machine Learning Pipeline

Este projeto implementa uma pipeline de machine learning usando Apache Airflow 3, realizando treinamento, avaliacao de metricas e publicacao em SQLite.

## Como rodar o projeto

1. Sincronize e instale as dependencias usando o uv:

```bash
uv sync
```

2. Configure as variaveis de ambiente:

```bash
export AIRFLOW_HOME=$(pwd)
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags
```

3. Inicialize o banco de dados do Airflow:

```bash
uv run airflow db migrate
```

### Execucao Direta (CLI)

Para rodar a DAG diretamente pelo terminal, sem a necessidade de iniciar o servidor web do Airflow ou criar um usuario:

```bash
uv run airflow dags test ml_pipeline
```

Ao final, os resultados serao salvos localmente na pasta `models/` e os metadados serao inseridos no banco SQLite `models_registry.db`.

### Execucao via Interface Web (Browser)

Para acompanhar a execucao pela interface do Airflow, e necessario criar um usuario de acesso:

1. Rode o script de configuracao interativo (ja existente na pasta) para gerar o acesso:
```bash
uv run python configurar_usuario.py
```

2. Inicie os servicos do Airflow:
```bash
uv run airflow standalone
```

3. Acesse `http://localhost:8080` no navegador, faca o login e execute a DAG `ml_pipeline`.
