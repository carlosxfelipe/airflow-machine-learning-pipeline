#!/bin/bash

# Garante que o script roda a partir da pasta onde ele esta localizado
cd "$(dirname "$0")"

echo "Configurando as variaveis de ambiente do Airflow..."
export AIRFLOW_HOME=$(pwd)
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags

# Garante que o banco de dados esta inicializado e atualizado
echo "Verificando banco de dados..."
uv run airflow db migrate

# Garante que existe o usuario padrao para login caso nao tenha sido configurado
PASSWORDS_FILE="simple_auth_manager_passwords.json.generated"
CFG_FILE="airflow.cfg"

if [ ! -f "$PASSWORDS_FILE" ] || [ ! -s "$PASSWORDS_FILE" ]; then
    echo "Criando usuario padrao..."
    echo '{"carlos": "admin"}' > "$PASSWORDS_FILE"
fi

# Configura o usuario carlos como admin no airflow.cfg
if grep -q "^simple_auth_manager_users =" "$CFG_FILE"; then
    # Se a linha ja existe, atualiza para garantir que a permissao esta correta
    sed -i 's/^simple_auth_manager_users =.*/simple_auth_manager_users = carlos:admin/' "$CFG_FILE"
else
    # Se nao existe ou esta comentada, adiciona/substitui
    if grep -q "simple_auth_manager_users =" "$CFG_FILE"; then
        sed -i 's/.*simple_auth_manager_users =.*/simple_auth_manager_users = carlos:admin/' "$CFG_FILE"
    else
        echo "simple_auth_manager_users = carlos:admin" >> "$CFG_FILE"
    fi
fi

echo "=================================================="
echo " Acesso a Interface Web do Airflow"
echo "=================================================="
echo " Endereco: http://localhost:8080"
echo " Usuario:  carlos"
echo " Senha:    admin"
echo "=================================================="
echo "Iniciando o servidor..."

uv run airflow standalone
