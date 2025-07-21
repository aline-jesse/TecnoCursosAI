/**
 * Timeline - Componente de timeline do editor (Simplificado)
 * Exibe cenas em formato de timeline
 */

import React, { useCallback, useRef } from 'react';
import { useScenes, useActiveScene, useEditor } from '../store/editorStore';
import './Timeline.css';

/**
 * Timeline - Componente de timeline do editor
 * Versão simplificada focada em exibir e selecionar cenas
 */
const Timeline: React.FC = () => {
  const timelineRef = useRef<HTMLDivElement>(null);
  
  // Hooks da store Zustand
  const scenes = useScenes();
  const activeScene = useActiveScene();
  const { setActiveScene } = useEditor();

  /**
   * Calcula a duração total do projeto
   */
  const totalDuration = scenes.reduce((total, scene) => total + (scene.duration || 5), 0);

  /**
   * Converte pixels para tempo
   */
  const pixelsToTime = useCallback((pixels: number) => {
    const timelineWidth = timelineRef.current?.offsetWidth || 800;
    return (pixels / timelineWidth) * totalDuration;
  }, [totalDuration]);

  /**
   * Converte tempo para pixels
   */
  const timeToPixels = useCallback((time: number) => {
    const timelineWidth = timelineRef.current?.offsetWidth || 800;
    return (time / totalDuration) * timelineWidth;
  }, [totalDuration]);

  /**
   * Manipula clique na timeline
   */
  const handleTimelineClick = useCallback((e: React.MouseEvent) => {
    if (!timelineRef.current) return;
    
    const rect = timelineRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const newTime = pixelsToTime(clickX);
    
    console.log('Timeline clicked at time:', newTime);
  }, [pixelsToTime]);

  /**
   * Manipula clique em uma cena na timeline
   */
  const handleSceneClick = useCallback((scene: any) => {
    setActiveScene(scene.id);
  }, [setActiveScene]);

  /**
   * Calcula posição da cena na timeline
   */
  const getScenePosition = useCallback((index: number) => {
    let position = 0;
    for (let i = 0; i < index; i++) {
      position += scenes[i]?.duration || 5;
    }
    return timeToPixels(position);
  }, [scenes, timeToPixels]);

  /**
   * Calcula largura da cena na timeline
   */
  const getSceneWidth = useCallback((scene: any) => {
    return timeToPixels(scene.duration || 5);
  }, [timeToPixels]);

  /**
   * Formata tempo em MM:SS
   */
  const formatTime = useCallback((seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  }, []);

  return (
    <div className="timeline">
      {/* Header da Timeline */}
      <div className="timeline-header">
        <div className="timeline-info">
          <h3>Timeline</h3>
          <span>{scenes.length} cenas • {formatTime(totalDuration)}</span>
        </div>
        
        {/* Controles básicos */}
        <div className="timeline-controls">
          <div className="time-display">
            <span>00:00 / {formatTime(totalDuration)}</span>
          </div>
        </div>
      </div>

      {/* Timeline Principal */}
      <div className="timeline-main">
        {/* Régua de tempo */}
        <div className="time-ruler">
          {Array.from({ length: Math.ceil(totalDuration / 10) }, (_, i) => (
            <div key={i} className="time-marker" style={{ left: `${(i * 10 / totalDuration) * 100}%` }}>
              <span>{formatTime(i * 10)}</span>
            </div>
          ))}
        </div>

        {/* Track principal */}
        <div 
          className="timeline-track"
          ref={timelineRef}
          onClick={handleTimelineClick}
        >
          {/* Cenas */}
          {scenes.map((scene, index) => (
            <div
              key={scene.id}
              className={`timeline-scene ${activeScene?.id === scene.id ? 'active' : ''}`}
              style={{
                left: `${(getScenePosition(index) / (timelineRef.current?.offsetWidth || 800)) * 100}%`,
                width: `${(getSceneWidth(scene) / (timelineRef.current?.offsetWidth || 800)) * 100}%`
              }}
              onClick={(e) => {
                e.stopPropagation();
                handleSceneClick(scene);
              }}
              title={`${scene.title || scene.name} (${formatTime(scene.duration || 5)})`}
            >
              <div className="scene-content">
                <span className="scene-name">{scene.title || scene.name}</span>
                <span className="scene-duration">{formatTime(scene.duration || 5)}</span>
              </div>
            </div>
          ))}

          {/* Linha de tempo (playhead placeholder) */}
          <div className="playhead" style={{ left: '0%' }} />
        </div>
      </div>

      {/* Footer da Timeline */}
      <div className="timeline-footer">
        <div className="zoom-controls">
          <button className="zoom-btn" title="Diminuir Zoom">−</button>
          <span>100%</span>
          <button className="zoom-btn" title="Aumentar Zoom">+</button>
        </div>
      </div>
    </div>
  );
};

export default Timeline;