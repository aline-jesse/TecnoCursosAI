import React, { useCallback, useEffect, useRef } from 'react';
import {
  CharacterElement,
  EditorElement,
  ImageElement,
  Scene,
  SceneBackground,
  ShapeElement,
  TextElement,
} from '../../types/editor';
import './ScenePreview.css';

interface ScenePreviewProps {
  scene: Scene;
  width?: number;
  height?: number;
  onError?: (error: string) => void;
  onRender?: (canvas: HTMLCanvasElement) => void;
  className?: string;
}

interface DrawElementOptions {
  ctx: CanvasRenderingContext2D;
  element: EditorElement;
  onError?: (error: string) => void;
}

const DEFAULT_WIDTH = 480;
const DEFAULT_HEIGHT = 270;
const DEFAULT_BACKGROUND = '#ffffff';

const ScenePreview: React.FC<ScenePreviewProps> = ({
  scene,
  width = DEFAULT_WIDTH,
  height = DEFAULT_HEIGHT,
  onError,
  onRender,
  className = '',
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  /**
   * Desenha um elemento de texto
   */
  const drawTextElement = useCallback(
    ({ ctx, element }: DrawElementOptions) => {
      const textElement = element as TextElement;
      ctx.font = `${textElement.fontSize}px ${textElement.fontFamily}`;
      ctx.fillStyle = textElement.fill;
      ctx.textAlign = textElement.textAlign || 'left';
      ctx.textBaseline = textElement.textBaseline || 'top';
      ctx.fillText(textElement.text, 0, 0);
    },
    []
  );

  /**
   * Desenha um elemento de imagem
   */
  const drawImageElement = useCallback(
    ({ ctx, element, onError }: DrawElementOptions) => {
      const imageElement = element as ImageElement | CharacterElement;
      const img = new window.Image();
      img.src = imageElement.src;

      img.onload = () => {
        ctx.drawImage(img, 0, 0, element.width, element.height);
      };

      img.onerror = () => {
        onError?.(`Erro ao carregar imagem: ${imageElement.src}`);
      };
    },
    []
  );

  /**
   * Desenha um elemento de forma
   */
  const drawShapeElement = useCallback(
    ({ ctx, element }: DrawElementOptions) => {
      const shapeElement = element as ShapeElement;
      ctx.fillStyle = shapeElement.fill;
      ctx.strokeStyle = shapeElement.stroke;
      ctx.lineWidth = shapeElement.strokeWidth;

      if (shapeElement.shapeType === 'rectangle') {
        if (shapeElement.cornerRadius) {
          const radius = shapeElement.cornerRadius;
          ctx.beginPath();
          ctx.moveTo(radius, 0);
          ctx.lineTo(element.width - radius, 0);
          ctx.quadraticCurveTo(element.width, 0, element.width, radius);
          ctx.lineTo(element.width, element.height - radius);
          ctx.quadraticCurveTo(
            element.width,
            element.height,
            element.width - radius,
            element.height
          );
          ctx.lineTo(radius, element.height);
          ctx.quadraticCurveTo(0, element.height, 0, element.height - radius);
          ctx.lineTo(0, radius);
          ctx.quadraticCurveTo(0, 0, radius, 0);
          ctx.closePath();
          ctx.fill();
          ctx.stroke();
        } else {
          ctx.fillRect(0, 0, element.width, element.height);
          ctx.strokeRect(0, 0, element.width, element.height);
        }
      } else if (shapeElement.shapeType === 'circle') {
        const radius = Math.min(element.width, element.height) / 2;
        ctx.beginPath();
        ctx.arc(radius, radius, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
      }
    },
    []
  );

  /**
   * Desenha um elemento no canvas
   */
  const drawElement = useCallback(
    ({ ctx, element, onError }: DrawElementOptions) => {
      ctx.save();

      // Aplicar transformações
      ctx.translate(element.x, element.y);
      if (element.rotation) {
        ctx.rotate((element.rotation * Math.PI) / 180);
      }
      if (element.scaleX || element.scaleY) {
        ctx.scale(element.scaleX || 1, element.scaleY || 1);
      }
      ctx.globalAlpha = element.opacity || 1;

      // Desenhar elemento
      try {
        switch (element.type) {
          case 'text':
            drawTextElement({ ctx, element, onError });
            break;
          case 'image':
          case 'character':
            drawImageElement({ ctx, element, onError });
            break;
          case 'shape':
            drawShapeElement({ ctx, element, onError });
            break;
          default:
            onError?.(`Tipo de elemento não suportado: ${element.type}`);
        }
      } catch (error) {
        onError?.(`Erro ao desenhar elemento: ${error}`);
      }

      ctx.restore();
    },
    [drawTextElement, drawImageElement, drawShapeElement]
  );

  /**
   * Desenha o fundo da cena
   */
  const drawBackground = useCallback(
    async (
      ctx: CanvasRenderingContext2D,
      background: SceneBackground,
      width: number,
      height: number
    ): Promise<void> => {
      return new Promise((resolve, reject) => {
        try {
          if (background.type === 'color') {
            ctx.fillStyle = background.value;
            ctx.fillRect(0, 0, width, height);
            resolve();
          } else if (background.type === 'image') {
            const img = new window.Image();
            img.src = background.value;
            img.onload = () => {
              ctx.drawImage(img, 0, 0, width, height);
              resolve();
            };
            img.onerror = () => {
              reject(`Erro ao carregar imagem de fundo: ${background.value}`);
            };
          } else if (background.type === 'video') {
            reject('Fundo de vídeo não suportado no preview');
          }
        } catch (error) {
          reject(`Erro ao desenhar fundo: ${error}`);
        }
      });
    },
    []
  );

  /**
   * Renderiza a cena no canvas
   */
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) {
      onError?.('Canvas 2D não suportado');
      return;
    }

    const renderScene = async () => {
      try {
        // Limpa canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Desenha o fundo
        if (scene.background) {
          await drawBackground(
            ctx,
            scene.background,
            canvas.width,
            canvas.height
          );
        } else {
          ctx.fillStyle = DEFAULT_BACKGROUND;
          ctx.fillRect(0, 0, canvas.width, canvas.height);
        }

        // Desenha os elementos
        scene.elements.forEach(element => {
          drawElement({ ctx, element, onError });
        });

        // Notifica que a renderização foi concluída
        onRender?.(canvas);
      } catch (error) {
        onError?.(error instanceof Error ? error.message : String(error));
      }
    };

    renderScene();
  }, [scene, drawElement, drawBackground, onError, onRender]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className={`scene-preview ${className}`}
      role="img"
      aria-label={`Preview da cena ${scene.name}`}
    />
  );
};

export default ScenePreview;
