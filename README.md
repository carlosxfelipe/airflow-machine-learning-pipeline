# Airflow Machine Learning Pipeline

Este projeto implementa uma pipeline de machine learning usando Apache Airflow 3, realizando treinamento, avaliação de métricas e publicação em SQLite.

## Como rodar o projeto

1. Sincronize e instale as dependências usando o uv:

```bash
uv sync
```

2. Configure as variáveis de ambiente:

```bash
export AIRFLOW_HOME=$(pwd)
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags
```

3. Inicialize o banco de dados do Airflow:

```bash
uv run airflow db migrate
```

### Execução Direta (CLI)

Para rodar a DAG diretamente pelo terminal, sem a necessidade de iniciar o servidor web do Airflow ou criar um usuário:

```bash
uv run airflow dags test ml_pipeline
```

Ao final, os resultados serão salvos localmente na pasta `models/` e os metadados serão inseridos no banco SQLite `models_registry.db`.

### Execução via Interface Web (Browser)

Para acompanhar a execução pela interface do Airflow, é necessário criar um usuário de acesso:

1. Rode o script de configuração interativo (já existente na pasta) para gerar o acesso:
```bash
uv run python configurar_usuario.py
```

2. Inicie os serviços do Airflow:
```bash
uv run airflow standalone
```

3. Acesse `http://localhost:8080` no navegador, faça o login e execute a DAG `ml_pipeline`.

## O que este projeto realmente faz?

Se você está achando o pipeline confuso ou com pouca utilidade prática, é porque este projeto serve como uma **simulação puramente didática de MLOps (Machine Learning Operations)**. 

Em ambientes corporativos reais, cientistas de dados não treinam modelos "na mão". Eles criam "esteiras automatizadas" no Airflow para treinar modelos em horários agendados. A DAG (`ml_pipeline`) deste projeto faz exatamente essa simulação em 4 etapas:

1. **Geração e Treinamento (`train_model`):** Para não depender de bases de dados externas ou configurações complexas, o código utiliza a biblioteca `scikit-learn` para **inventar dados aleatórios (sintéticos)** do zero. Em seguida, ele treina um algoritmo clássico chamado **Regressão Logística** em cima desses dados falsos.
2. **Avaliação Fictícia (`evaluate_model`):** O modelo recém-criado tenta fazer previsões em cima de um pedaço dos dados sintéticos, e o sistema calcula sua "nota" (Acurácia e a área sob a curva ROC).
3. **Validação Automática (`select_best_model`):** O código age como um "inspetor de qualidade", conferindo automaticamente se a pontuação do modelo foi maior ou igual a **80%**. 
4. **Catálogo/Publicação (`publish_model`):** Se aprovado na etapa anterior, as informações do modelo são registradas no banco de dados local (`models_registry.db`).

**Conclusão:** O foco desse código não é a Inteligência Artificial em si, e sim **aprender a construir os canos que conectam as etapas**. O "treinamento" é apenas um modelo gerando números aleatórios para que a gente possa ver a engrenagem do Apache Airflow funcionando, simulando de forma fácil o que, no mundo real, seria um modelo complexo sendo validado e publicado em nuvem (S3/AWS).
