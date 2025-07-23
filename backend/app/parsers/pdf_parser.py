import pdfplumber
import os
from typing import List, Dict
from PIL import Image

def parse_pdf(file_path: str, output_dir: str) -> List[Dict]:
    """
    Extrai texto e imagens de cada página de um PDF.
    Retorna lista de slides: [{ 'texto': str, 'imagens': [str] }]
    Salva imagens extraídas em output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)
    slides = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            texto = page.extract_text() or ""
            imagens = []
            for img_idx, img in enumerate(page.images):
                # Extrai imagem da página
                bbox = (img['x0'], img['top'], img['x1'], img['bottom'])
                cropped = page.crop(bbox).to_image(resolution=300)
                img_path = os.path.join(output_dir, f"slide_{i+1}_img_{img_idx+1}.png")
                cropped.save(img_path, format="PNG")
                imagens.append(img_path)
            slides.append({"texto": texto, "imagens": imagens})
    return slides

# Para adicionar novos formatos, crie um novo arquivo parser e siga a mesma interface: parse_<formato>(file_path, output_dir) -> List[Dict]
