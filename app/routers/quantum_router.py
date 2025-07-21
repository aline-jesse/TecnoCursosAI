#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔬 Quantum Optimization Router - TecnoCursos AI 2025
==================================================

Router para exposição das capacidades de otimização quântica via API REST.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

try:
    from app.services.quantum_optimization_service import (
        get_quantum_optimization_service,
        OptimizationProblem,
        OptimizationMethod
    )
    QUANTUM_AVAILABLE = True
except ImportError:
    QUANTUM_AVAILABLE = False

try:
    from app.auth import get_current_user, get_current_admin_user
    from app.models import User
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

from app.logger import get_logger

logger = get_logger("quantum_router")

router = APIRouter(
    prefix="/api/quantum",
    tags=["🔬 Quantum Optimization"],
    responses={
        503: {"description": "Serviço quântico indisponível"}
    }
)

# Schemas
class OptimizationRequest(BaseModel):
    problem_type: str = Field(..., description="Tipo do problema (TSP, MaxCut, etc.)")
    method: str = Field("quantum_annealing", description="Método de otimização")
    parameters: Dict[str, Any] = Field(..., description="Parâmetros do problema")
    constraints: List[str] = Field(default_factory=list, description="Restrições")
    objective_function: str = Field("minimize", description="Função objetivo")

class OptimizationResponse(BaseModel):
    problem_id: str
    solution: Dict[str, Any]
    objective_value: float
    quantum_advantage: float
    processing_time: float
    iterations: int

@router.post("/optimize", response_model=OptimizationResponse)
async def solve_optimization_problem(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
    """Resolver problema de otimização usando algoritmos quânticos"""
    if not QUANTUM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviço quântico não disponível")
    
    try:
        quantum_service = get_quantum_optimization_service()
        
        # Criar problema de otimização
        problem = OptimizationProblem(
            id=str(uuid.uuid4()),
            problem_type=request.problem_type,
            parameters=request.parameters,
            constraints=request.constraints,
            objective_function=request.objective_function,
            method=OptimizationMethod(request.method)
        )
        
        # Resolver problema
        result = await quantum_service.solve_optimization_problem(problem)
        
        logger.info(f"Problema quântico {problem.id} resolvido")
        
        return OptimizationResponse(
            problem_id=result.problem_id,
            solution=result.solution,
            objective_value=result.objective_value,
            quantum_advantage=result.quantum_advantage,
            processing_time=result.processing_time,
            iterations=result.iterations
        )
        
    except Exception as e:
        logger.error(f"Erro na otimização quântica: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/status")
async def get_quantum_status():
    """Status do sistema de otimização quântica"""
    if not QUANTUM_AVAILABLE:
        return {"status": "unavailable", "message": "Serviço quântico não configurado"}
    
    quantum_service = get_quantum_optimization_service()
    return quantum_service.get_service_status()

@router.get("/methods")
async def get_optimization_methods():
    """Listar métodos de otimização disponíveis"""
    return {
        "methods": [method.value for method in OptimizationMethod],
        "descriptions": {
            "quantum_annealing": "Otimização por recozimento quântico",
            "qaoa": "Quantum Approximate Optimization Algorithm",
            "vqe": "Variational Quantum Eigensolver",
            "qnn": "Quantum Neural Network",
            "hybrid": "Método híbrido clássico-quântico"
        }
    } 