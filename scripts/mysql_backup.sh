#!/bin/bash
# Script de backup e restauração do banco de dados MySQL 'tecnocursosai'
# Uso: ./mysql_backup.sh backup|restore [opções]
#
# backup: Gera um arquivo .sql de backup
# restore: Restaura o banco a partir de um arquivo .sql
#
# Exemplos:
#   ./mysql_backup.sh backup -u root -p senha -h localhost -d tecnocursosai
#   ./mysql_backup.sh restore -u root -p senha -h localhost -d tecnocursosai -f backup.sql

set -e

# Função para exibir uso
usage() {
  echo "Uso: $0 backup|restore [opções]"
  echo "\nOpções:"
  echo "  -u <usuario>     Usuário do MySQL"
  echo "  -p <senha>       Senha do MySQL"
  echo "  -h <host>        Host do MySQL (padrão: localhost)"
  echo "  -d <database>    Nome do banco (padrão: tecnocursosai)"
  echo "  -f <arquivo>     Arquivo .sql para restauração (apenas restore)"
  echo "\nExemplos:"
  echo "  $0 backup -u root -p senha -h localhost -d tecnocursosai"
  echo "  $0 restore -u root -p senha -h localhost -d tecnocursosai -f backup.sql"
  exit 1
}

# Valores padrão
HOST="localhost"
DATABASE="tecnocursosai"

# Parse de argumentos
MODE=$1
shift
while getopts "u:p:h:d:f:" opt; do
  case $opt in
    u) USER="$OPTARG" ;;
    p) PASS="$OPTARG" ;;
    h) HOST="$OPTARG" ;;
    d) DATABASE="$OPTARG" ;;
    f) FILE="$OPTARG" ;;
    *) usage ;;
  esac
done

if [ -z "$USER" ] || [ -z "$PASS" ]; then
  usage
fi

if [ "$MODE" = "backup" ]; then
  # Gera backup
  BACKUP_FILE="${DATABASE}_backup_$(date +%Y%m%d_%H%M%S).sql"
  echo "Gerando backup do banco '$DATABASE' em $BACKUP_FILE..."
  mysqldump -u "$USER" -p"$PASS" -h "$HOST" "$DATABASE" > "$BACKUP_FILE"
  echo "Backup concluído: $BACKUP_FILE"
elif [ "$MODE" = "restore" ]; then
  # Restaura backup
  if [ -z "$FILE" ]; then
    echo "Arquivo de backup não especificado."
    usage
  fi
  echo "Criando banco '$DATABASE' se não existir..."
  mysql -u "$USER" -p"$PASS" -h "$HOST" -e "CREATE DATABASE IF NOT EXISTS \\`$DATABASE\\`;"
  echo "Restaurando backup do arquivo $FILE para o banco '$DATABASE'..."
  mysql -u "$USER" -p"$PASS" -h "$HOST" "$DATABASE" < "$FILE"
  echo "Restauração concluída."
else
  usage
fi
