from typing import Callable, Dict

PARSER_REGISTRY: Dict[str, Callable] = {}

def register_parser(ext: str, parser_func: Callable):
    """Registra um parser para uma extensão de arquivo."""
    PARSER_REGISTRY[ext.lower()] = parser_func

def get_parser(ext: str) -> Callable:
    """Obtém o parser registrado para a extensão."""
    return PARSER_REGISTRY.get(ext.lower())
