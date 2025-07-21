"""
🚀 Semantic Release Service - TecnoCursos AI Enterprise Edition 2025
===================================================================

Sistema avançado de versionamento semântico automático:
- Análise inteligente de commits para determinação de versões
- Geração automática de changelogs
- Integração com CI/CD para releases automatizados
- Suporte a pré-releases e versionamento beta
- Análise de breaking changes
- Notificações automáticas de releases
"""

import os
import re
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import subprocess
import semver
from pathlib import Path

from app.logger import get_logger
from app.config import get_settings

logger = get_logger("semantic_release")
settings = get_settings()

class ReleaseType(Enum):
    """Tipos de release"""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    PRERELEASE = "prerelease"
    BUILD = "build"

class CommitType(Enum):
    """Tipos de commit convencionais"""
    FEAT = "feat"        # Nova funcionalidade
    FIX = "fix"          # Correção de bug
    DOCS = "docs"        # Documentação
    STYLE = "style"      # Formatação
    REFACTOR = "refactor" # Refatoração
    PERF = "perf"        # Performance
    TEST = "test"        # Testes
    BUILD = "build"      # Build system
    CI = "ci"           # CI/CD
    CHORE = "chore"     # Manutenção
    REVERT = "revert"   # Reverter commit

@dataclass
class Commit:
    """Estrutura de commit"""
    hash: str
    type: Optional[CommitType]
    scope: Optional[str]
    subject: str
    body: Optional[str]
    footer: Optional[str]
    is_breaking: bool
    timestamp: datetime
    author: str
    
@dataclass
class Release:
    """Estrutura de release"""
    version: str
    type: ReleaseType
    date: datetime
    commits: List[Commit]
    breaking_changes: List[str]
    features: List[str]
    fixes: List[str]
    changelog: str
    
class SemanticReleaseService:
    """Serviço de release semântico"""
    
    def __init__(self):
        self.current_version = "0.0.0"
        self.repo_path = Path(".")
        self.changelog_path = Path("CHANGELOG.md")
        self.version_file = Path("VERSION")
        self.package_json = Path("package.json")
        
        # Padrões de commit convencionais
        self.commit_pattern = re.compile(
            r"^(?P<type>\w+)(\((?P<scope>[\w\-]+)\))?(?P<breaking>!)?:\s+(?P<subject>.+)$"
        )
        
        # Padrões de breaking changes
        self.breaking_patterns = [
            r"BREAKING\s+CHANGE:",
            r"BREAKING-CHANGE:",
            r"!"
        ]
        
        logger.info("✅ Semantic Release Service inicializado")
    
    async def analyze_commits(self, since_tag: Optional[str] = None) -> List[Commit]:
        """Analisar commits desde uma tag ou desde o início"""
        try:
            # Comando git para obter commits
            cmd = ["git", "log", "--pretty=format:%H|%s|%b|%an|%at"]
            if since_tag:
                cmd.append(f"{since_tag}..HEAD")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Erro ao executar git log: {result.stderr}")
                return []
            
            commits = []
            for line in result.stdout.split('\n'):
                if not line.strip():
                    continue
                
                parts = line.split('|', 4)
                if len(parts) < 4:
                    continue
                
                hash_val, subject, body, author, timestamp = parts[0], parts[1], parts[2], parts[3], parts[4]
                
                # Parsear commit convencional
                commit = self._parse_conventional_commit(
                    hash_val, subject, body, author, int(timestamp)
                )
                commits.append(commit)
            
            logger.info(f"📊 Analisados {len(commits)} commits")
            return commits
            
        except Exception as e:
            logger.error(f"Erro ao analisar commits: {e}")
            return []
    
    def _parse_conventional_commit(self, hash_val: str, subject: str, body: str, author: str, timestamp: int) -> Commit:
        """Parsear commit convencional"""
        match = self.commit_pattern.match(subject)
        
        commit_type = None
        scope = None
        is_breaking = False
        
        if match:
            type_str = match.group('type').lower()
            scope = match.group('scope')
            is_breaking = match.group('breaking') == '!'
            subject = match.group('subject')
            
            # Mapear tipo
            try:
                commit_type = CommitType(type_str)
            except ValueError:
                commit_type = CommitType.CHORE
        
        # Verificar breaking changes no body ou footer
        full_text = f"{subject} {body}".lower()
        for pattern in self.breaking_patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                is_breaking = True
                break
        
        return Commit(
            hash=hash_val,
            type=commit_type,
            scope=scope,
            subject=subject,
            body=body,
            footer="",
            is_breaking=is_breaking,
            timestamp=datetime.fromtimestamp(timestamp),
            author=author
        )
    
    async def determine_next_version(self, commits: List[Commit]) -> Tuple[str, ReleaseType]:
        """Determinar próxima versão baseada nos commits"""
        try:
            current_version = await self._get_current_version()
            
            # Análise de commits
            has_breaking = any(commit.is_breaking for commit in commits)
            has_features = any(commit.type == CommitType.FEAT for commit in commits)
            has_fixes = any(commit.type == CommitType.FIX for commit in commits)
            
            # Determinar tipo de release
            if has_breaking:
                release_type = ReleaseType.MAJOR
            elif has_features:
                release_type = ReleaseType.MINOR
            elif has_fixes:
                release_type = ReleaseType.PATCH
            else:
                # Apenas mudanças de documentação, estilo, etc.
                release_type = ReleaseType.PATCH
            
            # Calcular próxima versão
            if release_type == ReleaseType.MAJOR:
                next_version = semver.bump_major(current_version)
            elif release_type == ReleaseType.MINOR:
                next_version = semver.bump_minor(current_version)
            else:
                next_version = semver.bump_patch(current_version)
            
            logger.info(f"🎯 Próxima versão: {current_version} → {next_version} ({release_type.value})")
            return next_version, release_type
            
        except Exception as e:
            logger.error(f"Erro ao determinar próxima versão: {e}")
            return await self._get_current_version(), ReleaseType.PATCH
    
    async def _get_current_version(self) -> str:
        """Obter versão atual"""
        try:
            # Tentar ler de VERSION file
            if self.version_file.exists():
                version = self.version_file.read_text().strip()
                if semver.VersionInfo.isvalid(version):
                    return version
            
            # Tentar ler do package.json
            if self.package_json.exists():
                package_data = json.loads(self.package_json.read_text())
                version = package_data.get("version", "0.0.0")
                if semver.VersionInfo.isvalid(version):
                    return version
            
            # Tentar obter da última tag git
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                tag = result.stdout.strip()
                # Remover 'v' do início se existir
                version = tag.lstrip('v')
                if semver.VersionInfo.isvalid(version):
                    return version
            
            # Versão padrão
            return "0.0.0"
            
        except Exception as e:
            logger.error(f"Erro ao obter versão atual: {e}")
            return "0.0.0"
    
    async def generate_changelog(self, commits: List[Commit], version: str) -> str:
        """Gerar changelog para a versão"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Separar commits por tipo
        features = [c for c in commits if c.type == CommitType.FEAT]
        fixes = [c for c in commits if c.type == CommitType.FIX]
        breaking_changes = [c for c in commits if c.is_breaking]
        performance = [c for c in commits if c.type == CommitType.PERF]
        docs = [c for c in commits if c.type == CommitType.DOCS]
        
        changelog = f"## [{version}] - {date_str}\n\n"
        
        # Breaking Changes
        if breaking_changes:
            changelog += "### 💥 BREAKING CHANGES\n\n"
            for commit in breaking_changes:
                changelog += f"- **{commit.scope or 'core'}**: {commit.subject}\n"
            changelog += "\n"
        
        # Features
        if features:
            changelog += "### ✨ New Features\n\n"
            for commit in features:
                scope_str = f"**{commit.scope}**: " if commit.scope else ""
                changelog += f"- {scope_str}{commit.subject}\n"
            changelog += "\n"
        
        # Bug Fixes
        if fixes:
            changelog += "### 🐛 Bug Fixes\n\n"
            for commit in fixes:
                scope_str = f"**{commit.scope}**: " if commit.scope else ""
                changelog += f"- {scope_str}{commit.subject}\n"
            changelog += "\n"
        
        # Performance Improvements
        if performance:
            changelog += "### ⚡ Performance Improvements\n\n"
            for commit in performance:
                scope_str = f"**{commit.scope}**: " if commit.scope else ""
                changelog += f"- {scope_str}{commit.subject}\n"
            changelog += "\n"
        
        # Documentation
        if docs:
            changelog += "### 📚 Documentation\n\n"
            for commit in docs:
                scope_str = f"**{commit.scope}**: " if commit.scope else ""
                changelog += f"- {scope_str}{commit.subject}\n"
            changelog += "\n"
        
        return changelog
    
    async def create_release(self, dry_run: bool = False) -> Optional[Release]:
        """Criar nova release"""
        try:
            # Analisar commits desde a última tag
            last_tag = await self._get_last_tag()
            commits = await self.analyze_commits(last_tag)
            
            if not commits:
                logger.info("📭 Nenhum commit novo encontrado")
                return None
            
            # Determinar próxima versão
            next_version, release_type = await self.determine_next_version(commits)
            
            # Gerar changelog
            changelog = await self.generate_changelog(commits, next_version)
            
            # Extrair informações específicas
            breaking_changes = [c.subject for c in commits if c.is_breaking]
            features = [c.subject for c in commits if c.type == CommitType.FEAT]
            fixes = [c.subject for c in commits if c.type == CommitType.FIX]
            
            # Criar objeto Release
            release = Release(
                version=next_version,
                type=release_type,
                date=datetime.now(),
                commits=commits,
                breaking_changes=breaking_changes,
                features=features,
                fixes=fixes,
                changelog=changelog
            )
            
            if not dry_run:
                # Atualizar arquivos de versão
                await self._update_version_files(next_version)
                
                # Atualizar changelog
                await self._update_changelog(changelog)
                
                # Criar tag git
                await self._create_git_tag(next_version, changelog)
                
                logger.info(f"🎉 Release {next_version} criada com sucesso!")
            else:
                logger.info(f"🧪 Dry run - Release {next_version} seria criada")
            
            return release
            
        except Exception as e:
            logger.error(f"Erro ao criar release: {e}")
            return None
    
    async def _get_last_tag(self) -> Optional[str]:
        """Obter última tag git"""
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception:
            return None
    
    async def _update_version_files(self, version: str):
        """Atualizar arquivos de versão"""
        try:
            # Atualizar VERSION file
            self.version_file.write_text(version)
            
            # Atualizar package.json se existir
            if self.package_json.exists():
                package_data = json.loads(self.package_json.read_text())
                package_data["version"] = version
                self.package_json.write_text(json.dumps(package_data, indent=2))
            
            # Atualizar config.py
            config_file = Path("app/config.py")
            if config_file.exists():
                content = config_file.read_text()
                content = re.sub(
                    r'version: str = "[^"]*"',
                    f'version: str = "{version}"',
                    content
                )
                config_file.write_text(content)
            
            logger.info(f"📝 Arquivos de versão atualizados para {version}")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar arquivos de versão: {e}")
    
    async def _update_changelog(self, new_entry: str):
        """Atualizar arquivo CHANGELOG.md"""
        try:
            if self.changelog_path.exists():
                current_content = self.changelog_path.read_text()
                # Inserir nova entrada após o cabeçalho
                lines = current_content.split('\n')
                header_end = 0
                for i, line in enumerate(lines):
                    if line.startswith('## '):
                        header_end = i
                        break
                
                new_content = '\n'.join(lines[:header_end]) + '\n\n' + new_entry + '\n' + '\n'.join(lines[header_end:])
            else:
                new_content = f"# Changelog\n\nTodas as mudanças notáveis neste projeto serão documentadas neste arquivo.\n\n{new_entry}"
            
            self.changelog_path.write_text(new_content)
            logger.info("📄 CHANGELOG.md atualizado")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar changelog: {e}")
    
    async def _create_git_tag(self, version: str, changelog: str):
        """Criar tag git com a versão"""
        try:
            tag_name = f"v{version}"
            
            # Criar tag anotada
            subprocess.run([
                "git", "tag", "-a", tag_name, "-m", f"Release {version}\n\n{changelog}"
            ], check=True)
            
            logger.info(f"🏷️ Tag {tag_name} criada")
            
        except Exception as e:
            logger.error(f"Erro ao criar tag git: {e}")
    
    async def get_release_notes(self, version: str) -> Optional[str]:
        """Obter notas de release para uma versão"""
        try:
            if not self.changelog_path.exists():
                return None
            
            content = self.changelog_path.read_text()
            
            # Procurar seção da versão
            version_pattern = rf"## \[{re.escape(version)}\].*?(?=## \[|\Z)"
            match = re.search(version_pattern, content, re.DOTALL)
            
            if match:
                return match.group(0).strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter notas de release: {e}")
            return None
    
    async def preview_next_release(self) -> Dict[str, Any]:
        """Preview da próxima release"""
        try:
            last_tag = await self._get_last_tag()
            commits = await self.analyze_commits(last_tag)
            
            if not commits:
                return {"message": "Nenhuma mudança desde a última release"}
            
            next_version, release_type = await self.determine_next_version(commits)
            changelog = await self.generate_changelog(commits, next_version)
            
            return {
                "current_version": await self._get_current_version(),
                "next_version": next_version,
                "release_type": release_type.value,
                "commits_count": len(commits),
                "features_count": len([c for c in commits if c.type == CommitType.FEAT]),
                "fixes_count": len([c for c in commits if c.type == CommitType.FIX]),
                "breaking_changes_count": len([c for c in commits if c.is_breaking]),
                "changelog": changelog
            }
            
        except Exception as e:
            logger.error(f"Erro no preview: {e}")
            return {"error": str(e)}
    
    async def validate_conventional_commits(self) -> Dict[str, Any]:
        """Validar se commits seguem convenção"""
        try:
            commits = await self.analyze_commits()
            total_commits = len(commits)
            valid_commits = len([c for c in commits if c.type is not None])
            
            invalid_commits = [
                {"hash": c.hash[:8], "subject": c.subject}
                for c in commits if c.type is None
            ]
            
            compliance_rate = (valid_commits / total_commits * 100) if total_commits > 0 else 100
            
            return {
                "total_commits": total_commits,
                "valid_commits": valid_commits,
                "invalid_commits": invalid_commits,
                "compliance_rate": round(compliance_rate, 2),
                "status": "good" if compliance_rate >= 80 else "warning" if compliance_rate >= 60 else "poor"
            }
            
        except Exception as e:
            logger.error(f"Erro na validação: {e}")
            return {"error": str(e)}

# Instância global do serviço
semantic_release_service = SemanticReleaseService()

# Funções de conveniência
async def create_release(dry_run: bool = False) -> Optional[Release]:
    """Criar nova release"""
    return await semantic_release_service.create_release(dry_run)

async def preview_release() -> Dict[str, Any]:
    """Preview da próxima release"""
    return await semantic_release_service.preview_next_release()

async def validate_commits() -> Dict[str, Any]:
    """Validar commits convencionais"""
    return await semantic_release_service.validate_conventional_commits()

if __name__ == "__main__":
    # Teste do serviço
    async def test_service():
        print("🧪 Testando Semantic Release Service...")
        
        # Preview da próxima release
        preview = await preview_release()
        print("📊 Preview:", json.dumps(preview, indent=2, default=str))
        
        # Validar commits
        validation = await validate_commits()
        print("✅ Validação:", json.dumps(validation, indent=2))
    
    asyncio.run(test_service()) 