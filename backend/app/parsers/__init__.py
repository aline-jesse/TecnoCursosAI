from .pdf_parser import parse_pdf
from .pptx_parser import parse_pptx
from .registry import register_parser, get_parser

register_parser('.pdf', parse_pdf)
register_parser('.pptx', parse_pptx)

__all__ = ["parse_pdf", "parse_pptx", "register_parser", "get_parser"]
