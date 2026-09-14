import os
import json
import threading
import click
from flask import Flask, request, jsonify
import boto3
import mysql.connector
from mysql.connector import errorcode

app = Flask(__name__)

DB_SECRET_NAME = os.getenv("DB_SECRET_NAME")
AWS_REGION = os.getenv("AWS_REGION", "us-east-2")

_secret_cache = None
_secret_cache_lock = threading.Lock()

def _get_secret():
    global _secret_cache
    if _secret_cache is None:
        with _secret_cache_lock:
            if _secret_cache is None:
                client = boto3.client("secretsmanager", region_name=AWS_REGION)
                response = client.get_secret_value(SecretId=DB_SECRET_NAME)
                _secret_cache = json.loads(response["SecretString"])
    return _secret_cache

def _get_db_credentials():
    if DB_SECRET_NAME:
        secret = _get_secret()
        return {
            "host": secret.get("host", os.getenv("DB_HOST", "togglemaster-prd.cfsy8k6qapj0.us-east-2.rds.amazonaws.com")),
            "port": secret.get("port", os.getenv("DB_PORT", "3306")),
            "database": secret.get("dbname", os.getenv("DB_NAME", "togglemaster_prd")),
            "user": secret.get("username", os.getenv("DB_USER")),
            "password": secret["password"],
        }
    return {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT", "3306"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

def get_db_connection():
    credentials = _get_db_credentials()
    conn = mysql.connector.connect(
        host=credentials["host"],
        port=credentials["port"],
        database=credentials["database"],
        user=credentials["user"],
        password=credentials["password"]
    )
    return conn

def init_db():
    print("Tentando inicializar a tabela 'flags'...")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS flags (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                is_enabled BOOLEAN NOT NULL DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Tabela 'flags' inicializada com sucesso.")
    except mysql.connector.Error as e:
        print(f"Erro de conexão ao inicializar o banco de dados: {e}")
    except Exception as e:
        print(f"Um erro inesperado ocorreu durante a inicialização do DB: {e}")

@app.cli.command("init-db")
def init_db_command():
    init_db()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route('/flags', methods=['POST'])
def create_flag():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "O campo 'name' é obrigatório"}), 400

    name = data['name']
    is_enabled = data.get('is_enabled', False)

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO flags (name, is_enabled) VALUES (%s, %s)", (name, is_enabled))
        conn.commit()
    except mysql.connector.Error as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            return jsonify({"error": f"A flag '{name}' já existe"}), 409
        return jsonify({"error": "Erro interno no servidor ao criar a flag", "details": str(e)}), 500
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

    return jsonify({"message": f"Flag '{name}' criada com sucesso"}), 201

@app.route('/flags', methods=['GET'])
def get_flags():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT name, is_enabled FROM flags ORDER BY name")
        flags = cur.fetchall()
        for flag in flags:
            flag["is_enabled"] = bool(flag["is_enabled"])
    except Exception as e:
        return jsonify({"error": "Erro interno no servidor ao buscar as flags", "details": str(e)}), 500
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

    return jsonify(flags), 200

@app.route('/flags/<string:name>', methods=['GET'])
def get_flag_status(name):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT name, is_enabled FROM flags WHERE name = %s", (name,))
        flag = cur.fetchone()
        if flag:
            flag["is_enabled"] = bool(flag["is_enabled"])
    except Exception as e:
        return jsonify({"error": "Erro interno no servidor ao buscar a flag", "details": str(e)}), 500
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

    if flag:
        return jsonify(flag), 200
    return jsonify({"error": "Flag não encontrada"}), 404

@app.route('/flags/<string:name>', methods=['PUT'])
def update_flag(name):
    data = request.get_json()
    if data is None or 'is_enabled' not in data or not isinstance(data['is_enabled'], bool):
        return jsonify({"error": "O campo 'is_enabled' (booleano) é obrigatório"}), 400

    is_enabled = data['is_enabled']

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE flags SET is_enabled = %s WHERE name = %s", (is_enabled, name))

        if cur.rowcount == 0:
            return jsonify({"error": "Flag não encontrada"}), 404

        conn.commit()
    except Exception as e:
        return jsonify({"error": "Erro interno no servidor ao atualizar a flag", "details": str(e)}), 500
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

    return jsonify({"message": f"Flag '{name}' atualizada"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
