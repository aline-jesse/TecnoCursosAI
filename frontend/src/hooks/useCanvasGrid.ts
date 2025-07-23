import { useCallback, useRef } from 'react';

interface GridConfig {
  size: number;
  color: string;
  opacity: number;
  showSubdivisions: boolean;
  subdivisionSize: number;
  subdivisionColor: string;
  subdivisionOpacity: number;
}

export const useCanvasGrid = () => {
  const configRef = useRef<GridConfig>({
    size: 20,
    color: '#000000',
    opacity: 0.1,
    showSubdivisions: true,
    subdivisionSize: 5,
    subdivisionColor: '#000000',
    subdivisionOpacity: 0.05,
  });

  // Desenhar grade
  const drawGrid = useCallback(
    (ctx: CanvasRenderingContext2D, width: number, height: number) => {
      const {
        size,
        color,
        opacity,
        showSubdivisions,
        subdivisionSize,
        subdivisionColor,
        subdivisionOpacity,
      } = configRef.current;

      ctx.save();

      // Desenhar subdivisões
      if (showSubdivisions) {
        ctx.beginPath();
        ctx.strokeStyle = subdivisionColor;
        ctx.globalAlpha = subdivisionOpacity;

        for (let x = 0; x <= width; x += subdivisionSize) {
          ctx.moveTo(x, 0);
          ctx.lineTo(x, height);
        }

        for (let y = 0; y <= height; y += subdivisionSize) {
          ctx.moveTo(0, y);
          ctx.lineTo(width, y);
        }

        ctx.stroke();
      }

      // Desenhar linhas principais
      ctx.beginPath();
      ctx.strokeStyle = color;
      ctx.globalAlpha = opacity;

      for (let x = 0; x <= width; x += size) {
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
      }

      for (let y = 0; y <= height; y += size) {
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
      }

      ctx.stroke();
      ctx.restore();
    },
    []
  );

  // Ajustar posição ao grid
  const snapToGrid = useCallback((x: number, y: number) => {
    const { size } = configRef.current;
    return {
      x: Math.round(x / size) * size,
      y: Math.round(y / size) * size,
    };
  }, []);

  // Atualizar configuração da grade
  const updateGridConfig = useCallback((config: Partial<GridConfig>) => {
    configRef.current = {
      ...configRef.current,
      ...config,
    };
  }, []);

  // Obter configuração atual
  const getGridConfig = useCallback(() => {
    return { ...configRef.current };
  }, []);

  // Verificar se um ponto está em uma interseção da grade
  const isPointOnGridIntersection = useCallback(
    (x: number, y: number, threshold = 5) => {
      const { size } = configRef.current;
      const snappedPoint = snapToGrid(x, y);

      return (
        Math.abs(x - snappedPoint.x) <= threshold &&
        Math.abs(y - snappedPoint.y) <= threshold
      );
    },
    [snapToGrid]
  );

  // Obter pontos de interseção próximos
  const getNearbyGridPoints = useCallback(
    (x: number, y: number, radius: number) => {
      const { size } = configRef.current;
      const points: Array<{ x: number; y: number }> = [];

      const startX = Math.floor((x - radius) / size) * size;
      const startY = Math.floor((y - radius) / size) * size;
      const endX = Math.ceil((x + radius) / size) * size;
      const endY = Math.ceil((y + radius) / size) * size;

      for (let gridX = startX; gridX <= endX; gridX += size) {
        for (let gridY = startY; gridY <= endY; gridY += size) {
          const distance = Math.sqrt(
            Math.pow(gridX - x, 2) + Math.pow(gridY - y, 2)
          );

          if (distance <= radius) {
            points.push({ x: gridX, y: gridY });
          }
        }
      }

      return points;
    },
    []
  );

  return {
    drawGrid,
    snapToGrid,
    updateGridConfig,
    getGridConfig,
    isPointOnGridIntersection,
    getNearbyGridPoints,
  };
};
