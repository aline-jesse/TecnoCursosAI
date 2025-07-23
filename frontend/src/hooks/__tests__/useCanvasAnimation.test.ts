import { act, renderHook  } from '@testing-library/react';
import { useCanvasAnimation } from '../useCanvasAnimation';

describe('useCanvasAnimation', () => {
  let mockContext: CanvasRenderingContext2D;

  beforeEach(() => {
    mockContext = {
      setTransform: jest.fn(),
    } as unknown as CanvasRenderingContext2D;

    // Mock requestAnimationFrame
    jest
      .spyOn(window, 'requestAnimationFrame')
      .mockImplementation(cb => setTimeout(cb, 0));
    jest
      .spyOn(window, 'cancelAnimationFrame')
      .mockImplementation(id => clearTimeout(id));
    jest.spyOn(performance, 'now').mockReturnValue(0);
  });

  afterEach(() => {
    jest.clearAllMocks();
    jest.useRealTimers();
  });

  it('should start animation', () => {
    const { result } = renderHook(() => useCanvasAnimation());
    const onUpdate = jest.fn();
    const onComplete = jest.fn();

    const config = {
      duration: 1000,
      easing: (t: number) => t,
      onUpdate,
      onComplete,
    };

    act(() => {
      result.current.startAnimation(config);
      jest.advanceTimersByTime(1000);
    });

    expect(onUpdate).toHaveBeenCalled();
    expect(onComplete).toHaveBeenCalled();
  });

  it('should stop animation', () => {
    const { result } = renderHook(() => useCanvasAnimation());
    const onUpdate = jest.fn();

    const config = {
      duration: 1000,
      onUpdate,
    };

    let animationId: number;
    act(() => {
      animationId = result.current.startAnimation(config);
      result.current.stopAnimation(animationId);
      jest.advanceTimersByTime(1000);
    });

    expect(onUpdate).not.toHaveBeenCalled();
  });

  it('should stop all animations', () => {
    const { result } = renderHook(() => useCanvasAnimation());
    const onUpdate1 = jest.fn();
    const onUpdate2 = jest.fn();

    const config1 = {
      duration: 1000,
      onUpdate: onUpdate1,
    };

    const config2 = {
      duration: 1000,
      onUpdate: onUpdate2,
    };

    act(() => {
      result.current.startAnimation(config1);
      result.current.startAnimation(config2);
      result.current.stopAllAnimations();
      jest.advanceTimersByTime(1000);
    });

    expect(onUpdate1).not.toHaveBeenCalled();
    expect(onUpdate2).not.toHaveBeenCalled();
  });

  it('should animate property', () => {
    const { result } = renderHook(() => useCanvasAnimation());
    const setter = jest.fn();

    act(() => {
      result.current.animateProperty(
        0,
        100,
        {
          duration: 1000,
          easing: (t: number) => t,
        },
        setter
      );
      jest.advanceTimersByTime(500);
    });

    expect(setter).toHaveBeenCalledWith(50);
  });

  it('should animate transform', () => {
    const { result } = renderHook(() => useCanvasAnimation());

    const startTransform = new DOMMatrix([1, 0, 0, 1, 0, 0]);
    const endTransform = new DOMMatrix([2, 0, 0, 2, 100, 100]);

    act(() => {
      result.current.animateTransform(mockContext, {
        duration: 1000,
        startTransform,
        endTransform,
        easing: (t: number) => t,
      });
      jest.advanceTimersByTime(500);
    });

    expect(mockContext.setTransform).toHaveBeenCalledWith(
      expect.any(DOMMatrix)
    );
  });

  it('should use easing functions', () => {
    const { result } = renderHook(() => useCanvasAnimation());
    const onUpdate = jest.fn();

    Object.entries(result.current.easings).forEach(([name, easing]) => {
      act(() => {
        result.current.startAnimation({
          duration: 1000,
          easing,
          onUpdate,
        });
        jest.advanceTimersByTime(1000);
      });
    });

    expect(onUpdate).toHaveBeenCalledTimes(
      Object.keys(result.current.easings).length
    );
  });

  it('should clean up animations on unmount', () => {
    const { result, unmount } = renderHook(() => useCanvasAnimation());
    const onUpdate = jest.fn();

    act(() => {
      result.current.startAnimation({
        duration: 1000,
        onUpdate,
      });
    });

    unmount();
    jest.advanceTimersByTime(1000);

    expect(onUpdate).not.toHaveBeenCalled();
    expect(window.cancelAnimationFrame).toHaveBeenCalled();
  });

  it('should handle multiple concurrent animations', () => {
    const { result } = renderHook(() => useCanvasAnimation());
    const onUpdate1 = jest.fn();
    const onUpdate2 = jest.fn();
    const onComplete1 = jest.fn();
    const onComplete2 = jest.fn();

    act(() => {
      result.current.startAnimation({
        duration: 1000,
        onUpdate: onUpdate1,
        onComplete: onComplete1,
      });

      result.current.startAnimation({
        duration: 500,
        onUpdate: onUpdate2,
        onComplete: onComplete2,
      });

      jest.advanceTimersByTime(1000);
    });

    expect(onUpdate1).toHaveBeenCalled();
    expect(onUpdate2).toHaveBeenCalled();
    expect(onComplete1).toHaveBeenCalled();
    expect(onComplete2).toHaveBeenCalled();
  });
});
