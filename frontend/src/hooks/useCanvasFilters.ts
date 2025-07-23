import { useCallback } from 'react';

interface FilterOptions {
  blur?: number;
  brightness?: number;
  contrast?: number;
  grayscale?: number;
  hueRotate?: number;
  invert?: number;
  opacity?: number;
  saturate?: number;
  sepia?: number;
}

const DEFAULT_OPTIONS: Required<FilterOptions> = {
  blur: 0,
  brightness: 100,
  contrast: 100,
  grayscale: 0,
  hueRotate: 0,
  invert: 0,
  opacity: 100,
  saturate: 100,
  sepia: 0,
};

export const useCanvasFilters = () => {
  const createFilterString = useCallback((options: FilterOptions = {}) => {
    const {
      blur,
      brightness,
      contrast,
      grayscale,
      hueRotate,
      invert,
      opacity,
      saturate,
      sepia,
    } = { ...DEFAULT_OPTIONS, ...options };

    return [
      blur && `blur(${blur}px)`,
      brightness !== 100 && `brightness(${brightness}%)`,
      contrast !== 100 && `contrast(${contrast}%)`,
      grayscale && `grayscale(${grayscale}%)`,
      hueRotate && `hue-rotate(${hueRotate}deg)`,
      invert && `invert(${invert}%)`,
      opacity !== 100 && `opacity(${opacity}%)`,
      saturate !== 100 && `saturate(${saturate}%)`,
      sepia && `sepia(${sepia}%)`,
    ]
      .filter(Boolean)
      .join(' ');
  }, []);

  const applyFilter = useCallback(
    (ctx: CanvasRenderingContext2D, options: FilterOptions = {}) => {
      const filter = createFilterString(options);
      ctx.filter = filter || 'none';
    },
    [createFilterString]
  );

  const clearFilter = useCallback((ctx: CanvasRenderingContext2D) => {
    ctx.filter = 'none';
  }, []);

  const withFilter = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      callback: () => void,
      options: FilterOptions = {}
    ) => {
      ctx.save();
      applyFilter(ctx, options);
      callback();
      ctx.restore();
    },
    [applyFilter]
  );

  const drawImageWithFilter = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      image: CanvasImageSource,
      x: number,
      y: number,
      width?: number,
      height?: number,
      options: FilterOptions = {}
    ) => {
      withFilter(
        ctx,
        () => {
          if (width !== undefined && height !== undefined) {
            ctx.drawImage(image, x, y, width, height);
          } else {
            ctx.drawImage(image, x, y);
          }
        },
        options
      );
    },
    [withFilter]
  );

  const drawRectWithFilter = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      x: number,
      y: number,
      width: number,
      height: number,
      options: FilterOptions = {}
    ) => {
      withFilter(
        ctx,
        () => {
          ctx.fillRect(x, y, width, height);
        },
        options
      );
    },
    [withFilter]
  );

  const drawPathWithFilter = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      path: Path2D,
      options: FilterOptions = {}
    ) => {
      withFilter(
        ctx,
        () => {
          ctx.fill(path);
        },
        options
      );
    },
    [withFilter]
  );

  const applyFilterToRegion = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      x: number,
      y: number,
      width: number,
      height: number,
      options: FilterOptions = {}
    ) => {
      // Criar canvas temporário
      const tempCanvas = document.createElement('canvas');
      const tempCtx = tempCanvas.getContext('2d')!;

      // Copiar região para o canvas temporário
      tempCanvas.width = width;
      tempCanvas.height = height;
      tempCtx.drawImage(ctx.canvas, x, y, width, height, 0, 0, width, height);

      // Aplicar filtro
      ctx.save();
      applyFilter(ctx, options);
      ctx.drawImage(tempCanvas, x, y);
      ctx.restore();
    },
    [applyFilter]
  );

  const createGrayscaleFilter = useCallback((): FilterOptions => {
    return { grayscale: 100 };
  }, []);

  const createSepiaFilter = useCallback((): FilterOptions => {
    return { sepia: 100 };
  }, []);

  const createInvertFilter = useCallback((): FilterOptions => {
    return { invert: 100 };
  }, []);

  const createHighContrastFilter = useCallback((): FilterOptions => {
    return { contrast: 200 };
  }, []);

  const createLowContrastFilter = useCallback((): FilterOptions => {
    return { contrast: 50 };
  }, []);

  const createBrightenFilter = useCallback((): FilterOptions => {
    return { brightness: 150 };
  }, []);

  const createDarkenFilter = useCallback((): FilterOptions => {
    return { brightness: 50 };
  }, []);

  const createBlurFilter = useCallback((amount = 5): FilterOptions => {
    return { blur: amount };
  }, []);

  const createSaturateFilter = useCallback((amount = 200): FilterOptions => {
    return { saturate: amount };
  }, []);

  const createDesaturateFilter = useCallback((amount = 50): FilterOptions => {
    return { saturate: amount };
  }, []);

  return {
    createFilterString,
    applyFilter,
    clearFilter,
    withFilter,
    drawImageWithFilter,
    drawRectWithFilter,
    drawPathWithFilter,
    applyFilterToRegion,
    createGrayscaleFilter,
    createSepiaFilter,
    createInvertFilter,
    createHighContrastFilter,
    createLowContrastFilter,
    createBrightenFilter,
    createDarkenFilter,
    createBlurFilter,
    createSaturateFilter,
    createDesaturateFilter,
  };
};
