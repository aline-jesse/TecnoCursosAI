# Script PowerShell para backup e restauração do banco MySQL 'tecnocursosai'
# Uso:
#   .\mysql_backup.ps1 -Mode backup -User root -Pass senha -Host localhost -Database tecnocursosai
#   .\mysql_backup.ps1 -Mode restore -User root -Pass senha -Host localhost -Database tecnocursosai -File backup.sql

param(
  [Parameter(Mandatory=$true)][ValidateSet('backup','restore')]$Mode,
  [Parameter(Mandatory=$true)][string]$User,
  [Parameter(Mandatory=$true)][string]$Pass,
  [string]$Host = 'localhost',
  [string]$Database = 'tecnocursosai',
  [string]$File
)

# Função para exibir uso
function Show-Usage {
  Write-Host "Uso: .\\mysql_backup.ps1 -Mode backup|restore -User <usuario> -Pass <senha> -Host <host> -Database <banco> [-File <arquivo.sql>]"
  Write-Host "Exemplo backup: .\\mysql_backup.ps1 -Mode backup -User root -Pass senha -Host localhost -Database tecnocursosai"
  Write-Host "Exemplo restore: .\\mysql_backup.ps1 -Mode restore -User root -Pass senha -Host localhost -Database tecnocursosai -File backup.sql"
  exit 1
}

if ($Mode -eq 'backup') {
  # Gera backup
  $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $backupFile = "${Database}_backup_${timestamp}.sql"
  Write-Host "Gerando backup do banco '$Database' em $backupFile..."
  & mysqldump -u $User -p$Pass -h $Host $Database > $backupFile
  if ($LASTEXITCODE -eq 0) {
    Write-Host "Backup concluído: $backupFile"
  } else {
    Write-Host "Erro ao gerar backup."
    exit 1
  }
} elseif ($Mode -eq 'restore') {
  if (-not $File) {
    Write-Host "Arquivo de backup não especificado."
    Show-Usage
  }
  Write-Host "Criando banco '$Database' se não existir..."
  & mysql -u $User -p$Pass -h $Host -e "CREATE DATABASE IF NOT EXISTS `$Database`;"
  Write-Host "Restaurando backup do arquivo $File para o banco '$Database'..."
  & mysql -u $User -p$Pass -h $Host $Database < $File
  if ($LASTEXITCODE -eq 0) {
    Write-Host "Restauração concluída."
  } else {
    Write-Host "Erro ao restaurar backup."
    exit 1
  }
} else {
  Show-Usage
}
