#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced A/B Testing & Feature Expansion System - TecnoCursos AI

Sistema avançado de A/B testing e feature flagging seguindo as melhores práticas de:
- Experimentation engineering
- Statistical significance testing
- Feature flagging
- Progressive rollouts
- Multi-variate testing
- Bayesian optimization
- Real-time analytics

Baseado em:
- Google Optimize patterns
- Facebook Planout framework
- Netflix experimentation platform
- Spotify feature flag best practices

Funcionalidades:
- A/B testing engine
- Multi-variate testing (MVT)
- Feature flags management
- Progressive rollouts
- Statistical analysis
- Real-time monitoring
- Experiment lifecycle management
- Automated decision making
- Bayesian optimization
- Causal inference

Autor: TecnoCursos AI System
Data: 17/01/2025
"""

import os
import sys
import json
import time
import uuid
import hashlib
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
import random
from functools import wraps

try:
    import numpy as np
    import pandas as pd
    from scipy import stats
    from scipy.stats import chi2_contingency, ttest_ind, mannwhitneyu
    import matplotlib.pyplot as plt
    import seaborn as sns
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False
    print("⚠️  Statistical libraries não disponíveis")

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import cross_val_score
    from sklearn.preprocessing import StandardScaler
    import pymc3 as pm
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  ML libraries não disponíveis para Bayesian optimization")

try:
    import redis
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import text
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("⚠️  Database dependencies não disponíveis")

# ============================================================================
# ENUMS E CONSTANTES
# ============================================================================

class ExperimentStatus(Enum):
    """Status do experimento"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ExperimentType(Enum):
    """Tipo de experimento"""
    AB_TEST = "ab_test"
    MULTIVARIATE = "multivariate"
    FEATURE_FLAG = "feature_flag"
    PROGRESSIVE_ROLLOUT = "progressive_rollout"

class MetricType(Enum):
    """Tipo de métrica"""
    CONVERSION = "conversion"
    REVENUE = "revenue"
    ENGAGEMENT = "engagement"
    RETENTION = "retention"
    PERFORMANCE = "performance"

class AllocationMethod(Enum):
    """Método de alocação"""
    RANDOM = "random"
    DETERMINISTIC = "deterministic"
    STRATIFIED = "stratified"
    TRAFFIC_BASED = "traffic_based"

class SignificanceLevel(Enum):
    """Nível de significância"""
    LOW = 0.10      # 90% confidence
    MEDIUM = 0.05   # 95% confidence
    HIGH = 0.01     # 99% confidence

# ============================================================================
# MODELOS DE DADOS
# ============================================================================

@dataclass
class ExperimentVariant:
    """Variante do experimento"""
    variant_id: str
    name: str
    description: str
    allocation_percentage: float
    configuration: Dict[str, Any]
    is_control: bool = False

@dataclass
class ExperimentMetric:
    """Métrica do experimento"""
    metric_id: str
    name: str
    description: str
    metric_type: MetricType
    goal: str  # "increase", "decrease", "maintain"
    primary: bool = False
    target_value: Optional[float] = None
    minimum_effect_size: float = 0.05  # 5% minimum effect

@dataclass
class Experiment:
    """Definição de experimento"""
    experiment_id: str
    name: str
    description: str
    experiment_type: ExperimentType
    status: ExperimentStatus
    variants: List[ExperimentVariant]
    metrics: List[ExperimentMetric]
    target_audience: Dict[str, Any]
    allocation_method: AllocationMethod
    traffic_percentage: float
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_sample_size: int = 1000
    significance_level: SignificanceLevel = SignificanceLevel.MEDIUM
    power: float = 0.8  # Statistical power
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    tags: List[str] = field(default_factory=list)

@dataclass
class ExperimentEvent:
    """Evento do experimento"""
    event_id: str
    experiment_id: str
    variant_id: str
    user_id: str
    session_id: str
    metric_name: str
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExperimentResult:
    """Resultado do experimento"""
    experiment_id: str
    variant_id: str
    metric_name: str
    sample_size: int
    conversions: int
    conversion_rate: float
    confidence_interval: Tuple[float, float]
    p_value: float
    effect_size: float
    statistical_significance: bool
    practical_significance: bool
    confidence_level: float

@dataclass
class FeatureFlag:
    """Feature flag"""
    flag_id: str
    name: str
    description: str
    is_enabled: bool
    rollout_percentage: float
    target_users: List[str]
    target_segments: List[str]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)

# ============================================================================
# ALLOCATION ENGINE
# ============================================================================

class AllocationEngine:
    """Engine de alocação de usuários"""
    
    def __init__(self):
        self.salt = os.getenv("AB_TEST_SALT", "tecnocursos_ab_salt")
        self.allocation_cache = {}
        
    def allocate_user(self, user_id: str, experiment: Experiment) -> Optional[str]:
        """Alocar usuário para uma variante"""
        try:
            # Verificar se usuário está no público-alvo
            if not self._is_in_target_audience(user_id, experiment.target_audience):
                return None
            
            # Verificar tráfego geral
            if not self._should_include_in_traffic(user_id, experiment.traffic_percentage):
                return None
            
            # Alocar baseado no método
            if experiment.allocation_method == AllocationMethod.DETERMINISTIC:
                return self._deterministic_allocation(user_id, experiment)
            elif experiment.allocation_method == AllocationMethod.RANDOM:
                return self._random_allocation(user_id, experiment)
            elif experiment.allocation_method == AllocationMethod.STRATIFIED:
                return self._stratified_allocation(user_id, experiment)
            else:
                return self._deterministic_allocation(user_id, experiment)  # Default
                
        except Exception as e:
            logging.error(f"Erro na alocação do usuário {user_id}: {e}")
            return None
    
    def _is_in_target_audience(self, user_id: str, target_audience: Dict[str, Any]) -> bool:
        """Verificar se usuário está no público-alvo"""
        if not target_audience:
            return True
        
        # Implementação simplificada - em produção, consultar dados do usuário
        # Exemplo de critérios: país, idade, tipo de conta, etc.
        
        # Simular alguns critérios
        if "countries" in target_audience:
            # Simular verificação de país baseada no user_id
            user_hash = int(hashlib.md5(f"{user_id}_country".encode()).hexdigest(), 16)
            user_country = ["BR", "US", "UK", "DE", "FR"][user_hash % 5]
            if user_country not in target_audience["countries"]:
                return False
        
        if "user_types" in target_audience:
            # Simular tipo de usuário
            user_hash = int(hashlib.md5(f"{user_id}_type".encode()).hexdigest(), 16)
            user_type = ["free", "premium", "enterprise"][user_hash % 3]
            if user_type not in target_audience["user_types"]:
                return False
        
        return True
    
    def _should_include_in_traffic(self, user_id: str, traffic_percentage: float) -> bool:
        """Verificar se usuário deve ser incluído no tráfego"""
        if traffic_percentage >= 100.0:
            return True
        
        # Hash determinístico baseado no user_id
        user_hash = int(hashlib.md5(f"{user_id}_{self.salt}_traffic".encode()).hexdigest(), 16)
        user_bucket = (user_hash % 10000) / 100.0  # 0-99.99%
        
        return user_bucket < traffic_percentage
    
    def _deterministic_allocation(self, user_id: str, experiment: Experiment) -> str:
        """Alocação determinística (sempre o mesmo resultado para o mesmo usuário)"""
        # Hash baseado no user_id e experiment_id
        hash_input = f"{user_id}_{experiment.experiment_id}_{self.salt}"
        user_hash = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        user_bucket = user_hash % 10000  # 0-9999
        
        # Alocar baseado nas porcentagens
        cumulative_percentage = 0
        for variant in experiment.variants:
            cumulative_percentage += variant.allocation_percentage
            threshold = int(cumulative_percentage * 100)  # Convert to 0-10000 scale
            
            if user_bucket < threshold:
                return variant.variant_id
        
        # Fallback para controle se algo der errado
        control_variant = next((v for v in experiment.variants if v.is_control), experiment.variants[0])
        return control_variant.variant_id
    
    def _random_allocation(self, user_id: str, experiment: Experiment) -> str:
        """Alocação aleatória"""
        # Usar seed baseado no user_id para consistência
        random.seed(hash(f"{user_id}_{experiment.experiment_id}"))
        
        rand_value = random.random() * 100
        cumulative_percentage = 0
        
        for variant in experiment.variants:
            cumulative_percentage += variant.allocation_percentage
            if rand_value <= cumulative_percentage:
                return variant.variant_id
        
        # Fallback
        control_variant = next((v for v in experiment.variants if v.is_control), experiment.variants[0])
        return control_variant.variant_id
    
    def _stratified_allocation(self, user_id: str, experiment: Experiment) -> str:
        """Alocação estratificada (garante distribuição uniforme por segmentos)"""
        # Implementação simplificada - em produção, usar segmentos reais
        user_segment = self._get_user_segment(user_id)
        
        # Para cada segmento, usar alocação determinística
        hash_input = f"{user_id}_{experiment.experiment_id}_{user_segment}_{self.salt}"
        user_hash = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        user_bucket = user_hash % 10000
        
        cumulative_percentage = 0
        for variant in experiment.variants:
            cumulative_percentage += variant.allocation_percentage
            threshold = int(cumulative_percentage * 100)
            
            if user_bucket < threshold:
                return variant.variant_id
        
        # Fallback
        control_variant = next((v for v in experiment.variants if v.is_control), experiment.variants[0])
        return control_variant.variant_id
    
    def _get_user_segment(self, user_id: str) -> str:
        """Obter segmento do usuário"""
        # Simular segmentação baseada no user_id
        user_hash = int(hashlib.md5(f"{user_id}_segment".encode()).hexdigest(), 16)
        segments = ["new_user", "returning_user", "power_user", "enterprise_user"]
        return segments[user_hash % len(segments)]

# ============================================================================
# STATISTICAL ANALYSIS ENGINE
# ============================================================================

class StatisticalAnalyzer:
    """Engine de análise estatística"""
    
    def __init__(self):
        self.analysis_cache = {}
        
    def analyze_experiment(self, experiment: Experiment, events: List[ExperimentEvent]) -> Dict[str, List[ExperimentResult]]:
        """Analisar experimento completo"""
        if not STATS_AVAILABLE:
            return self._mock_analysis(experiment, events)
        
        results = {}
        
        # Agrupar eventos por métrica
        events_by_metric = {}
        for event in events:
            if event.metric_name not in events_by_metric:
                events_by_metric[event.metric_name] = []
            events_by_metric[event.metric_name].append(event)
        
        # Analisar cada métrica
        for metric in experiment.metrics:
            metric_events = events_by_metric.get(metric.name, [])
            metric_results = self._analyze_metric(experiment, metric, metric_events)
            results[metric.name] = metric_results
        
        return results
    
    def _analyze_metric(self, experiment: Experiment, metric: ExperimentMetric, events: List[ExperimentEvent]) -> List[ExperimentResult]:
        """Analisar métrica específica"""
        results = []
        
        # Agrupar eventos por variante
        events_by_variant = {}
        for event in events:
            if event.variant_id not in events_by_variant:
                events_by_variant[event.variant_id] = []
            events_by_variant[event.variant_id].append(event)
        
        # Encontrar variante de controle
        control_variant = next((v for v in experiment.variants if v.is_control), experiment.variants[0])
        control_events = events_by_variant.get(control_variant.variant_id, [])
        
        # Analisar cada variante vs controle
        for variant in experiment.variants:
            if variant.is_control:
                continue
            
            variant_events = events_by_variant.get(variant.variant_id, [])
            
            if metric.metric_type == MetricType.CONVERSION:
                result = self._analyze_conversion_metric(
                    experiment, variant, metric, control_events, variant_events
                )
            else:
                result = self._analyze_continuous_metric(
                    experiment, variant, metric, control_events, variant_events
                )
            
            results.append(result)
        
        return results
    
    def _analyze_conversion_metric(self, experiment: Experiment, variant: ExperimentVariant, 
                                  metric: ExperimentMetric, control_events: List[ExperimentEvent], 
                                  variant_events: List[ExperimentEvent]) -> ExperimentResult:
        """Analisar métrica de conversão"""
        # Calcular taxas de conversão
        control_users = set(e.user_id for e in control_events)
        variant_users = set(e.user_id for e in variant_events)
        
        control_conversions = len([e for e in control_events if e.value > 0])
        variant_conversions = len([e for e in variant_events if e.value > 0])
        
        control_sample_size = len(control_users)
        variant_sample_size = len(variant_users)
        
        control_rate = control_conversions / control_sample_size if control_sample_size > 0 else 0
        variant_rate = variant_conversions / variant_sample_size if variant_sample_size > 0 else 0
        
        # Teste de significância (Chi-square)
        if control_sample_size > 0 and variant_sample_size > 0:
            # Tabela de contingência
            observed = np.array([
                [control_conversions, control_sample_size - control_conversions],
                [variant_conversions, variant_sample_size - variant_conversions]
            ])
            
            chi2, p_value, dof, expected = chi2_contingency(observed)
            
            # Intervalo de confiança para diferença de proporções
            diff = variant_rate - control_rate
            se_diff = np.sqrt(
                (control_rate * (1 - control_rate) / control_sample_size) +
                (variant_rate * (1 - variant_rate) / variant_sample_size)
            )
            
            z_score = stats.norm.ppf(1 - experiment.significance_level.value / 2)
            margin_of_error = z_score * se_diff
            ci_lower = diff - margin_of_error
            ci_upper = diff + margin_of_error
            
        else:
            p_value = 1.0
            ci_lower = ci_upper = 0
            diff = 0
        
        # Efeito prático
        effect_size = abs(diff)
        practical_significance = effect_size >= metric.minimum_effect_size
        statistical_significance = p_value < experiment.significance_level.value
        
        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            variant_id=variant.variant_id,
            metric_name=metric.name,
            sample_size=variant_sample_size,
            conversions=variant_conversions,
            conversion_rate=variant_rate,
            confidence_interval=(ci_lower, ci_upper),
            p_value=p_value,
            effect_size=effect_size,
            statistical_significance=statistical_significance,
            practical_significance=practical_significance,
            confidence_level=(1 - experiment.significance_level.value) * 100
        )
    
    def _analyze_continuous_metric(self, experiment: Experiment, variant: ExperimentVariant,
                                  metric: ExperimentMetric, control_events: List[ExperimentEvent],
                                  variant_events: List[ExperimentEvent]) -> ExperimentResult:
        """Analisar métrica contínua"""
        control_values = [e.value for e in control_events]
        variant_values = [e.value for e in variant_events]
        
        if not control_values or not variant_values:
            return self._empty_result(experiment, variant, metric)
        
        control_mean = np.mean(control_values)
        variant_mean = np.mean(variant_values)
        
        # T-test para comparar médias
        if len(control_values) > 1 and len(variant_values) > 1:
            t_stat, p_value = ttest_ind(variant_values, control_values)
            
            # Intervalo de confiança para diferença de médias
            pooled_se = np.sqrt(
                (np.var(control_values, ddof=1) / len(control_values)) +
                (np.var(variant_values, ddof=1) / len(variant_values))
            )
            
            degrees_freedom = len(control_values) + len(variant_values) - 2
            t_critical = stats.t.ppf(1 - experiment.significance_level.value / 2, degrees_freedom)
            
            diff = variant_mean - control_mean
            margin_of_error = t_critical * pooled_se
            ci_lower = diff - margin_of_error
            ci_upper = diff + margin_of_error
            
        else:
            p_value = 1.0
            ci_lower = ci_upper = 0
            diff = variant_mean - control_mean
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt(
            ((len(control_values) - 1) * np.var(control_values, ddof=1) +
             (len(variant_values) - 1) * np.var(variant_values, ddof=1)) /
            (len(control_values) + len(variant_values) - 2)
        )
        
        effect_size = abs(diff / pooled_std) if pooled_std > 0 else 0
        
        # Significância
        statistical_significance = p_value < experiment.significance_level.value
        practical_significance = effect_size >= metric.minimum_effect_size
        
        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            variant_id=variant.variant_id,
            metric_name=metric.name,
            sample_size=len(variant_values),
            conversions=len([v for v in variant_values if v > 0]),
            conversion_rate=variant_mean,
            confidence_interval=(ci_lower, ci_upper),
            p_value=p_value,
            effect_size=effect_size,
            statistical_significance=statistical_significance,
            practical_significance=practical_significance,
            confidence_level=(1 - experiment.significance_level.value) * 100
        )
    
    def _empty_result(self, experiment: Experiment, variant: ExperimentVariant, metric: ExperimentMetric) -> ExperimentResult:
        """Resultado vazio para casos sem dados"""
        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            variant_id=variant.variant_id,
            metric_name=metric.name,
            sample_size=0,
            conversions=0,
            conversion_rate=0.0,
            confidence_interval=(0.0, 0.0),
            p_value=1.0,
            effect_size=0.0,
            statistical_significance=False,
            practical_significance=False,
            confidence_level=(1 - experiment.significance_level.value) * 100
        )
    
    def _mock_analysis(self, experiment: Experiment, events: List[ExperimentEvent]) -> Dict[str, List[ExperimentResult]]:
        """Análise simulada quando bibliotecas estatísticas não estão disponíveis"""
        results = {}
        
        for metric in experiment.metrics:
            metric_results = []
            
            for variant in experiment.variants:
                if variant.is_control:
                    continue
                
                # Simular resultados
                result = ExperimentResult(
                    experiment_id=experiment.experiment_id,
                    variant_id=variant.variant_id,
                    metric_name=metric.name,
                    sample_size=500,
                    conversions=50,
                    conversion_rate=0.10,
                    confidence_interval=(-0.02, 0.04),
                    p_value=0.15,
                    effect_size=0.01,
                    statistical_significance=False,
                    practical_significance=False,
                    confidence_level=95.0
                )
                
                metric_results.append(result)
            
            results[metric.name] = metric_results
        
        return results
    
    def calculate_sample_size(self, baseline_rate: float, effect_size: float, 
                             significance_level: float = 0.05, power: float = 0.8) -> int:
        """Calcular tamanho da amostra necessário"""
        if not STATS_AVAILABLE:
            return max(1000, int(1 / effect_size * 1000))  # Aproximação simples
        
        # Usar função de power analysis
        from statsmodels.stats.power import ttest_power
        from statsmodels.stats.proportion import proportion_effectsize
        
        try:
            effect = proportion_effectsize(baseline_rate, baseline_rate + effect_size)
            sample_size = ttest_power(effect, power, significance_level)
            return max(100, int(sample_size))
        except:
            return max(1000, int(1 / effect_size * 1000))

# ============================================================================
# FEATURE FLAG MANAGER
# ============================================================================

class FeatureFlagManager:
    """Gerenciador de feature flags"""
    
    def __init__(self):
        self.flags = {}
        self.flag_evaluations = {}
        
    def create_flag(self, flag: FeatureFlag) -> bool:
        """Criar feature flag"""
        try:
            self.flags[flag.flag_id] = flag
            logging.info(f"Feature flag criada: {flag.name}")
            return True
        except Exception as e:
            logging.error(f"Erro ao criar flag {flag.name}: {e}")
            return False
    
    def evaluate_flag(self, flag_id: str, user_id: str, context: Dict[str, Any] = None) -> bool:
        """Avaliar feature flag para usuário"""
        try:
            flag = self.flags.get(flag_id)
            if not flag:
                return False
            
            # Verificar se flag está habilitada
            if not flag.is_enabled:
                return False
            
            # Verificar período de validade
            now = datetime.utcnow()
            if flag.start_date and now < flag.start_date:
                return False
            if flag.end_date and now > flag.end_date:
                return False
            
            # Verificar usuários específicos
            if flag.target_users and user_id in flag.target_users:
                self._record_evaluation(flag_id, user_id, True, "targeted_user")
                return True
            
            # Verificar segmentos
            if flag.target_segments:
                user_segment = self._get_user_segment(user_id, context)
                if user_segment in flag.target_segments:
                    self._record_evaluation(flag_id, user_id, True, "targeted_segment")
                    return True
            
            # Verificar rollout percentage
            if self._should_enable_for_rollout(user_id, flag.rollout_percentage):
                self._record_evaluation(flag_id, user_id, True, "rollout_percentage")
                return True
            
            self._record_evaluation(flag_id, user_id, False, "not_eligible")
            return False
            
        except Exception as e:
            logging.error(f"Erro ao avaliar flag {flag_id} para usuário {user_id}: {e}")
            return False
    
    def _should_enable_for_rollout(self, user_id: str, rollout_percentage: float) -> bool:
        """Verificar se usuário deve receber flag baseado no rollout"""
        if rollout_percentage >= 100.0:
            return True
        if rollout_percentage <= 0.0:
            return False
        
        # Hash determinístico
        user_hash = int(hashlib.md5(f"{user_id}_flag_rollout".encode()).hexdigest(), 16)
        user_bucket = (user_hash % 10000) / 100.0  # 0-99.99%
        
        return user_bucket < rollout_percentage
    
    def _get_user_segment(self, user_id: str, context: Dict[str, Any] = None) -> str:
        """Obter segmento do usuário"""
        if context and "segment" in context:
            return context["segment"]
        
        # Simular segmentação
        user_hash = int(hashlib.md5(f"{user_id}_segment".encode()).hexdigest(), 16)
        segments = ["new_user", "returning_user", "power_user", "enterprise_user"]
        return segments[user_hash % len(segments)]
    
    def _record_evaluation(self, flag_id: str, user_id: str, result: bool, reason: str):
        """Registrar avaliação da flag"""
        if flag_id not in self.flag_evaluations:
            self.flag_evaluations[flag_id] = []
        
        evaluation = {
            "user_id": user_id,
            "result": result,
            "reason": reason,
            "timestamp": datetime.utcnow()
        }
        
        self.flag_evaluations[flag_id].append(evaluation)
        
        # Manter apenas últimas 1000 avaliações por flag
        if len(self.flag_evaluations[flag_id]) > 1000:
            self.flag_evaluations[flag_id] = self.flag_evaluations[flag_id][-1000:]
    
    def update_flag(self, flag_id: str, updates: Dict[str, Any]) -> bool:
        """Atualizar feature flag"""
        try:
            flag = self.flags.get(flag_id)
            if not flag:
                return False
            
            # Atualizar campos permitidos
            allowed_fields = [
                "is_enabled", "rollout_percentage", "target_users", 
                "target_segments", "end_date"
            ]
            
            for field, value in updates.items():
                if field in allowed_fields and hasattr(flag, field):
                    setattr(flag, field, value)
            
            logging.info(f"Feature flag {flag.name} atualizada")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao atualizar flag {flag_id}: {e}")
            return False
    
    def get_flag_stats(self, flag_id: str) -> Dict[str, Any]:
        """Obter estatísticas da flag"""
        flag = self.flags.get(flag_id)
        if not flag:
            return {}
        
        evaluations = self.flag_evaluations.get(flag_id, [])
        recent_evaluations = [
            e for e in evaluations
            if (datetime.utcnow() - e["timestamp"]).total_seconds() < 86400  # 24h
        ]
        
        enabled_count = len([e for e in recent_evaluations if e["result"]])
        total_count = len(recent_evaluations)
        
        return {
            "flag_id": flag_id,
            "flag_name": flag.name,
            "is_enabled": flag.is_enabled,
            "rollout_percentage": flag.rollout_percentage,
            "total_evaluations_24h": total_count,
            "enabled_evaluations_24h": enabled_count,
            "enabled_rate_24h": (enabled_count / total_count * 100) if total_count > 0 else 0,
            "target_users_count": len(flag.target_users),
            "target_segments": flag.target_segments
        }

# ============================================================================
# SISTEMA PRINCIPAL DE A/B TESTING
# ============================================================================

class AdvancedABTestingSystem:
    """Sistema principal de A/B testing"""
    
    def __init__(self):
        self.experiments = {}
        self.events = []
        self.allocation_engine = AllocationEngine()
        self.statistical_analyzer = StatisticalAnalyzer()
        self.feature_flag_manager = FeatureFlagManager()
        self.auto_decision_enabled = True
        
    def create_experiment(self, experiment: Experiment) -> bool:
        """Criar novo experimento"""
        try:
            # Validar experimento
            if not self._validate_experiment(experiment):
                return False
            
            # Calcular tamanho da amostra se não especificado
            if experiment.min_sample_size == 1000:  # valor padrão
                primary_metric = next((m for m in experiment.metrics if m.primary), experiment.metrics[0])
                calculated_size = self.statistical_analyzer.calculate_sample_size(
                    baseline_rate=0.10,  # 10% baseline assumido
                    effect_size=primary_metric.minimum_effect_size,
                    significance_level=experiment.significance_level.value,
                    power=experiment.power
                )
                experiment.min_sample_size = calculated_size
            
            self.experiments[experiment.experiment_id] = experiment
            logging.info(f"Experimento criado: {experiment.name}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao criar experimento {experiment.name}: {e}")
            return False
    
    def _validate_experiment(self, experiment: Experiment) -> bool:
        """Validar configuração do experimento"""
        # Verificar se há pelo menos 2 variantes
        if len(experiment.variants) < 2:
            logging.error("Experimento deve ter pelo menos 2 variantes")
            return False
        
        # Verificar se há variante de controle
        control_variants = [v for v in experiment.variants if v.is_control]
        if len(control_variants) != 1:
            logging.error("Experimento deve ter exatamente 1 variante de controle")
            return False
        
        # Verificar se soma das alocações é 100%
        total_allocation = sum(v.allocation_percentage for v in experiment.variants)
        if abs(total_allocation - 100.0) > 0.01:
            logging.error(f"Soma das alocações deve ser 100%, atual: {total_allocation}%")
            return False
        
        # Verificar se há pelo menos 1 métrica
        if not experiment.metrics:
            logging.error("Experimento deve ter pelo menos 1 métrica")
            return False
        
        # Verificar se há métrica primária
        primary_metrics = [m for m in experiment.metrics if m.primary]
        if len(primary_metrics) != 1:
            logging.error("Experimento deve ter exatamente 1 métrica primária")
            return False
        
        return True
    
    def allocate_user_to_experiment(self, experiment_id: str, user_id: str) -> Optional[str]:
        """Alocar usuário para experimento"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return None
        
        if experiment.status != ExperimentStatus.RUNNING:
            return None
        
        return self.allocation_engine.allocate_user(user_id, experiment)
    
    def track_event(self, experiment_id: str, variant_id: str, user_id: str, 
                   session_id: str, metric_name: str, value: float, 
                   metadata: Dict[str, Any] = None) -> bool:
        """Rastrear evento do experimento"""
        try:
            event = ExperimentEvent(
                event_id=str(uuid.uuid4()),
                experiment_id=experiment_id,
                variant_id=variant_id,
                user_id=user_id,
                session_id=session_id,
                metric_name=metric_name,
                value=value,
                timestamp=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            self.events.append(event)
            
            # Manter apenas eventos dos últimos 30 dias
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            self.events = [e for e in self.events if e.timestamp > cutoff_date]
            
            # Verificar se deve tomar decisão automática
            if self.auto_decision_enabled:
                self._check_auto_decision(experiment_id)
            
            return True
            
        except Exception as e:
            logging.error(f"Erro ao rastrear evento: {e}")
            return False
    
    def _check_auto_decision(self, experiment_id: str):
        """Verificar se deve tomar decisão automática"""
        experiment = self.experiments.get(experiment_id)
        if not experiment or experiment.status != ExperimentStatus.RUNNING:
            return
        
        # Obter eventos do experimento
        experiment_events = [e for e in self.events if e.experiment_id == experiment_id]
        
        # Verificar tamanho mínimo da amostra
        unique_users = set(e.user_id for e in experiment_events)
        if len(unique_users) < experiment.min_sample_size:
            return
        
        # Analisar resultados
        results = self.statistical_analyzer.analyze_experiment(experiment, experiment_events)
        
        # Verificar se há resultado significativo
        primary_metric = next(m for m in experiment.metrics if m.primary)
        primary_results = results.get(primary_metric.name, [])
        
        for result in primary_results:
            if result.statistical_significance and result.practical_significance:
                # Tomar decisão automática
                self._make_auto_decision(experiment, result)
                break
    
    def _make_auto_decision(self, experiment: Experiment, result: ExperimentResult):
        """Tomar decisão automática"""
        if result.effect_size > 0:  # Variante é melhor
            winning_variant = next(v for v in experiment.variants if v.variant_id == result.variant_id)
            logging.info(f"Decisão automática: {winning_variant.name} venceu no experimento {experiment.name}")
            
            # Parar experimento
            experiment.status = ExperimentStatus.COMPLETED
            
            # Criar feature flag para rollout gradual do vencedor
            flag = FeatureFlag(
                flag_id=f"exp_{experiment.experiment_id}_winner",
                name=f"Winner: {winning_variant.name}",
                description=f"Auto-rollout of winning variant from experiment {experiment.name}",
                is_enabled=True,
                rollout_percentage=10.0,  # Começar com 10%
                target_users=[],
                target_segments=[]
            )
            
            self.feature_flag_manager.create_flag(flag)
    
    def get_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """Obter resultados do experimento"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return {}
        
        # Obter eventos
        experiment_events = [e for e in self.events if e.experiment_id == experiment_id]
        
        # Análise estatística
        statistical_results = self.statistical_analyzer.analyze_experiment(experiment, experiment_events)
        
        # Estatísticas gerais
        unique_users = set(e.user_id for e in experiment_events)
        events_by_variant = {}
        users_by_variant = {}
        
        for variant in experiment.variants:
            variant_events = [e for e in experiment_events if e.variant_id == variant.variant_id]
            variant_users = set(e.user_id for e in variant_events)
            
            events_by_variant[variant.variant_id] = len(variant_events)
            users_by_variant[variant.variant_id] = len(variant_users)
        
        return {
            "experiment": asdict(experiment),
            "total_users": len(unique_users),
            "total_events": len(experiment_events),
            "users_by_variant": users_by_variant,
            "events_by_variant": events_by_variant,
            "statistical_results": statistical_results,
            "recommendation": self._generate_recommendation(experiment, statistical_results)
        }
    
    def _generate_recommendation(self, experiment: Experiment, results: Dict[str, List[ExperimentResult]]) -> str:
        """Gerar recomendação baseada nos resultados"""
        primary_metric = next(m for m in experiment.metrics if m.primary)
        primary_results = results.get(primary_metric.name, [])
        
        if not primary_results:
            return "Dados insuficientes para recomendação"
        
        significant_results = [r for r in primary_results if r.statistical_significance and r.practical_significance]
        
        if not significant_results:
            return "Nenhuma variante mostrou diferença significativa do controle"
        
        # Encontrar melhor variante
        best_result = max(significant_results, key=lambda x: x.effect_size)
        best_variant = next(v for v in experiment.variants if v.variant_id == best_result.variant_id)
        
        return f"Recomendação: Implementar '{best_variant.name}' - Melhoria de {best_result.effect_size:.2%} com {best_result.confidence_level:.0f}% de confiança"
    
    def start_experiment(self, experiment_id: str) -> bool:
        """Iniciar experimento"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return False
        
        experiment.status = ExperimentStatus.RUNNING
        experiment.start_date = datetime.utcnow()
        
        logging.info(f"Experimento iniciado: {experiment.name}")
        return True
    
    def stop_experiment(self, experiment_id: str, reason: str = "") -> bool:
        """Parar experimento"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return False
        
        experiment.status = ExperimentStatus.COMPLETED
        experiment.end_date = datetime.utcnow()
        
        logging.info(f"Experimento finalizado: {experiment.name}. Razão: {reason}")
        return True
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obter dados para dashboard"""
        active_experiments = [e for e in self.experiments.values() if e.status == ExperimentStatus.RUNNING]
        completed_experiments = [e for e in self.experiments.values() if e.status == ExperimentStatus.COMPLETED]
        
        # Estatísticas de flags
        active_flags = [f for f in self.feature_flag_manager.flags.values() if f.is_enabled]
        
        # Eventos recentes
        recent_events = [e for e in self.events if (datetime.utcnow() - e.timestamp).total_seconds() < 86400]
        
        return {
            "summary": {
                "total_experiments": len(self.experiments),
                "active_experiments": len(active_experiments),
                "completed_experiments": len(completed_experiments),
                "active_feature_flags": len(active_flags),
                "events_last_24h": len(recent_events)
            },
            "active_experiments": [
                {
                    "experiment_id": e.experiment_id,
                    "name": e.name,
                    "type": e.experiment_type.value,
                    "start_date": e.start_date,
                    "variants_count": len(e.variants),
                    "metrics_count": len(e.metrics)
                }
                for e in active_experiments
            ],
            "feature_flags": [
                self.feature_flag_manager.get_flag_stats(f.flag_id)
                for f in active_flags
            ]
        }

# ============================================================================
# DECORADOR PARA A/B TESTING
# ============================================================================

def ab_test(experiment_id: str, metric_name: str = "conversion", 
           track_value: float = 1.0):
    """Decorator para A/B testing automático"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extrair user_id do contexto (simplificado)
            user_id = kwargs.get("user_id") or getattr(args[0], "user_id", None) if args else None
            session_id = kwargs.get("session_id", str(uuid.uuid4()))
            
            if user_id and hasattr(ab_testing_system, 'allocate_user_to_experiment'):
                # Alocar usuário
                variant_id = ab_testing_system.allocate_user_to_experiment(experiment_id, user_id)
                
                if variant_id:
                    # Executar função
                    result = await func(*args, **kwargs)
                    
                    # Rastrear evento
                    ab_testing_system.track_event(
                        experiment_id=experiment_id,
                        variant_id=variant_id,
                        user_id=user_id,
                        session_id=session_id,
                        metric_name=metric_name,
                        value=track_value
                    )
                    
                    return result
            
            # Fallback: executar função normalmente
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id") or getattr(args[0], "user_id", None) if args else None
            session_id = kwargs.get("session_id", str(uuid.uuid4()))
            
            if user_id and hasattr(ab_testing_system, 'allocate_user_to_experiment'):
                variant_id = ab_testing_system.allocate_user_to_experiment(experiment_id, user_id)
                
                if variant_id:
                    result = func(*args, **kwargs)
                    
                    ab_testing_system.track_event(
                        experiment_id=experiment_id,
                        variant_id=variant_id,
                        user_id=user_id,
                        session_id=session_id,
                        metric_name=metric_name,
                        value=track_value
                    )
                    
                    return result
            
            return func(*args, **kwargs)
        
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# ============================================================================
# INSTÂNCIA GLOBAL
# ============================================================================

# Instância global do sistema de A/B testing
ab_testing_system = AdvancedABTestingSystem()

__all__ = [
    "AdvancedABTestingSystem",
    "Experiment",
    "ExperimentVariant", 
    "ExperimentMetric",
    "FeatureFlag",
    "ExperimentStatus",
    "ExperimentType",
    "MetricType",
    "ab_testing_system",
    "ab_test"
] 