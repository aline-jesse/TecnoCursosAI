/**
 * PreviewCanvas - Canvas de Preview da Cena
 * TecnoCursos AI - Sistema de Preview
 * 
 * Componente responsável por renderizar a cena em tempo real
 * no canvas de preview com animações e efeitos aplicados.
 */
import React, { useEffect, useRef, useCallback } from 'react';
import { ScenePreviewConfig, PreviewPlayerState } from '../types/preview';

interface PreviewCanvasProps {
  config: ScenePreviewConfig;
  playerState: PreviewPlayerState;
}

export const PreviewCanvas: React.FC<PreviewCanvasProps> = ({
  config,
  playerState
}) => {
  // Referência para o canvas
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number>();

  // Função para renderizar um frame
  const renderFrame = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Limpar canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Renderizar elementos com suas animações
    config.elements.forEach(element => {
      const animation = config.animations[element.id];
      if (!animation) return;

      // Calcular progresso da animação
      const progress = Math.max(0, Math.min(1, 
        (playerState.currentTime - animation.delay) / animation.duration
      ));

      // Aplicar animação baseada no tipo
      ctx.save();
      
      switch (animation.type) {
        case 'fade':
          ctx.globalAlpha = progress;
          break;
        case 'slide':
          ctx.translate(
            (1 - progress) * canvas.width,
            0
          );
          break;
        case 'zoom':
          const scale = 0.5 + (progress * 0.5);
          ctx.scale(scale, scale);
          break;
      }

      // Renderizar elemento (implementar baseado no tipo)
      switch (element.type) {
        case 'text':
          // Renderizar texto
          ctx.fillStyle = '#000';
          ctx.font = '24px Arial';
          ctx.fillText('Texto de exemplo', 100, 100);
          break;
        case 'image':
          // Renderizar imagem
          // Implementar carregamento e renderização de imagem
          break;
        case 'shape':
          // Renderizar forma geométrica
          ctx.fillStyle = '#4A90E2';
          ctx.fillRect(100, 100, 200, 100);
          break;
      }

      ctx.restore();
    });

    // Continuar animação se estiver reproduzindo
    if (playerState.isPlaying) {
      animationFrameRef.current = requestAnimationFrame(renderFrame);
    }
  }, [config.elements, config.animations, playerState.currentTime, playerState.isPlaying]);

  // Iniciar/parar renderização baseado no estado de reprodução
  useEffect(() => {
    if (playerState.isPlaying) {
      animationFrameRef.current = requestAnimationFrame(renderFrame);
    } else if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [playerState.isPlaying, renderFrame]);

  // Renderizar frame inicial quando configuração mudar
  useEffect(() => {
    renderFrame();
  }, [config, renderFrame]);

  return (
    <canvas
      ref={canvasRef}
      width={1280}
      height={720}
      className="w-full h-full object-contain bg-black"
    />
  );
};