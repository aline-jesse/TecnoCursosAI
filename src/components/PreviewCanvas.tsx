/**
 * PreviewCanvas - Canvas de Preview da Cena
 * TecnoCursos AI - Sistema de Preview
 * 
 * Componente responsável por renderizar a cena em tempo real
 * no canvas de preview com animações e efeitos aplicados.
 */

import React, { useEffect, useRef, useCallback, useMemo } from 'react'
import { ScenePreviewConfig, PreviewCanvasProps, PreviewSceneElement } from '../types/preview'

const PreviewCanvas: React.FC<PreviewCanvasProps> = ({
  scene,
  currentTime,
  quality,
  isPlaying,
  onRender,
  onError
}) => {
  // Refs para canvas e contexto
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const contextRef = useRef<CanvasRenderingContext2D | null>(null)
  const animationFrameRef = useRef<number | null>(null)
  const imageCache = useRef<Map<string, HTMLImageElement>>(new Map())
  const videoCache = useRef<Map<string, HTMLVideoElement>>(new Map())

  // Configurações de qualidade baseadas no prop
  const qualitySettings = useMemo(() => {
    switch (quality) {
      case 'low':
        return { width: 640, height: 360, scale: 0.5 }
      case 'medium':
        return { width: 1280, height: 720, scale: 0.75 }
      case 'high':
        return { width: 1920, height: 1080, scale: 1 }
      case 'ultra':
        return { width: 3840, height: 2160, scale: 1.25 }
      default:
        return { width: 1280, height: 720, scale: 0.75 }
    }
  }, [quality])

  /**
   * Inicializa o canvas e contexto
   */
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    // Configura o tamanho do canvas baseado na qualidade
    canvas.width = qualitySettings.width
    canvas.height = qualitySettings.height
    canvas.style.width = '100%'
    canvas.style.height = '100%'
    canvas.style.objectFit = 'contain'

    // Obtém o contexto 2D
    const context = canvas.getContext('2d')
    if (!context) {
      onError?.(new Error('Não foi possível obter contexto 2D do canvas'))
      return
    }

    // Configura renderização de alta qualidade
    context.imageSmoothingEnabled = true
    context.imageSmoothingQuality = 'high'
    context.textBaseline = 'top'
    context.textAlign = 'left'

    contextRef.current = context
  }, [qualitySettings, onError])

  /**
   * Carrega uma imagem e armazena no cache
   */
  const loadImage = useCallback(async (src: string): Promise<HTMLImageElement> => {
    // Verifica se já está no cache
    if (imageCache.current.has(src)) {
      return imageCache.current.get(src)!
    }

    return new Promise((resolve, reject) => {
      const img = new Image()
      img.crossOrigin = 'anonymous'
      
      img.onload = () => {
        imageCache.current.set(src, img)
        resolve(img)
      }
      
      img.onerror = () => {
        reject(new Error(`Erro ao carregar imagem: ${src}`))
      }
      
      img.src = src
    })
  }, [])

  /**
   * Carrega um vídeo e armazena no cache
   */
  const loadVideo = useCallback(async (src: string): Promise<HTMLVideoElement> => {
    // Verifica se já está no cache
    if (videoCache.current.has(src)) {
      return videoCache.current.get(src)!
    }

    return new Promise((resolve, reject) => {
      const video = document.createElement('video')
      video.crossOrigin = 'anonymous'
      video.muted = true // Necessário para autoplay
      
      video.addEventListener('loadedmetadata', () => {
        videoCache.current.set(src, video)
        resolve(video)
      })
      
      video.addEventListener('error', () => {
        reject(new Error(`Erro ao carregar vídeo: ${src}`))
      })
      
      video.src = src
    })
  }, [])

  /**
   * Calcula transformações CSS para animações
   */
  const calculateAnimationTransform = useCallback((
    element: PreviewSceneElement,
    currentTime: number
  ): {
    opacity: number
    transform: string
    visible: boolean
  } => {
    const { startTime, endTime = scene.duration, animation } = element
    
    // Verifica se o elemento deve estar visível no tempo atual
    const isInTimeRange = currentTime >= startTime && currentTime <= endTime
    if (!isInTimeRange || !element.visible) {
      return { opacity: 0, transform: '', visible: false }
    }

    // Se não há animação, retorna estado padrão
    if (!animation || animation.type === 'none') {
      return { opacity: 1, transform: '', visible: true }
    }

    // Calcula o progresso da animação
    const elementDuration = endTime - startTime
    const animationDuration = Math.min(animation.duration, elementDuration)
    const timeSinceStart = currentTime - startTime - animation.delay

    let progress = 0
    let opacity = 1
    let transform = ''

    if (timeSinceStart >= 0 && timeSinceStart <= animationDuration) {
      progress = timeSinceStart / animationDuration
      
      // Aplica easing
      switch (animation.easing) {
        case 'ease-in':
          progress = progress * progress
          break
        case 'ease-out':
          progress = 1 - Math.pow(1 - progress, 2)
          break
        case 'ease-in-out':
          progress = progress < 0.5 
            ? 2 * progress * progress 
            : 1 - Math.pow(-2 * progress + 2, 2) / 2
          break
        // 'linear' não precisa de modificação
      }

      // Aplica animação baseada no tipo
      switch (animation.type) {
        case 'fadeIn':
          opacity = progress
          break
        case 'fadeOut':
          opacity = 1 - progress
          break
        case 'slideIn':
          transform = `translateX(${(1 - progress) * -100}px)`
          break
        case 'slideOut':
          transform = `translateX(${progress * 100}px)`
          break
        case 'bounce':
          const bounceValue = Math.sin(progress * Math.PI * 4) * (1 - progress) * 10
          transform = `translateY(${bounceValue}px)`
          break
        case 'shake':
          const shakeValue = Math.sin(progress * Math.PI * 8) * (1 - progress) * 5
          transform = `translateX(${shakeValue}px)`
          break
        case 'pulse':
          const scaleValue = 1 + Math.sin(progress * Math.PI * 6) * 0.1
          transform = `scale(${scaleValue})`
          break
        case 'rotate':
          transform = `rotate(${progress * 360}deg)`
          break
        case 'scale':
          const scale = progress
          transform = `scale(${scale})`
          break
      }
    } else if (timeSinceStart > animationDuration) {
      // Animação terminada - estado final
      switch (animation.type) {
        case 'fadeOut':
          opacity = 0
          break
        case 'slideOut':
          transform = 'translateX(100px)'
          break
        case 'scale':
          if (animation.direction === 'reverse') {
            transform = 'scale(0)'
          }
          break
      }
    }

    return { opacity, transform, visible: true }
  }, [scene.duration])

  /**
   * Renderiza um elemento de texto
   */
  const renderTextElement = useCallback((
    ctx: CanvasRenderingContext2D,
    element: PreviewSceneElement,
    animationState: ReturnType<typeof calculateAnimationTransform>
  ) => {
    if (!animationState.visible) return

    const { content, position, style } = element
    const { x, y, width, height } = position

    // Salva o estado do contexto
    ctx.save()

    // Aplica opacidade
    ctx.globalAlpha = animationState.opacity

    // Configura fonte e estilo
    const fontSize = style.fontSize || 24
    const fontFamily = style.fontFamily || 'Arial, sans-serif'
    const fontWeight = style.fontWeight || 'normal'
    const color = style.color || '#000000'
    const textAlign = style.textAlign || 'left'
    const backgroundColor = style.backgroundColor

    ctx.font = `${fontWeight} ${fontSize}px ${fontFamily}`
    ctx.fillStyle = color
    ctx.textAlign = textAlign as CanvasTextAlign

    // Renderiza fundo se especificado
    if (backgroundColor) {
      ctx.fillStyle = backgroundColor
      ctx.fillRect(x, y, width, height)
      ctx.fillStyle = color
    }

    // Quebra o texto em linhas se necessário
    const text = content.text || ''
    const lines = text.split('\n')
    const lineHeight = fontSize * 1.2

    // Centraliza verticalmente
    const totalTextHeight = lines.length * lineHeight
    const startY = y + (height - totalTextHeight) / 2

    // Renderiza cada linha
    lines.forEach((line, index) => {
      const lineY = startY + index * lineHeight
      let lineX = x

      // Ajusta posição X baseado no alinhamento
      if (textAlign === 'center') {
        lineX = x + width / 2
      } else if (textAlign === 'right') {
        lineX = x + width
      }

      ctx.fillText(line, lineX, lineY)
    })

    // Restaura o estado do contexto
    ctx.restore()
  }, [])

  /**
   * Renderiza um elemento de imagem
   */
  const renderImageElement = useCallback(async (
    ctx: CanvasRenderingContext2D,
    element: PreviewSceneElement,
    animationState: ReturnType<typeof calculateAnimationTransform>
  ) => {
    if (!animationState.visible || !element.content.src) return

    try {
      const img = await loadImage(element.content.src)
      const { x, y, width, height } = element.position

      // Salva o estado do contexto
      ctx.save()

      // Aplica opacidade
      ctx.globalAlpha = animationState.opacity

      // Renderiza a imagem
      ctx.drawImage(img, x, y, width, height)

      // Restaura o estado do contexto
      ctx.restore()
    } catch (error) {
      console.error('Erro ao renderizar imagem:', error)
      onError?.(error as Error)
    }
  }, [loadImage, onError])

  /**
   * Renderiza um elemento de vídeo
   */
  const renderVideoElement = useCallback(async (
    ctx: CanvasRenderingContext2D,
    element: PreviewSceneElement,
    animationState: ReturnType<typeof calculateAnimationTransform>
  ) => {
    if (!animationState.visible || !element.content.src) return

    try {
      const video = await loadVideo(element.content.src)
      const { x, y, width, height } = element.position

      // Sincroniza o tempo do vídeo com o tempo da cena
      const videoTime = currentTime - element.startTime
      if (Math.abs(video.currentTime - videoTime) > 0.1) {
        video.currentTime = Math.max(0, videoTime)
      }

      // Reproduz ou pausa baseado no estado
      if (isPlaying && video.paused) {
        video.play().catch(console.error)
      } else if (!isPlaying && !video.paused) {
        video.pause()
      }

      // Salva o estado do contexto
      ctx.save()

      // Aplica opacidade
      ctx.globalAlpha = animationState.opacity

      // Renderiza o frame atual do vídeo
      ctx.drawImage(video, x, y, width, height)

      // Restaura o estado do contexto
      ctx.restore()
    } catch (error) {
      console.error('Erro ao renderizar vídeo:', error)
      onError?.(error as Error)
    }
  }, [loadVideo, currentTime, isPlaying, onError])

  /**
   * Renderiza um elemento de forma geométrica
   */
  const renderShapeElement = useCallback((
    ctx: CanvasRenderingContext2D,
    element: PreviewSceneElement,
    animationState: ReturnType<typeof calculateAnimationTransform>
  ) => {
    if (!animationState.visible) return

    const { content, position, style } = element
    const { x, y, width, height } = position
    const shapeType = content.type || 'rectangle'

    // Salva o estado do contexto
    ctx.save()

    // Aplica opacidade
    ctx.globalAlpha = animationState.opacity

    // Configura estilos
    const fillColor = style.fillColor || style.backgroundColor || '#cccccc'
    const strokeColor = style.strokeColor || style.borderColor
    const strokeWidth = style.strokeWidth || style.borderWidth || 0

    ctx.fillStyle = fillColor
    if (strokeColor && strokeWidth > 0) {
      ctx.strokeStyle = strokeColor
      ctx.lineWidth = strokeWidth
    }

    // Desenha a forma baseada no tipo
    ctx.beginPath()
    switch (shapeType) {
      case 'rectangle':
        ctx.rect(x, y, width, height)
        break
      case 'circle':
        const radius = Math.min(width, height) / 2
        const centerX = x + width / 2
        const centerY = y + height / 2
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI)
        break
      case 'ellipse':
        const radiusX = width / 2
        const radiusY = height / 2
        const centerXe = x + radiusX
        const centerYe = y + radiusY
        ctx.ellipse(centerXe, centerYe, radiusX, radiusY, 0, 0, 2 * Math.PI)
        break
      case 'triangle':
        ctx.moveTo(x + width / 2, y)
        ctx.lineTo(x, y + height)
        ctx.lineTo(x + width, y + height)
        ctx.closePath()
        break
    }

    // Preenche e contorna
    ctx.fill()
    if (strokeColor && strokeWidth > 0) {
      ctx.stroke()
    }

    // Restaura o estado do contexto
    ctx.restore()
  }, [])

  /**
   * Renderiza todos os elementos da cena
   */
  const renderScene = useCallback(async () => {
    const canvas = canvasRef.current
    const ctx = contextRef.current
    if (!canvas || !ctx || !scene) return

    // Limpa o canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Renderiza o fundo da cena
    if (scene.background) {
      ctx.save()
      
      switch (scene.background.type) {
        case 'color':
          ctx.fillStyle = scene.background.value
          ctx.fillRect(0, 0, canvas.width, canvas.height)
          break
        case 'gradient':
          // Implementa gradiente (simplificado)
          const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height)
          gradient.addColorStop(0, scene.background.value)
          gradient.addColorStop(1, '#ffffff')
          ctx.fillStyle = gradient
          ctx.fillRect(0, 0, canvas.width, canvas.height)
          break
        case 'image':
          try {
            const bgImage = await loadImage(scene.background.value)
            ctx.drawImage(bgImage, 0, 0, canvas.width, canvas.height)
          } catch (error) {
            console.error('Erro ao renderizar fundo:', error)
          }
          break
      }
      
      ctx.restore()
    }

    // Ordena elementos por z-index (ou ordem na lista)
    const sortedElements = [...scene.elements].sort((a, b) => {
      const aIndex = (a as any).zIndex || 0
      const bIndex = (b as any).zIndex || 0
      return aIndex - bIndex
    })

    // Renderiza cada elemento
    for (const element of sortedElements) {
      const animationState = calculateAnimationTransform(element, currentTime)
      
      try {
        switch (element.type) {
          case 'text':
            renderTextElement(ctx, element, animationState)
            break
          case 'image':
            await renderImageElement(ctx, element, animationState)
            break
          case 'video':
            await renderVideoElement(ctx, element, animationState)
            break
          case 'shape':
            renderShapeElement(ctx, element, animationState)
            break
        }
      } catch (error) {
        console.error(`Erro ao renderizar elemento ${element.type}:`, error)
        onError?.(error as Error)
      }
    }

    // Chama callback de render se fornecido
    onRender?.(canvas)
  }, [
    scene,
    currentTime,
    calculateAnimationTransform,
    renderTextElement,
    renderImageElement,
    renderVideoElement,
    renderShapeElement,
    loadImage,
    onRender,
    onError
  ])

  /**
   * Loop de animação para renderização contínua
   */
  const animate = useCallback(() => {
    renderScene()
    
    if (isPlaying) {
      animationFrameRef.current = requestAnimationFrame(animate)
    }
  }, [renderScene, isPlaying])

  // Inicia/para a animação baseado no estado de reprodução
  useEffect(() => {
    if (isPlaying) {
      animate()
    } else {
      // Renderiza frame estático
      renderScene()
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
        animationFrameRef.current = null
      }
    }
  }, [isPlaying, animate, renderScene])

  // Renderiza quando o tempo atual muda (para scrubbing)
  useEffect(() => {
    if (!isPlaying) {
      renderScene()
    }
  }, [currentTime, renderScene, isPlaying])

  // Limpa cache quando necessário
  useEffect(() => {
    return () => {
      // Limpa caches ao desmontar
      imageCache.current.clear()
      videoCache.current.forEach(video => {
        video.pause()
        video.src = ''
      })
      videoCache.current.clear()
    }
  }, [])

  return (
    <div className="preview-canvas-wrapper">
      <canvas
        ref={canvasRef}
        className="preview-canvas"
        style={{
          maxWidth: '100%',
          maxHeight: '100%',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          backgroundColor: '#000000'
        }}
      />
      
      {/* Overlay de informações de debug (opcional) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="preview-debug-info">
          <div>Qualidade: {quality}</div>
          <div>Resolução: {qualitySettings.width}x{qualitySettings.height}</div>
          <div>Tempo: {currentTime.toFixed(2)}s</div>
          <div>Elementos: {scene.elements.length}</div>
        </div>
      )}
    </div>
  )
}

export default PreviewCanvas