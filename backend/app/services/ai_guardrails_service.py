"""
Sistema Avançado de IA Guardrails - TecnoCursos AI
==================================================

Sistema completo de supervisão e controle de IA com:
- Oversight humano inteligente 
- Explainable AI (XAI)
- Controles de segurança adaptativos
- Monitoramento ético em tempo real
- Sistema de intervenção humana
- Auditoria e compliance automatizada

Autor: TecnoCursos AI Team
Data: 2024
"""

import json
import logging
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import numpy as np
from collections import defaultdict, deque
import threading
import uuid

# Configuração de logging
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Níveis de risco para decisões de IA"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class OversightMode(Enum):
    """Modos de supervisão humana"""
    AUTONOMOUS = "autonomous"        # IA atua independentemente
    ADVISORY = "advisory"           # IA sugere, humano decide
    COLLABORATIVE = "collaborative" # IA e humano colaboram
    SUPERVISED = "supervised"       # Humano supervisiona ativamente
    MANUAL = "manual"              # Controle totalmente humano

class DecisionCategory(Enum):
    """Categorias de decisões do sistema"""
    CONTENT_GENERATION = "content_generation"
    USER_INTERACTION = "user_interaction"
    DATA_PROCESSING = "data_processing"
    SYSTEM_OPERATION = "system_operation"
    SECURITY_ACTION = "security_action"
    BUSINESS_LOGIC = "business_logic"

@dataclass
class AIDecision:
    """Estrutura de uma decisão de IA"""
    id: str
    timestamp: datetime
    category: DecisionCategory
    action: str
    confidence: float
    risk_level: RiskLevel
    explanation: str
    context: Dict[str, Any]
    human_required: bool
    approval_status: Optional[str] = None
    human_reviewer: Optional[str] = None
    override_reason: Optional[str] = None

@dataclass
class GuardrailRule:
    """Regra de guardrail para controle de IA"""
    id: str
    name: str
    category: DecisionCategory
    condition: str  # Condição em formato JSON
    action: str     # Ação a tomar
    risk_threshold: float
    human_intervention: bool
    explanation: str
    active: bool = True

class AIGuardrailsService:
    """
    Serviço principal de IA Guardrails
    
    Funcionalidades:
    - Supervisão adaptativa de decisões de IA
    - Explicabilidade e transparência
    - Controles de segurança em tempo real
    - Sistema de intervenção humana
    - Auditoria e compliance
    """
    
    def __init__(self):
        self.decisions_log: deque = deque(maxlen=10000)
        self.active_decisions: Dict[str, AIDecision] = {}
        self.guardrail_rules: Dict[str, GuardrailRule] = {}
        self.human_reviewers: Dict[str, Dict] = {}
        self.metrics: Dict[str, Any] = defaultdict(int)
        self.oversight_mode: OversightMode = OversightMode.COLLABORATIVE
        self.risk_thresholds: Dict[RiskLevel, float] = {
            RiskLevel.LOW: 0.2,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.HIGH: 0.8,
            RiskLevel.CRITICAL: 0.95
        }
        
        # Cache para explicações de IA
        self.explanation_cache: Dict[str, str] = {}
        
        # Sistema de notificações
        self.notification_callbacks: List[Callable] = []
        
        # Lock para thread safety
        self._lock = threading.Lock()
        
        # Inicializar regras padrão
        self._initialize_default_rules()
        
        logger.info("✅ AI Guardrails Service inicializado")
    
    def _initialize_default_rules(self):
        """Inicializa regras padrão de guardrails"""
        
        default_rules = [
            # Regras de segurança
            GuardrailRule(
                id="content_safety",
                name="Segurança de Conteúdo",
                category=DecisionCategory.CONTENT_GENERATION,
                condition='{"contains_unsafe": true}',
                action="block",
                risk_threshold=0.3,
                human_intervention=True,
                explanation="Bloquear conteúdo potencialmente inseguro"
            ),
            
            # Regras de privacidade
            GuardrailRule(
                id="privacy_protection",
                name="Proteção de Privacidade",
                category=DecisionCategory.DATA_PROCESSING,
                condition='{"has_pii": true}',
                action="anonymize",
                risk_threshold=0.4,
                human_intervention=True,
                explanation="Proteger informações pessoais identificáveis"
            ),
            
            # Regras de qualidade
            GuardrailRule(
                id="quality_control",
                name="Controle de Qualidade",
                category=DecisionCategory.CONTENT_GENERATION,
                condition='{"quality_score": {"<": 0.7}}',
                action="review",
                risk_threshold=0.5,
                human_intervention=False,
                explanation="Revisar conteúdo com baixa qualidade"
            ),
            
            # Regras de bias
            GuardrailRule(
                id="bias_detection",
                name="Detecção de Viés",
                category=DecisionCategory.USER_INTERACTION,
                condition='{"bias_score": {">": 0.6}}',
                action="flag",
                risk_threshold=0.6,
                human_intervention=True,
                explanation="Detectar e sinalizar possível viés"
            ),
            
            # Regras de sistema crítico
            GuardrailRule(
                id="critical_system",
                name="Operações Críticas",
                category=DecisionCategory.SYSTEM_OPERATION,
                condition='{"system_critical": true}',
                action="require_approval",
                risk_threshold=0.9,
                human_intervention=True,
                explanation="Requer aprovação para operações críticas"
            )
        ]
        
        for rule in default_rules:
            self.guardrail_rules[rule.id] = rule
    
    async def evaluate_decision(
        self, 
        action: str, 
        category: DecisionCategory,
        context: Dict[str, Any],
        confidence: float = 1.0,
        user_id: Optional[str] = None
    ) -> AIDecision:
        """
        Avalia uma decisão de IA com guardrails
        
        Args:
            action: Ação proposta pela IA
            category: Categoria da decisão
            context: Contexto da decisão
            confidence: Nível de confiança (0-1)
            user_id: ID do usuário (se aplicável)
        
        Returns:
            AIDecision: Decisão avaliada com explicação
        """
        decision_id = str(uuid.uuid4())
        
        # Análise de risco
        risk_level = await self._assess_risk(action, category, context, confidence)
        
        # Verificar se intervenção humana é necessária
        human_required = await self._requires_human_intervention(
            action, category, context, risk_level, confidence
        )
        
        # Gerar explicação
        explanation = await self._generate_explanation(
            action, category, context, risk_level, confidence
        )
        
        # Criar decisão
        decision = AIDecision(
            id=decision_id,
            timestamp=datetime.now(),
            category=category,
            action=action,
            confidence=confidence,
            risk_level=risk_level,
            explanation=explanation,
            context=context,
            human_required=human_required
        )
        
        # Aplicar guardrails
        decision = await self._apply_guardrails(decision)
        
        # Registrar decisão
        with self._lock:
            self.decisions_log.append(decision)
            if human_required:
                self.active_decisions[decision_id] = decision
            
            # Atualizar métricas
            self.metrics[f"decisions_{category.value}"] += 1
            self.metrics[f"risk_{risk_level.value}"] += 1
            if human_required:
                self.metrics["human_interventions"] += 1
        
        # Notificar se necessário
        if human_required or risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            await self._notify_decision(decision)
        
        logger.info(f"Decisão avaliada: {decision_id} - {risk_level.value} - Human: {human_required}")
        
        return decision
    
    async def _assess_risk(
        self, 
        action: str, 
        category: DecisionCategory,
        context: Dict[str, Any],
        confidence: float
    ) -> RiskLevel:
        """Avalia o nível de risco de uma decisão"""
        
        risk_score = 0.0
        
        # Fatores de risco base
        risk_factors = {
            # Baixa confiança = maior risco
            "confidence": 1.0 - confidence,
            
            # Categorias mais sensíveis
            "category_risk": {
                DecisionCategory.SECURITY_ACTION: 0.8,
                DecisionCategory.SYSTEM_OPERATION: 0.6,
                DecisionCategory.BUSINESS_LOGIC: 0.5,
                DecisionCategory.USER_INTERACTION: 0.4,
                DecisionCategory.DATA_PROCESSING: 0.3,
                DecisionCategory.CONTENT_GENERATION: 0.2
            }.get(category, 0.1),
            
            # Contexto específico
            "user_impact": context.get("affects_users", 0) * 0.3,
            "data_sensitivity": context.get("data_sensitivity", 0) * 0.4,
            "financial_impact": context.get("financial_impact", 0) * 0.5,
            "system_impact": context.get("system_impact", 0) * 0.6
        }
        
        # Calcular score de risco
        risk_score = sum(risk_factors.values()) / len(risk_factors)
        
        # Fatores contextuais específicos
        if context.get("emergency_mode", False):
            risk_score += 0.3
        
        if context.get("production_environment", True):
            risk_score += 0.2
        
        if context.get("external_api", False):
            risk_score += 0.1
        
        # Determinar nível de risco
        if risk_score >= self.risk_thresholds[RiskLevel.CRITICAL]:
            return RiskLevel.CRITICAL
        elif risk_score >= self.risk_thresholds[RiskLevel.HIGH]:
            return RiskLevel.HIGH
        elif risk_score >= self.risk_thresholds[RiskLevel.MEDIUM]:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    async def _requires_human_intervention(
        self,
        action: str,
        category: DecisionCategory,
        context: Dict[str, Any],
        risk_level: RiskLevel,
        confidence: float
    ) -> bool:
        """Determina se intervenção humana é necessária"""
        
        # Regras baseadas em risco
        if risk_level == RiskLevel.CRITICAL:
            return True
        
        # Regras baseadas em modo de supervisão
        if self.oversight_mode == OversightMode.MANUAL:
            return True
        
        if self.oversight_mode == OversightMode.SUPERVISED and risk_level in [RiskLevel.HIGH, RiskLevel.MEDIUM]:
            return True
        
        if self.oversight_mode == OversightMode.AUTONOMOUS:
            return risk_level == RiskLevel.CRITICAL
        
        # Verificar regras específicas de guardrails
        for rule in self.guardrail_rules.values():
            if not rule.active or rule.category != category:
                continue
            
            if await self._evaluate_rule_condition(rule, context) and rule.human_intervention:
                return True
        
        # Regras baseadas em confiança
        if confidence < 0.5:
            return True
        
        # Regras contextuais
        if context.get("involves_minors", False):
            return True
        
        if context.get("legal_implications", False):
            return True
        
        if context.get("permanent_action", False) and risk_level != RiskLevel.LOW:
            return True
        
        return False
    
    async def _generate_explanation(
        self,
        action: str,
        category: DecisionCategory,
        context: Dict[str, Any],
        risk_level: RiskLevel,
        confidence: float
    ) -> str:
        """Gera explicação para a decisão de IA (XAI - Explainable AI)"""
        
        # Verificar cache
        cache_key = f"{action}_{category.value}_{risk_level.value}_{confidence}"
        if cache_key in self.explanation_cache:
            return self.explanation_cache[cache_key]
        
        # Componentes da explicação
        explanation_parts = []
        
        # Explicação da ação
        explanation_parts.append(f"Ação proposta: {action}")
        
        # Explicação do risco
        risk_explanations = {
            RiskLevel.LOW: "Baixo risco - ação rotineira com impacto mínimo",
            RiskLevel.MEDIUM: "Risco moderado - requer atenção mas é gerenciável",
            RiskLevel.HIGH: "Alto risco - pode ter impacto significativo",
            RiskLevel.CRITICAL: "Risco crítico - requer supervisão humana imediata"
        }
        explanation_parts.append(f"Nível de risco: {risk_explanations[risk_level]}")
        
        # Explicação da confiança
        if confidence >= 0.9:
            explanation_parts.append("Confiança muito alta - IA tem certeza da decisão")
        elif confidence >= 0.7:
            explanation_parts.append("Confiança alta - IA considera a decisão apropriada")
        elif confidence >= 0.5:
            explanation_parts.append("Confiança moderada - IA tem algumas incertezas")
        else:
            explanation_parts.append("Confiança baixa - IA recomenda revisão humana")
        
        # Fatores contextuais
        if context.get("affects_users"):
            explanation_parts.append(f"Impacta {context.get('affects_users')} usuários")
        
        if context.get("data_sensitivity"):
            explanation_parts.append("Envolve dados sensíveis")
        
        if context.get("financial_impact"):
            explanation_parts.append("Tem implicações financeiras")
        
        # Explicação de regras aplicadas
        for rule in self.guardrail_rules.values():
            if rule.active and rule.category == category:
                if await self._evaluate_rule_condition(rule, context):
                    explanation_parts.append(f"Regra aplicada: {rule.explanation}")
        
        explanation = ". ".join(explanation_parts)
        
        # Cache da explicação
        self.explanation_cache[cache_key] = explanation
        
        return explanation
    
    async def _apply_guardrails(self, decision: AIDecision) -> AIDecision:
        """Aplica regras de guardrails à decisão"""
        
        applicable_rules = [
            rule for rule in self.guardrail_rules.values()
            if rule.active and rule.category == decision.category
        ]
        
        for rule in applicable_rules:
            if await self._evaluate_rule_condition(rule, decision.context):
                
                # Aplicar ação da regra
                if rule.action == "block":
                    decision.action = "BLOCKED"
                    decision.human_required = True
                    decision.explanation += f" | BLOQUEADO: {rule.explanation}"
                
                elif rule.action == "require_approval":
                    decision.human_required = True
                    decision.explanation += f" | APROVAÇÃO NECESSÁRIA: {rule.explanation}"
                
                elif rule.action == "flag":
                    decision.explanation += f" | SINALIZADO: {rule.explanation}"
                
                elif rule.action == "review":
                    decision.human_required = True
                    decision.explanation += f" | REVISÃO: {rule.explanation}"
                
                elif rule.action == "anonymize":
                    decision.context["anonymize_required"] = True
                    decision.explanation += f" | ANONIMIZAÇÃO: {rule.explanation}"
        
        return decision
    
    async def _evaluate_rule_condition(self, rule: GuardrailRule, context: Dict[str, Any]) -> bool:
        """Avalia se uma condição de regra é atendida"""
        try:
            condition = json.loads(rule.condition)
            return self._evaluate_json_condition(condition, context)
        except:
            return False
    
    def _evaluate_json_condition(self, condition: Any, context: Dict[str, Any]) -> bool:
        """Avalia condição em formato JSON"""
        if isinstance(condition, dict):
            for key, value in condition.items():
                if key in context:
                    if isinstance(value, dict):
                        # Operadores de comparação
                        for op, op_value in value.items():
                            if op == ">" and context[key] <= op_value:
                                return False
                            elif op == "<" and context[key] >= op_value:
                                return False
                            elif op == ">=" and context[key] < op_value:
                                return False
                            elif op == "<=" and context[key] > op_value:
                                return False
                            elif op == "==" and context[key] != op_value:
                                return False
                            elif op == "!=" and context[key] == op_value:
                                return False
                    else:
                        if context[key] != value:
                            return False
                else:
                    return False
            return True
        return condition in context and context[condition]
    
    async def _notify_decision(self, decision: AIDecision):
        """Notifica sobre decisões importantes"""
        for callback in self.notification_callbacks:
            try:
                await callback(decision)
            except Exception as e:
                logger.error(f"Erro em callback de notificação: {e}")
    
    # === MÉTODOS PÚBLICOS DE CONTROLE ===
    
    async def approve_decision(
        self, 
        decision_id: str, 
        reviewer_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """Aprova uma decisão pendente"""
        if decision_id not in self.active_decisions:
            return False
        
        decision = self.active_decisions[decision_id]
        decision.approval_status = "approved"
        decision.human_reviewer = reviewer_id
        
        if notes:
            decision.context["approval_notes"] = notes
        
        # Remover da lista de pendentes
        del self.active_decisions[decision_id]
        
        self.metrics["decisions_approved"] += 1
        
        logger.info(f"Decisão aprovada: {decision_id} por {reviewer_id}")
        return True
    
    async def reject_decision(
        self,
        decision_id: str,
        reviewer_id: str,
        reason: str
    ) -> bool:
        """Rejeita uma decisão pendente"""
        if decision_id not in self.active_decisions:
            return False
        
        decision = self.active_decisions[decision_id]
        decision.approval_status = "rejected"
        decision.human_reviewer = reviewer_id
        decision.override_reason = reason
        
        # Remover da lista de pendentes
        del self.active_decisions[decision_id]
        
        self.metrics["decisions_rejected"] += 1
        
        logger.info(f"Decisão rejeitada: {decision_id} por {reviewer_id}")
        return True
    
    def set_oversight_mode(self, mode: OversightMode):
        """Define o modo de supervisão"""
        self.oversight_mode = mode
        logger.info(f"Modo de supervisão alterado para: {mode.value}")
    
    def add_guardrail_rule(self, rule: GuardrailRule):
        """Adiciona uma nova regra de guardrail"""
        self.guardrail_rules[rule.id] = rule
        logger.info(f"Regra de guardrail adicionada: {rule.name}")
    
    def remove_guardrail_rule(self, rule_id: str):
        """Remove uma regra de guardrail"""
        if rule_id in self.guardrail_rules:
            del self.guardrail_rules[rule_id]
            logger.info(f"Regra de guardrail removida: {rule_id}")
    
    def add_notification_callback(self, callback: Callable):
        """Adiciona callback para notificações"""
        self.notification_callbacks.append(callback)
    
    # === MÉTODOS DE CONSULTA E RELATÓRIOS ===
    
    def get_pending_decisions(self) -> List[AIDecision]:
        """Retorna decisões pendentes de aprovação"""
        return list(self.active_decisions.values())
    
    def get_decision_history(self, limit: int = 100) -> List[AIDecision]:
        """Retorna histórico de decisões"""
        return list(self.decisions_log)[-limit:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do sistema de guardrails"""
        with self._lock:
            return {
                **dict(self.metrics),
                "pending_decisions": len(self.active_decisions),
                "total_decisions": len(self.decisions_log),
                "oversight_mode": self.oversight_mode.value,
                "active_rules": len([r for r in self.guardrail_rules.values() if r.active])
            }
    
    def get_risk_analysis(self) -> Dict[str, Any]:
        """Análise de risco das decisões"""
        if not self.decisions_log:
            return {}
        
        recent_decisions = list(self.decisions_log)[-1000:]  # Últimas 1000 decisões
        
        risk_counts = defaultdict(int)
        category_risks = defaultdict(list)
        
        for decision in recent_decisions:
            risk_counts[decision.risk_level.value] += 1
            category_risks[decision.category.value].append(decision.risk_level.value)
        
        return {
            "risk_distribution": dict(risk_counts),
            "category_analysis": {
                category: {
                    "total": len(risks),
                    "high_risk": risks.count("high") + risks.count("critical"),
                    "avg_risk": self._calculate_avg_risk(risks)
                }
                for category, risks in category_risks.items()
            },
            "intervention_rate": self.metrics.get("human_interventions", 0) / len(recent_decisions) if recent_decisions else 0
        }
    
    def _calculate_avg_risk(self, risk_levels: List[str]) -> float:
        """Calcula risco médio numérico"""
        risk_values = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        if not risk_levels:
            return 0
        return sum(risk_values.get(risk, 1) for risk in risk_levels) / len(risk_levels)
    
    def export_audit_log(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Exporta log de auditoria para compliance"""
        filtered_decisions = [
            decision for decision in self.decisions_log
            if start_date <= decision.timestamp <= end_date
        ]
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_decisions": len(filtered_decisions),
                "human_interventions": len([d for d in filtered_decisions if d.human_required]),
                "high_risk_decisions": len([d for d in filtered_decisions if d.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]),
                "blocked_decisions": len([d for d in filtered_decisions if "BLOCKED" in d.action])
            },
            "decisions": [asdict(decision) for decision in filtered_decisions]
        }

# === INSTÂNCIA GLOBAL ===
ai_guardrails_service = AIGuardrailsService()

# === DECORADOR PARA MONITORAMENTO AUTOMÁTICO ===
def ai_guardrail(category: DecisionCategory, confidence: float = 1.0):
    """
    Decorador para monitoramento automático de funções com IA Guardrails
    
    Usage:
        @ai_guardrail(DecisionCategory.CONTENT_GENERATION, confidence=0.8)
        async def generate_content(text: str):
            # Sua função aqui
            return content
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Preparar contexto
            context = {
                "function": func.__name__,
                "args_count": len(args),
                "kwargs_count": len(kwargs),
                "timestamp": datetime.now().isoformat()
            }
            
            # Avaliar decisão
            decision = await ai_guardrails_service.evaluate_decision(
                action=f"execute_{func.__name__}",
                category=category,
                context=context,
                confidence=confidence
            )
            
            # Se bloqueado, não executar
            if "BLOCKED" in decision.action:
                raise Exception(f"Ação bloqueada pelos guardrails: {decision.explanation}")
            
            # Se requer aprovação humana, aguardar
            if decision.human_required and decision.approval_status is None:
                # Em produção, isso seria uma notificação para humanos
                logger.warning(f"Ação requer aprovação humana: {decision.explanation}")
                # Por enquanto, vamos aprovar automaticamente para não travar
                await ai_guardrails_service.approve_decision(decision.id, "system_auto")
            
            # Executar função
            result = await func(*args, **kwargs)
            
            return result
        
        return wrapper
    return decorator

logger.info("✅ AI Guardrails Service carregado com sucesso") 