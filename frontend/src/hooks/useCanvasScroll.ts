import { useCallback, useRef } from 'react';

interface Point {
  x: number;
  y: number;
}

interface ScrollState {
  scrollLeft: number;
  scrollTop: number;
  scrollWidth: number;
  scrollHeight: number;
  clientWidth: number;
  clientHeight: number;
  isScrolling: boolean;
  lastScrollTime: number;
  scrollDirection: {
    x: -1 | 0 | 1;
    y: -1 | 0 | 1;
  };
}

interface ScrollHandlers {
  onScroll?: (scrollLeft: number, scrollTop: number) => void;
  onScrollStart?: () => void;
  onScrollEnd?: () => void;
  onScrollIntoView?: (element: any) => void;
}

interface ScrollOptions {
  smoothScroll?: boolean;
  scrollBehavior?: ScrollBehavior;
  scrollEndDelay?: number;
  preventBounce?: boolean;
  enableInertia?: boolean;
  inertiaDeceleration?: number;
}

export const useCanvasScroll = (
  handlers: ScrollHandlers = {},
  options: ScrollOptions = {}
) => {
  const {
    smoothScroll = true,
    scrollBehavior = 'smooth',
    scrollEndDelay = 150,
    preventBounce = true,
    enableInertia = true,
    inertiaDeceleration = 0.95,
  } = options;

  const scrollState = useRef<ScrollState>({
    scrollLeft: 0,
    scrollTop: 0,
    scrollWidth: 0,
    scrollHeight: 0,
    clientWidth: 0,
    clientHeight: 0,
    isScrolling: false,
    lastScrollTime: 0,
    scrollDirection: {
      x: 0,
      y: 0,
    },
  });

  const scrollEndTimer = useRef<number | null>(null);
  const inertiaFrame = useRef<number | null>(null);
  const velocity = useRef({ x: 0, y: 0 });

  // Atualizar dimensões de rolagem
  const updateScrollDimensions = useCallback(
    (canvas: HTMLCanvasElement, container: HTMLElement) => {
      scrollState.current = {
        ...scrollState.current,
        scrollWidth: canvas.width,
        scrollHeight: canvas.height,
        clientWidth: container.clientWidth,
        clientHeight: container.clientHeight,
      };
    },
    []
  );

  // Converter coordenadas do mouse para coordenadas do canvas
  const getCanvasPoint = useCallback(
    (event: WheelEvent, canvas: HTMLCanvasElement): Point => {
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;

      return {
        x: (event.clientX - rect.left) * scaleX,
        y: (event.clientY - rect.top) * scaleY,
      };
    },
    []
  );

  // Aplicar rolagem com limites
  const applyScroll = useCallback(
    (deltaX: number, deltaY: number, canvas: HTMLCanvasElement) => {
      const { scrollWidth, scrollHeight, clientWidth, clientHeight } =
        scrollState.current;

      // Calcular novos valores de rolagem
      let newScrollLeft = scrollState.current.scrollLeft + deltaX;
      let newScrollTop = scrollState.current.scrollTop + deltaY;

      // Aplicar limites
      if (preventBounce) {
        newScrollLeft = Math.max(
          0,
          Math.min(newScrollLeft, scrollWidth - clientWidth)
        );
        newScrollTop = Math.max(
          0,
          Math.min(newScrollTop, scrollHeight - clientHeight)
        );
      }

      // Atualizar estado
      scrollState.current = {
        ...scrollState.current,
        scrollLeft: newScrollLeft,
        scrollTop: newScrollTop,
        scrollDirection: {
          x: Math.sign(deltaX) as -1 | 0 | 1,
          y: Math.sign(deltaY) as -1 | 0 | 1,
        },
        lastScrollTime: performance.now(),
      };

      // Notificar handlers
      handlers.onScroll?.(newScrollLeft, newScrollTop);

      // Iniciar rolagem se necessário
      if (!scrollState.current.isScrolling) {
        scrollState.current.isScrolling = true;
        handlers.onScrollStart?.();
      }

      // Atualizar timer de fim de rolagem
      if (scrollEndTimer.current !== null) {
        clearTimeout(scrollEndTimer.current);
      }

      scrollEndTimer.current = window.setTimeout(() => {
        scrollState.current.isScrolling = false;
        handlers.onScrollEnd?.();
        scrollEndTimer.current = null;
      }, scrollEndDelay);

      // Atualizar transformação do canvas
      canvas.style.transform = `translate(${-newScrollLeft}px, ${-newScrollTop}px)`;
    },
    [preventBounce, scrollEndDelay, handlers]
  );

  // Aplicar inércia
  const applyInertia = useCallback(
    (canvas: HTMLCanvasElement) => {
      if (!enableInertia || !scrollState.current.isScrolling) return;

      const animate = () => {
        if (
          Math.abs(velocity.current.x) < 0.1 &&
          Math.abs(velocity.current.y) < 0.1
        ) {
          if (inertiaFrame.current !== null) {
            cancelAnimationFrame(inertiaFrame.current);
            inertiaFrame.current = null;
          }
          return;
        }

        applyScroll(velocity.current.x, velocity.current.y, canvas);

        velocity.current.x *= inertiaDeceleration;
        velocity.current.y *= inertiaDeceleration;

        inertiaFrame.current = requestAnimationFrame(animate);
      };

      if (inertiaFrame.current === null) {
        inertiaFrame.current = requestAnimationFrame(animate);
      }
    },
    [enableInertia, inertiaDeceleration, applyScroll]
  );

  // Handler para wheel
  const handleWheel = useCallback(
    (event: WheelEvent) => {
      event.preventDefault();

      const canvas = event.currentTarget as HTMLCanvasElement;
      const deltaX = event.deltaX;
      const deltaY = event.deltaY;

      // Atualizar velocidade para inércia
      if (enableInertia) {
        velocity.current = {
          x: deltaX,
          y: deltaY,
        };
      }

      if (smoothScroll) {
        // Rolagem suave
        const step = () => {
          const progress = Math.min(
            1,
            (performance.now() - startTime) / duration
          );
          const easeProgress = easeInOutCubic(progress);

          applyScroll(deltaX * easeProgress, deltaY * easeProgress, canvas);

          if (progress < 1) {
            requestAnimationFrame(step);
          } else if (enableInertia) {
            applyInertia(canvas);
          }
        };

        const startTime = performance.now();
        const duration = 300; // Duração da animação em ms
        requestAnimationFrame(step);
      } else {
        // Rolagem imediata
        applyScroll(deltaX, deltaY, canvas);
        if (enableInertia) {
          applyInertia(canvas);
        }
      }
    },
    [smoothScroll, enableInertia, applyScroll, applyInertia]
  );

  // Função de easing
  const easeInOutCubic = (t: number): number => {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  };

  // Rolar para posição
  const scrollTo = useCallback(
    (x: number, y: number, canvas: HTMLCanvasElement) => {
      const deltaX = x - scrollState.current.scrollLeft;
      const deltaY = y - scrollState.current.scrollTop;

      if (smoothScroll) {
        const step = () => {
          const progress = Math.min(
            1,
            (performance.now() - startTime) / duration
          );
          const easeProgress = easeInOutCubic(progress);

          applyScroll(deltaX * easeProgress, deltaY * easeProgress, canvas);

          if (progress < 1) {
            requestAnimationFrame(step);
          }
        };

        const startTime = performance.now();
        const duration = 300;
        requestAnimationFrame(step);
      } else {
        applyScroll(deltaX, deltaY, canvas);
      }
    },
    [smoothScroll, applyScroll]
  );

  // Rolar para elemento
  const scrollIntoView = useCallback(
    (
      element: any,
      canvas: HTMLCanvasElement,
      options: {
        block?: 'start' | 'center' | 'end' | 'nearest';
        inline?: 'start' | 'center' | 'end' | 'nearest';
      } = {}
    ) => {
      const { block = 'center', inline = 'center' } = options;

      // Calcular posição do elemento
      const elementBounds = {
        left: element.x,
        top: element.y,
        width: element.width,
        height: element.height,
      };

      // Calcular posição de destino
      let targetX = scrollState.current.scrollLeft;
      let targetY = scrollState.current.scrollTop;

      switch (inline) {
        case 'start':
          targetX = elementBounds.left;
          break;
        case 'center':
          targetX =
            elementBounds.left +
            elementBounds.width / 2 -
            scrollState.current.clientWidth / 2;
          break;
        case 'end':
          targetX =
            elementBounds.left +
            elementBounds.width -
            scrollState.current.clientWidth;
          break;
      }

      switch (block) {
        case 'start':
          targetY = elementBounds.top;
          break;
        case 'center':
          targetY =
            elementBounds.top +
            elementBounds.height / 2 -
            scrollState.current.clientHeight / 2;
          break;
        case 'end':
          targetY =
            elementBounds.top +
            elementBounds.height -
            scrollState.current.clientHeight;
          break;
      }

      scrollTo(targetX, targetY, canvas);
      handlers.onScrollIntoView?.(element);
    },
    [scrollTo, handlers]
  );

  // Obter estado de rolagem
  const getScrollState = useCallback(() => {
    return { ...scrollState.current };
  }, []);

  // Limpar estado
  const clearScrollState = useCallback(() => {
    scrollState.current = {
      scrollLeft: 0,
      scrollTop: 0,
      scrollWidth: 0,
      scrollHeight: 0,
      clientWidth: 0,
      clientHeight: 0,
      isScrolling: false,
      lastScrollTime: 0,
      scrollDirection: {
        x: 0,
        y: 0,
      },
    };

    if (scrollEndTimer.current !== null) {
      clearTimeout(scrollEndTimer.current);
      scrollEndTimer.current = null;
    }

    if (inertiaFrame.current !== null) {
      cancelAnimationFrame(inertiaFrame.current);
      inertiaFrame.current = null;
    }

    velocity.current = { x: 0, y: 0 };
  }, []);

  return {
    handleWheel,
    scrollTo,
    scrollIntoView,
    updateScrollDimensions,
    getScrollState,
    clearScrollState,
  };
};
