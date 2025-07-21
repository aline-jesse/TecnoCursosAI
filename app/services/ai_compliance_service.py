"""
Sistema de Compliance e Auditoria para IA Responsável - TecnoCursos AI
=====================================================================

Sistema abrangente de compliance que garante:
- Conformidade com regulamentações (GDPR, LGPD, AI Act)
- Detecção e mitigação de bias
- Transparência e accountability
- Auditoria contínua de IA
- Relatórios de compliance
- Monitoramento ético

Autor: TecnoCursos AI Team
Data: 2024
"""

import json
import logging
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import numpy as np
from collections import defaultdict, Counter
import re
import uuid

# Configuração de logging
logger = logging.getLogger(__name__)

class ComplianceStandard(Enum):
    """Padrões de compliance suportados"""
    GDPR = "gdpr"           # General Data Protection Regulation
    LGPD = "lgpd"           # Lei Geral de Proteção de Dados
    AI_ACT = "ai_act"       # EU AI Act
    SOX = "sox"             # Sarbanes-Oxley Act
    HIPAA = "hipaa"         # Health Insurance Portability and Accountability Act
    ISO27001 = "iso27001"   # Information Security Management
    NIST = "nist"           # NIST AI Risk Management Framework

class BiasType(Enum):
    """Tipos de bias detectáveis"""
    DEMOGRAPHIC = "demographic"     # Viés demográfico
    SELECTION = "selection"         # Viés de seleção
    CONFIRMATION = "confirmation"   # Viés de confirmação
    ANCHORING = "anchoring"         # Viés de ancoragem
    AVAILABILITY = "availability"   # Viés de disponibilidade
    REPRESENTATION = "representation" # Viés de representação

class AuditEventType(Enum):
    """Tipos de eventos de auditoria"""
    AI_DECISION = "ai_decision"
    DATA_ACCESS = "data_access"
    MODEL_UPDATE = "model_update"
    BIAS_DETECTION = "bias_detection"
    COMPLIANCE_CHECK = "compliance_check"
    HUMAN_OVERRIDE = "human_override"
    PRIVACY_BREACH = "privacy_breach"
    SYSTEM_CHANGE = "system_change"

@dataclass
class BiasDetection:
    """Resultado de detecção de bias"""
    id: str
    timestamp: datetime
    bias_type: BiasType
    severity: float  # 0-1
    affected_groups: List[str]
    context: Dict[str, Any]
    mitigation_suggested: str
    status: str = "detected"  # detected, mitigated, accepted

@dataclass
class ComplianceCheck:
    """Resultado de verificação de compliance"""
    id: str
    timestamp: datetime
    standard: ComplianceStandard
    requirement: str
    status: str  # compliant, non_compliant, needs_review
    evidence: Dict[str, Any]
    findings: List[str]
    remediation_plan: Optional[str] = None

@dataclass
class AuditEvent:
    """Evento de auditoria"""
    id: str
    timestamp: datetime
    event_type: AuditEventType
    actor: str  # user_id ou system
    resource: str
    action: str
    details: Dict[str, Any]
    compliance_impact: Optional[str] = None
    risk_level: str = "low"

class AIComplianceService:
    """
    Serviço de Compliance e Auditoria para IA
    
    Funcionalidades:
    - Monitoramento contínuo de compliance
    - Detecção automática de bias
    - Auditoria de decisões de IA
    - Relatórios de transparência
    - Gestão de conformidade regulatória
    """
    
    def __init__(self):
        self.audit_log: List[AuditEvent] = []
        self.bias_detections: List[BiasDetection] = []
        self.compliance_checks: List[ComplianceCheck] = []
        
        # Configurações de compliance por padrão
        self.compliance_config: Dict[ComplianceStandard, Dict] = {
            ComplianceStandard.GDPR: {
                "data_retention_days": 365,
                "consent_required": True,
                "right_to_deletion": True,
                "data_portability": True,
                "privacy_by_design": True
            },
            ComplianceStandard.LGPD: {
                "data_retention_days": 365,
                "consent_required": True,
                "transparency_required": True,
                "data_minimization": True
            },
            ComplianceStandard.AI_ACT: {
                "high_risk_oversight": True,
                "transparency_requirements": True,
                "human_oversight": True,
                "accuracy_requirements": True,
                "robustness_testing": True
            }
        }
        
        # Palavras e padrões que podem indicar bias
        self.bias_patterns = {
            BiasType.DEMOGRAPHIC: [
                r'\b(homem|mulher|masculino|feminino)\b',
                r'\b(jovem|idoso|velho|novo)\b',
                r'\b(branco|negro|pardo|indígena)\b',
                r'\b(rico|pobre|classe\s+\w+)\b'
            ],
            BiasType.SELECTION: [
                r'\bselecionamos\s+apenas\b',
                r'\bpreferencialmente\b',
                r'\bexclusivamente\b'
            ]
        }
        
        # Métricas de compliance
        self.metrics: Dict[str, Any] = defaultdict(int)
        
        logger.info("✅ AI Compliance Service inicializado")
    
    async def audit_ai_decision(
        self,
        decision_id: str,
        decision_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> AuditEvent:
        """Audita uma decisão de IA"""
        
        audit_event = AuditEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type=AuditEventType.AI_DECISION,
            actor=user_id or "system",
            resource=f"ai_decision_{decision_id}",
            action="ai_decision_made",
            details=decision_data,
            risk_level=decision_data.get("risk_level", "low")
        )
        
        # Verificar compliance das decisões
        compliance_issues = await self._check_decision_compliance(decision_data)
        if compliance_issues:
            audit_event.compliance_impact = "potential_violation"
            audit_event.details["compliance_issues"] = compliance_issues
        
        # Detectar possível bias na decisão
        bias_detected = await self._detect_bias_in_decision(decision_data)
        if bias_detected:
            audit_event.details["bias_detected"] = bias_detected
        
        self.audit_log.append(audit_event)
        self.metrics["ai_decisions_audited"] += 1
        
        logger.info(f"Decisão de IA auditada: {decision_id}")
        return audit_event
    
    async def detect_bias(
        self,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> List[BiasDetection]:
        """Detecta bias em conteúdo"""
        
        detections = []
        metadata = metadata or {}
        
        # Detecção baseada em padrões
        for bias_type, patterns in self.bias_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    detection = BiasDetection(
                        id=str(uuid.uuid4()),
                        timestamp=datetime.now(),
                        bias_type=bias_type,
                        severity=len(matches) / len(content.split()) * 10,  # Simplicado
                        affected_groups=list(set(matches)),
                        context={
                            "content_length": len(content),
                            "matches": matches,
                            "pattern": pattern,
                            **metadata
                        },
                        mitigation_suggested=f"Revisar linguagem para {bias_type.value}"
                    )
                    detections.append(detection)
        
        # Detecção estatística (simulada)
        word_distribution = Counter(content.lower().split())
        
        # Verificar desequilíbrio de gênero
        male_terms = ["ele", "homem", "masculino", "pai", "filho"]
        female_terms = ["ela", "mulher", "feminino", "mãe", "filha"]
        
        male_count = sum(word_distribution.get(term, 0) for term in male_terms)
        female_count = sum(word_distribution.get(term, 0) for term in female_terms)
        
        if male_count > 0 or female_count > 0:
            total = male_count + female_count
            if total > 0:
                imbalance = abs(male_count - female_count) / total
                if imbalance > 0.7:  # 70% de desequilíbrio
                    detection = BiasDetection(
                        id=str(uuid.uuid4()),
                        timestamp=datetime.now(),
                        bias_type=BiasType.DEMOGRAPHIC,
                        severity=imbalance,
                        affected_groups=["gênero"],
                        context={
                            "male_count": male_count,
                            "female_count": female_count,
                            "imbalance_ratio": imbalance
                        },
                        mitigation_suggested="Balancear referências de gênero"
                    )
                    detections.append(detection)
        
        # Salvar detecções
        self.bias_detections.extend(detections)
        self.metrics["bias_detections"] += len(detections)
        
        return detections
    
    async def check_compliance(
        self,
        standard: ComplianceStandard,
        data: Dict[str, Any]
    ) -> ComplianceCheck:
        """Verifica compliance com padrão específico"""
        
        check_id = str(uuid.uuid4())
        findings = []
        status = "compliant"
        
        config = self.compliance_config.get(standard, {})
        
        if standard == ComplianceStandard.GDPR:
            findings = await self._check_gdpr_compliance(data, config)
        elif standard == ComplianceStandard.LGPD:
            findings = await self._check_lgpd_compliance(data, config)
        elif standard == ComplianceStandard.AI_ACT:
            findings = await self._check_ai_act_compliance(data, config)
        
        if findings:
            status = "non_compliant" if any("CRITICAL" in f for f in findings) else "needs_review"
        
        compliance_check = ComplianceCheck(
            id=check_id,
            timestamp=datetime.now(),
            standard=standard,
            requirement="automated_check",
            status=status,
            evidence=data,
            findings=findings,
            remediation_plan=self._generate_remediation_plan(findings) if findings else None
        )
        
        self.compliance_checks.append(compliance_check)
        self.metrics[f"compliance_checks_{standard.value}"] += 1
        
        logger.info(f"Compliance check realizado: {standard.value} - {status}")
        return compliance_check
    
    async def _check_gdpr_compliance(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> List[str]:
        """Verifica compliance com GDPR"""
        
        findings = []
        
        # Verificar consentimento
        if config.get("consent_required", True):
            if not data.get("user_consent", False):
                findings.append("CRITICAL: Falta consentimento do usuário para processamento de dados")
        
        # Verificar dados pessoais
        if data.get("contains_personal_data", False):
            if not data.get("lawful_basis"):
                findings.append("CRITICAL: Falta base legal para processamento de dados pessoais")
            
            if not data.get("data_protection_measures"):
                findings.append("WARNING: Faltam medidas de proteção de dados adequadas")
        
        # Verificar retenção de dados
        data_age = data.get("data_age_days", 0)
        max_retention = config.get("data_retention_days", 365)
        if data_age > max_retention:
            findings.append(f"WARNING: Dados retidos por {data_age} dias, limite é {max_retention}")
        
        # Verificar direitos do titular
        if data.get("contains_personal_data", False):
            if not data.get("deletion_capability", False):
                findings.append("WARNING: Sistema não suporta direito ao esquecimento")
            
            if not data.get("portability_capability", False):
                findings.append("INFO: Sistema não suporta portabilidade de dados")
        
        return findings
    
    async def _check_lgpd_compliance(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> List[str]:
        """Verifica compliance com LGPD"""
        
        findings = []
        
        # Verificar finalidade específica
        if not data.get("processing_purpose"):
            findings.append("CRITICAL: Falta finalidade específica para tratamento de dados")
        
        # Verificar minimização de dados
        if config.get("data_minimization", True):
            if data.get("excessive_data_collection", False):
                findings.append("WARNING: Possível coleta excessiva de dados")
        
        # Verificar transparência
        if config.get("transparency_required", True):
            if not data.get("privacy_policy_accessible", False):
                findings.append("WARNING: Política de privacidade não acessível")
        
        # Verificar segurança
        if not data.get("encryption_enabled", False):
            findings.append("WARNING: Dados não estão criptografados")
        
        return findings
    
    async def _check_ai_act_compliance(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> List[str]:
        """Verifica compliance com EU AI Act"""
        
        findings = []
        
        ai_system_risk = data.get("ai_risk_level", "low")
        
        if ai_system_risk in ["high", "critical"]:
            # Sistemas de alto risco requerem supervisão humana
            if config.get("high_risk_oversight", True):
                if not data.get("human_oversight_enabled", False):
                    findings.append("CRITICAL: Sistema de alto risco sem supervisão humana")
            
            # Requer documentação detalhada
            if not data.get("technical_documentation", False):
                findings.append("CRITICAL: Falta documentação técnica para sistema de alto risco")
            
            # Requer testes de robustez
            if config.get("robustness_testing", True):
                if not data.get("robustness_tested", False):
                    findings.append("WARNING: Sistema não foi testado para robustez")
        
        # Transparência para todos os sistemas
        if config.get("transparency_requirements", True):
            if not data.get("ai_disclosure", False):
                findings.append("WARNING: Usuários devem ser informados sobre uso de IA")
        
        # Verificar precisão
        if config.get("accuracy_requirements", True):
            accuracy = data.get("model_accuracy", 0)
            if accuracy < 0.8:  # 80% mínimo
                findings.append(f"WARNING: Precisão do modelo ({accuracy:.1%}) pode ser insuficiente")
        
        return findings
    
    def _generate_remediation_plan(self, findings: List[str]) -> str:
        """Gera plano de remediação baseado nos achados"""
        
        plans = []
        
        for finding in findings:
            if "consentimento" in finding.lower():
                plans.append("Implementar sistema de coleta de consentimento explícito")
            elif "base legal" in finding.lower():
                plans.append("Definir e documentar base legal para processamento")
            elif "supervisão humana" in finding.lower():
                plans.append("Implementar controles de supervisão humana")
            elif "criptografia" in finding.lower() or "criptografados" in finding.lower():
                plans.append("Implementar criptografia de dados em repouso e em trânsito")
            elif "documentação" in finding.lower():
                plans.append("Criar documentação técnica detalhada do sistema de IA")
            elif "transparência" in finding.lower():
                plans.append("Implementar notificações sobre uso de IA para usuários")
            elif "precisão" in finding.lower() or "accuracy" in finding.lower():
                plans.append("Melhorar treinamento do modelo ou implementar validação humana")
            else:
                plans.append("Revisar processo e implementar controles adequados")
        
        return "; ".join(set(plans))  # Remove duplicatas
    
    async def _check_decision_compliance(self, decision_data: Dict[str, Any]) -> List[str]:
        """Verifica compliance de uma decisão específica"""
        
        issues = []
        
        # Verificar se decisão afeta dados pessoais
        if decision_data.get("affects_personal_data", False):
            if not decision_data.get("user_consent", False):
                issues.append("Decisão afeta dados pessoais sem consentimento")
        
        # Verificar se há explicação para decisão automatizada
        if decision_data.get("automated_decision", False):
            if not decision_data.get("explanation_provided", False):
                issues.append("Decisão automatizada sem explicação adequada")
        
        # Verificar se há impacto significativo
        if decision_data.get("significant_impact", False):
            if not decision_data.get("human_review", False):
                issues.append("Decisão com impacto significativo sem revisão humana")
        
        return issues
    
    async def _detect_bias_in_decision(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta bias em decisões de IA"""
        
        bias_indicators = {}
        
        # Verificar desequilíbrio demográfico nas decisões
        demographics = decision_data.get("user_demographics", {})
        decision_outcome = decision_data.get("outcome", "")
        
        if demographics and decision_outcome:
            # Simplicado: verificar se certas demografias recebem tratamento diferente
            age_group = demographics.get("age_group", "")
            gender = demographics.get("gender", "")
            
            if age_group in ["young", "elderly"] and decision_outcome == "rejected":
                bias_indicators["age_bias"] = f"Possível viés etário: {age_group} rejeitado"
            
            if gender and decision_outcome == "rejected":
                bias_indicators["gender_bias"] = f"Verificar padrão de rejeição por gênero: {gender}"
        
        return bias_indicators
    
    # === MÉTODOS DE RELATÓRIOS ===
    
    def generate_compliance_report(
        self,
        standard: Optional[ComplianceStandard] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Gera relatório de compliance"""
        
        # Filtrar checks
        checks = self.compliance_checks
        if standard:
            checks = [c for c in checks if c.standard == standard]
        if start_date:
            checks = [c for c in checks if c.timestamp >= start_date]
        if end_date:
            checks = [c for c in checks if c.timestamp <= end_date]
        
        # Estatísticas
        total_checks = len(checks)
        compliant = len([c for c in checks if c.status == "compliant"])
        non_compliant = len([c for c in checks if c.status == "non_compliant"])
        needs_review = len([c for c in checks if c.status == "needs_review"])
        
        return {
            "report_generated": datetime.now().isoformat(),
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "standard": standard.value if standard else "all",
            "summary": {
                "total_checks": total_checks,
                "compliant": compliant,
                "non_compliant": non_compliant,
                "needs_review": needs_review,
                "compliance_rate": compliant / total_checks if total_checks > 0 else 0
            },
            "checks": [asdict(check) for check in checks[-50:]]  # Últimos 50
        }
    
    def generate_bias_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Gera relatório de bias"""
        
        # Filtrar detecções
        detections = self.bias_detections
        if start_date:
            detections = [d for d in detections if d.timestamp >= start_date]
        if end_date:
            detections = [d for d in detections if d.timestamp <= end_date]
        
        # Análise por tipo
        bias_by_type = defaultdict(list)
        for detection in detections:
            bias_by_type[detection.bias_type.value].append(detection.severity)
        
        type_analysis = {}
        for bias_type, severities in bias_by_type.items():
            type_analysis[bias_type] = {
                "count": len(severities),
                "avg_severity": sum(severities) / len(severities),
                "max_severity": max(severities),
                "min_severity": min(severities)
            }
        
        return {
            "report_generated": datetime.now().isoformat(),
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "summary": {
                "total_detections": len(detections),
                "unique_bias_types": len(bias_by_type),
                "avg_severity": sum(d.severity for d in detections) / len(detections) if detections else 0,
                "high_severity_count": len([d for d in detections if d.severity > 0.7])
            },
            "analysis_by_type": type_analysis,
            "recent_detections": [asdict(detection) for detection in detections[-20:]]
        }
    
    def generate_audit_report(
        self,
        event_type: Optional[AuditEventType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Gera relatório de auditoria"""
        
        # Filtrar eventos
        events = self.audit_log
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if start_date:
            events = [e for e in events if e.timestamp >= start_date]
        if end_date:
            events = [e for e in events if e.timestamp <= end_date]
        
        # Análise de riscos
        risk_distribution = Counter(event.risk_level for event in events)
        
        # Análise de atores
        actor_activity = Counter(event.actor for event in events)
        
        return {
            "report_generated": datetime.now().isoformat(),
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "event_type": event_type.value if event_type else "all",
            "summary": {
                "total_events": len(events),
                "unique_actors": len(actor_activity),
                "risk_distribution": dict(risk_distribution),
                "compliance_violations": len([e for e in events if e.compliance_impact])
            },
            "actor_activity": dict(actor_activity),
            "recent_events": [asdict(event) for event in events[-30:]]
        }
    
    def get_compliance_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de compliance"""
        return {
            **dict(self.metrics),
            "total_audit_events": len(self.audit_log),
            "total_bias_detections": len(self.bias_detections),
            "total_compliance_checks": len(self.compliance_checks),
            "compliance_standards_monitored": len(self.compliance_config)
        }

# === INSTÂNCIA GLOBAL ===
ai_compliance_service = AIComplianceService()

logger.info("✅ AI Compliance Service carregado com sucesso") 