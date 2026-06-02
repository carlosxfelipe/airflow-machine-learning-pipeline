import json
import os
import getpass
import re
import subprocess

CFG_PATH = "airflow.cfg"
PASSWORDS_FILE = "simple_auth_manager_passwords.json.generated"


def garantir_airflow_cfg():
    """Garante que o airflow.cfg existe, rodando db migrate se necessário."""
    if not os.path.exists(CFG_PATH):
        print("Arquivo airflow.cfg não encontrado. Inicializando banco de dados...")
        subprocess.run(
            ["uv", "run", "airflow", "db", "migrate"],
            check=True,
            env={**os.environ, "AIRFLOW_HOME": os.getcwd()},
        )
        print("Banco de dados inicializado.\n")


def atualizar_airflow_cfg(usuario):
    """Atualiza o airflow.cfg com o usuário e role admin."""
    with open(CFG_PATH, "r") as f:
        content = f.read()

    new_line = f"simple_auth_manager_users = {usuario}:admin"
    pattern = r"simple_auth_manager_users\s*=\s*.*"

    if re.search(pattern, content):
        new_content = re.sub(pattern, new_line, content)
        with open(CFG_PATH, "w") as f:
            f.write(new_content)
        print(f"airflow.cfg atualizado: '{usuario}' definido como admin.")
    else:
        print("AVISO: Não encontrou simple_auth_manager_users no airflow.cfg.")


def salvar_senha(usuario, senha):
    """Salva apenas o usuário configurado, sem misturar com entradas antigas."""
    with open(PASSWORDS_FILE, "w") as f:
        json.dump({usuario: senha}, f)
    print(f"Arquivo de senhas criado para o usuário '{usuario}'.")


def configurar():
    print("\n--- Configuração de Usuário Airflow 3 ---\n")

    garantir_airflow_cfg()

    usuario = input("Nome de usuário [admin]: ").strip() or "admin"

    while True:
        senha = getpass.getpass(f"Senha para '{usuario}': ")
        if not senha:
            print("A senha não pode ser vazia.")
            continue
        confirmar = getpass.getpass("Confirme a senha: ")
        if senha == confirmar:
            break
        print("As senhas não coincidem. Tente novamente.")

    salvar_senha(usuario, senha)
    atualizar_airflow_cfg(usuario)

    print(f"\nPronto! Usuário '{usuario}' configurado com sucesso.")
    print("Agora rode:")
    print("  export AIRFLOW_HOME=$(pwd)")
    print("  export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags")
    print("  uv run airflow standalone")


if __name__ == "__main__":
    configurar()
