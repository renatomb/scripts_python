# Importar os módulos necessários
import sqlite3
import sys

# Verificar se os argumentos da linha de comando estão corretos
if len(sys.argv) != 3:
    print("Uso: python sqlite_to_mysql.py sqlite_file.sql mysql_file.sql")
    sys.exit(1)

# Conectar ao banco de dados sqlite
sqlite_file = sys.argv[1]
sqlite_conn = sqlite3.connect(sqlite_file)
sqlite_cursor = sqlite_conn.cursor()

# Obter os nomes das tabelas do banco de dados sqlite
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = sqlite_cursor.fetchall()

# Abrir o arquivo de saída mysql
mysql_file = sys.argv[2]
mysql_file = open(mysql_file, "w")

# Para cada tabela do banco de dados sqlite
for table in tables:
    # Obter o nome da tabela
    table_name = table[0]
    # Escrever o comando para criar a tabela no mysql
    mysql_file.write(f"DROP TABLE IF EXISTS {table_name};\n")
    mysql_file.write(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
    # Obter as colunas da tabela
    sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
    columns = sqlite_cursor.fetchall()
    # Para cada coluna da tabela
    for column in columns:
        # Obter o nome, o tipo e a restrição da coluna
        column_name = column[1]
        column_type = column[2]
        column_notnull = column[3]
        # Converter o tipo da coluna para o equivalente no mysql
        if column_type == "INTEGER":
            column_type = "INT"
        elif column_type == "REAL":
            column_type = "FLOAT"
        elif column_type == "TEXT":
            column_type = "VARCHAR(255)"
        elif column_type == "BLOB":
            column_type = "BLOB"
        # Converter a restrição da coluna para o equivalente no mysql
        if column_notnull == 1:
            column_notnull = "NOT NULL"
        else:
            column_notnull = ""
        # Escrever o comando para criar a coluna no mysql
        mysql_file.write(f"  {column_name} {column_type} {column_notnull},\n")
    # Remover a última vírgula
    mysql_file.seek(mysql_file.tell() - 2)
    # Escrever o comando para finalizar a criação da tabela no mysql
    mysql_file.write("\n);\n\n")
    # Obter os dados da tabela
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    data = sqlite_cursor.fetchall()
    # Para cada linha de dados da tabela
    for row in data:
        # Escrever o comando para inserir os dados no mysql
        mysql_file.write(f"INSERT INTO {table_name} VALUES (")
        # Para cada valor da linha
        for value in row:
            # Verificar se o valor é uma string
            if isinstance(value, str):
                # Escapar as aspas simples
                value = value.replace("'", "''")
                # Colocar o valor entre aspas simples
                value = f"'{value}'"
            # Escrever o valor no arquivo
            mysql_file.write(f"{value},")
        # Remover a última vírgula
        mysql_file.seek(mysql_file.tell() - 1)
        # Escrever o comando para finalizar a inserção dos dados no mysql
        mysql_file.write(");\n")
    # Escrever uma linha em branco
    mysql_file.write("\n")

# Fechar o arquivo de saída mysql
mysql_file.close()

# Fechar a conexão com o banco de dados sqlite
sqlite_conn.close()
