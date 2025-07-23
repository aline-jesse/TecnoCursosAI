import { useCallback } from 'react';

interface BaseExportOptions {
  quality?: number;
  backgroundColor?: string;
  scale?: number;
  filename?: string;
  dpi?: number;
}

interface ImageExportOptions extends BaseExportOptions {
  format?: 'png' | 'jpeg' | 'webp';
}

interface GIFOptions extends BaseExportOptions {
  frames: Array<{
    canvas: HTMLCanvasElement;
    delay: number;
  }>;
  loop?: boolean;
}

interface PDFOptions extends BaseExportOptions {
  title?: string;
  author?: string;
  subject?: string;
  keywords?: string[];
  orientation?: 'portrait' | 'landscape';
  unit?: 'pt' | 'mm' | 'cm' | 'in';
  pdfFormat?: 'a4' | 'a3' | 'letter' | [number, number];
}

// Remover require('gif.js') do topo do arquivo.
// Substituir uso de GIF = require('gif.js') por:
// @ts-expect-error
const GIF = (await import('gif.js')).default;
// Para jsPDF:

export const useCanvasExport = () => {
  // Exportar para imagem
  const exportToImage = useCallback(
    async (
      canvas: HTMLCanvasElement,
      options: ImageExportOptions = {}
    ): Promise<string> => {
      const {
        format = 'png',
        quality = 1,
        backgroundColor = 'transparent',
        scale = 1,
        filename = `canvas-export.${format}`,
        dpi = 96,
      } = options;

      // Criar canvas temporário com escala
      const tempCanvas = document.createElement('canvas');
      tempCanvas.width = canvas.width * scale;
      tempCanvas.height = canvas.height * scale;

      const tempCtx = tempCanvas.getContext('2d');
      if (!tempCtx) throw new Error('Failed to get temporary context');

      // Aplicar escala e fundo
      tempCtx.scale(scale, scale);
      tempCtx.fillStyle = backgroundColor;
      tempCtx.fillRect(0, 0, canvas.width, canvas.height);

      // Desenhar canvas original
      tempCtx.drawImage(canvas, 0, 0);

      // Configurar DPI
      const dataUrl = tempCanvas.toDataURL(`image/${format}`, quality);
      const img = new Image();
      img.src = dataUrl;

      await new Promise(resolve => {
        img.onload = resolve;
      });

      const finalCanvas = document.createElement('canvas');
      const finalCtx = finalCanvas.getContext('2d');
      if (!finalCtx) throw new Error('Failed to get final context');

      // Calcular dimensões com DPI
      const scaleFactor = dpi / 96;
      finalCanvas.width = tempCanvas.width * scaleFactor;
      finalCanvas.height = tempCanvas.height * scaleFactor;

      // Desenhar com DPI ajustado
      finalCtx.scale(scaleFactor, scaleFactor);
      finalCtx.drawImage(img, 0, 0);

      // Criar link de download
      const link = document.createElement('a');
      link.download = filename;
      link.href = finalCanvas.toDataURL(`image/${format}`, quality);
      link.click();

      return link.href;
    },
    []
  );

  // Exportar para GIF
  const exportToGIF = useCallback(
    async (options: GIFOptions): Promise<string> => {
      const {
        frames,
        loop = true,
        filename = 'canvas-animation.gif',
        quality = 10,
        scale = 1,
      } = options;

      // Carregar biblioteca GIF.js
      // Substituir import dinâmico por require com declaração de módulo para evitar erro de tipo, caso não haja tipos disponíveis.
      // Para gif.js:
      // @ts-ignore
      const GIF = require('gif.js');
      const gif = new GIF({
        workers: 2,
        quality,
        width: frames[0].canvas.width * scale,
        height: frames[0].canvas.height * scale,
        workerScript: '/gif.worker.js',
        repeat: loop ? 0 : -1,
      });

      // Adicionar frames
      frames.forEach(({ canvas, delay }) => {
        // Criar canvas temporário com escala
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = canvas.width * scale;
        tempCanvas.height = canvas.height * scale;

        const tempCtx = tempCanvas.getContext('2d');
        if (!tempCtx) throw new Error('Failed to get temporary context');

        tempCtx.scale(scale, scale);
        tempCtx.drawImage(canvas, 0, 0);

        gif.addFrame(tempCanvas, { delay });
      });

      // Renderizar GIF
      return new Promise((resolve, reject) => {
        gif.on('finished', (blob: Blob) => {
          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.download = filename;
          link.href = url;
          link.click();

          URL.revokeObjectURL(url);
          resolve(url);
        });

        gif.on('error', reject);
        gif.render();
      });
    },
    []
  );

  // Exportar para PDF
  const exportToPDF = useCallback(
    async (
      canvas: HTMLCanvasElement,
      options: PDFOptions = {}
    ): Promise<string> => {
      const {
        title = 'Canvas Export',
        author = '',
        subject = '',
        keywords = [],
        orientation = 'portrait',
        unit = 'mm',
        pdfFormat = 'a4',
        scale = 1,
        quality = 1,
        filename = 'canvas-export.pdf',
      } = options;

      // Carregar biblioteca jsPDF
      // Substituir import dinâmico por require com declaração de módulo para evitar erro de tipo, caso não haja tipos disponíveis.
      // Para jsPDF:
      // @ts-ignore
      const { jsPDF } = require('jspdf');

      // Criar documento PDF
      const pdf = new jsPDF({
        orientation,
        unit,
        format: pdfFormat,
      });

      // Adicionar metadados
      pdf.setProperties({
        title,
        author,
        subject,
        keywords: keywords.join(', '),
      });

      // Converter canvas para imagem
      const dataUrl = canvas.toDataURL('image/jpeg', quality);

      // Calcular dimensões
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const imgWidth = canvas.width * scale;
      const imgHeight = canvas.height * scale;

      // Calcular posição para centralizar
      const x = (pageWidth - imgWidth) / 2;
      const y = (pageHeight - imgHeight) / 2;

      // Adicionar imagem
      pdf.addImage(dataUrl, 'JPEG', x, y, imgWidth, imgHeight);

      // Salvar PDF
      pdf.save(filename);

      return URL.createObjectURL(pdf.output('blob'));
    },
    []
  );

  // Exportar para SVG
  const exportToSVG = useCallback(
    (canvas: HTMLCanvasElement, options: BaseExportOptions = {}): string => {
      const { scale = 1, filename = 'canvas-export.svg' } = options;

      // Criar elemento SVG
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('width', String(canvas.width * scale));
      svg.setAttribute('height', String(canvas.height * scale));
      svg.setAttribute('viewBox', `0 0 ${canvas.width} ${canvas.height}`);

      // Converter canvas para imagem base64
      const image = document.createElementNS(
        'http://www.w3.org/2000/svg',
        'image'
      );
      image.setAttribute('width', String(canvas.width));
      image.setAttribute('height', String(canvas.height));
      image.setAttribute('href', canvas.toDataURL());

      svg.appendChild(image);

      // Converter SVG para string
      const serializer = new XMLSerializer();
      const svgString = serializer.serializeToString(svg);
      const svgBlob = new Blob([svgString], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(svgBlob);

      // Criar link de download
      const link = document.createElement('a');
      link.download = filename;
      link.href = url;
      link.click();

      URL.revokeObjectURL(url);
      return url;
    },
    []
  );

  return {
    exportToImage,
    exportToGIF,
    exportToPDF,
    exportToSVG,
  };
};
