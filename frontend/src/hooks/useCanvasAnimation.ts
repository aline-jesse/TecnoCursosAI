import { useCallback, useEffect, useRef } from 'react';

interface AnimationConfig {
  duration: number;
  easing?: (t: number) => number;
  onUpdate?: (progress: number) => void;
  onComplete?: () => void;
}

interface Animation {
  id: number;
  startTime: number;
  config: AnimationConfig;
}

export const useCanvasAnimation = () => {
  const animationsRef = useRef<Map<number, Animation>>(new Map());
  const nextAnimationIdRef = useRef(1);
  const animationFrameRef = useRef<number | null>(null);

  // Funções de easing padrão
  const easings = {
    linear: (t: number) => t,
    easeInQuad: (t: number) => t * t,
    easeOutQuad: (t: number) => t * (2 - t),
    easeInOutQuad: (t: number) => (t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t),
    easeInCubic: (t: number) => t * t * t,
    easeOutCubic: (t: number) => --t * t * t + 1,
    easeInOutCubic: (t: number) =>
      t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1,
  };

  // Atualizar animações
  const updateAnimations = useCallback((currentTime: number) => {
    animationsRef.current.forEach((animation, id) => {
      const { startTime, config } = animation;
      const {
        duration,
        easing = easings.linear,
        onUpdate,
        onComplete,
      } = config;

      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easedProgress = easing(progress);

      onUpdate?.(easedProgress);

      if (progress >= 1) {
        onComplete?.();
        animationsRef.current.delete(id);
      }
    });

    if (animationsRef.current.size > 0) {
      animationFrameRef.current = requestAnimationFrame(updateAnimations);
    } else {
      animationFrameRef.current = null;
    }
  }, []);

  // Iniciar animação
  const startAnimation = useCallback(
    (config: AnimationConfig): number => {
      const id = nextAnimationIdRef.current++;
      const animation: Animation = {
        id,
        startTime: performance.now(),
        config,
      };

      animationsRef.current.set(id, animation);

      if (!animationFrameRef.current) {
        animationFrameRef.current = requestAnimationFrame(updateAnimations);
      }

      return id;
    },
    [updateAnimations]
  );

  // Parar animação
  const stopAnimation = useCallback((id: number) => {
    animationsRef.current.delete(id);
  }, []);

  // Parar todas as animações
  const stopAllAnimations = useCallback(() => {
    animationsRef.current.clear();
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
  }, []);

  // Animar propriedade
  const animateProperty = useCallback(
    (
      startValue: number,
      endValue: number,
      config: AnimationConfig,
      setter: (value: number) => void
    ): number => {
      return startAnimation({
        ...config,
        onUpdate: progress => {
          const currentValue = startValue + (endValue - startValue) * progress;
          setter(currentValue);
          config.onUpdate?.(progress);
        },
      });
    },
    [startAnimation]
  );

  // Animar transformação
  const animateTransform = useCallback(
    (
      ctx: CanvasRenderingContext2D,
      config: AnimationConfig & {
        startTransform: DOMMatrix;
        endTransform: DOMMatrix;
      }
    ): number => {
      const { startTransform, endTransform, ...animationConfig } = config;

      return startAnimation({
        ...animationConfig,
        onUpdate: progress => {
          const currentTransform = new DOMMatrix([
            startTransform.a + (endTransform.a - startTransform.a) * progress,
            startTransform.b + (endTransform.b - startTransform.b) * progress,
            startTransform.c + (endTransform.c - startTransform.c) * progress,
            startTransform.d + (endTransform.d - startTransform.d) * progress,
            startTransform.e + (endTransform.e - startTransform.e) * progress,
            startTransform.f + (endTransform.f - startTransform.f) * progress,
          ]);

          ctx.setTransform(currentTransform);
          config.onUpdate?.(progress);
        },
      });
    },
    [startAnimation]
  );

  // Limpar animações ao desmontar
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  return {
    startAnimation,
    stopAnimation,
    stopAllAnimations,
    animateProperty,
    animateTransform,
    easings,
  };
};
