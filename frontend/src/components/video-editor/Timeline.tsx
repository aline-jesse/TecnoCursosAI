/**
 * Timeline Component - Interface da linha do tempo
 */

import React, { useCallback, useRef, useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Slider } from '@/components/ui/slider';
import { 
  Scissors, 
  Copy, 
  Trash2, 
  Volume2, 
  VolumeX,
  Lock,
  Unlock,
  Eye,
  EyeOff
} from 'lucide-react';

interface TimelineClip {
  id: string;
  name: string;
  type: 'video' | 'audio' | 'image' | 'text';
  startTime: number;
  endTime: number;
  layer: number;
  color?: string;
  volume?: number;
  locked?: boolean;
  visible?: boolean;
}

interface TimelineProps {
  clips: TimelineClip[];
  currentTime: number;
  duration: number;
  selectedClip: string | null;
  zoom: number;
  onClipSelect: (clipId: string) => void;
  onClipMove: (clipId: string, startTime: number, layer: number) => void;
  onClipResize: (clipId: string, startTime: number, endTime: number) => void;
  onClipSplit: (clipId: string, time: number) => void;
  onClipDelete: (clipId: string) => void;
  onClipDuplicate: (clipId: string) => void;
  onSeek: (time: number) => void;
  onZoomChange: (zoom: number) => void;
}

const Timeline: React.FC<TimelineProps> = ({
  clips,
  currentTime,
  duration,
  selectedClip,
  zoom,
  onClipSelect,
  onClipMove,
  onClipResize,
  onClipSplit,
  onClipDelete,
  onClipDuplicate,
  onSeek,
  onZoomChange
}) => {
  const timelineRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState<string | null>(null);
  const [isResizing, setIsResizing] = useState<{ clipId: string; side: 'start' | 'end' } | null>(null);
  const [dragStart, setDragStart] = useState({ x: 0, time: 0, layer: 0 });

  // Configurações
  const TRACK_HEIGHT = 64;
  const RULER_HEIGHT = 30;
  const LAYERS = ['Vídeo 1', 'Vídeo 2', 'Áudio 1', 'Áudio 2', 'Texto'];

  // Conversores
  const timeToPixels = useCallback((time: number) => {
    const containerWidth = timelineRef.current?.clientWidth || 1000;
    return (time / duration) * containerWidth * (zoom / 100);
  }, [duration, zoom]);

  const pixelsToTime = useCallback((pixels: number) => {
    const containerWidth = timelineRef.current?.clientWidth || 1000;
    return (pixels / (containerWidth * (zoom / 100))) * duration;
  }, [duration, zoom]);

  // Formatação de tempo
  const formatTime = useCallback((seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }, []);

  // Cores por tipo de clipe
  const getClipColor = useCallback((type: string) => {
    const colors = {
      video: 'bg-blue-600 border-blue-500',
      audio: 'bg-green-600 border-green-500',
      image: 'bg-purple-600 border-purple-500',
      text: 'bg-orange-600 border-orange-500'
    };
    return colors[type as keyof typeof colors] || 'bg-gray-600 border-gray-500';
  }, []);

  // Handlers de mouse
  const handleMouseDown = useCallback((e: React.MouseEvent, clipId: string, action: 'move' | 'resize-start' | 'resize-end') => {
    e.preventDefault();
    const clip = clips.find(c => c.id === clipId);
    if (!clip || clip.locked) return;

    const rect = timelineRef.current?.getBoundingClientRect();
    if (!rect) return;

    const x = e.clientX - rect.left;
    const time = pixelsToTime(x);

    if (action === 'move') {
      setIsDragging(clipId);
      setDragStart({ x, time: clip.startTime, layer: clip.layer });
    } else if (action === 'resize-start' || action === 'resize-end') {
      setIsResizing({ clipId, side: action === 'resize-start' ? 'start' : 'end' });
      setDragStart({ x, time, layer: clip.layer });
    }

    onClipSelect(clipId);
  }, [clips, pixelsToTime, onClipSelect]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging && !isResizing) return;

    const rect = timelineRef.current?.getBoundingClientRect();
    if (!rect) return;

    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top - RULER_HEIGHT;
    
    if (isDragging) {
      const clip = clips.find(c => c.id === isDragging);
      if (!clip) return;

      const deltaX = x - dragStart.x;
      const deltaTime = pixelsToTime(deltaX);
      const newStartTime = Math.max(0, dragStart.time + deltaTime);
      const newLayer = Math.max(0, Math.min(LAYERS.length - 1, Math.floor(y / TRACK_HEIGHT)));

      onClipMove(isDragging, newStartTime, newLayer);
    }

    if (isResizing) {
      const clip = clips.find(c => c.id === isResizing.clipId);
      if (!clip) return;

      const currentTime = pixelsToTime(x);
      
      if (isResizing.side === 'start') {
        const newStartTime = Math.max(0, Math.min(currentTime, clip.endTime - 1));
        onClipResize(isResizing.clipId, newStartTime, clip.endTime);
      } else {
        const newEndTime = Math.max(clip.startTime + 1, Math.min(currentTime, duration));
        onClipResize(isResizing.clipId, clip.startTime, newEndTime);
      }
    }
  }, [isDragging, isResizing, clips, dragStart, pixelsToTime, onClipMove, onClipResize, duration]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(null);
    setIsResizing(null);
  }, []);

  // Timeline click para seek
  const handleTimelineClick = useCallback((e: React.MouseEvent) => {
    if (isDragging || isResizing) return;

    const rect = timelineRef.current?.getBoundingClientRect();
    if (!rect) return;

    const x = e.clientX - rect.left;
    const time = pixelsToTime(x);
    onSeek(Math.max(0, Math.min(time, duration)));
  }, [isDragging, isResizing, pixelsToTime, onSeek, duration]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!selectedClip) return;

      switch (e.key) {
        case 'Delete':
        case 'Backspace':
          onClipDelete(selectedClip);
          break;
        case 'c':
          if (e.ctrlKey || e.metaKey) {
            onClipDuplicate(selectedClip);
          }
          break;
        case 's':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            onClipSplit(selectedClip, currentTime);
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedClip, currentTime, onClipDelete, onClipDuplicate, onClipSplit]);

  return (
    <div className="bg-gray-900 border-t border-gray-700">
      {/* Timeline Header */}
      <div className="flex items-center justify-between p-3 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-medium text-white">Timeline</h3>
          {selectedClip && (
            <div className="flex items-center gap-1 ml-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onClipSplit(selectedClip, currentTime)}
                title="Dividir clipe (Ctrl+S)"
              >
                <Scissors className="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onClipDuplicate(selectedClip)}
                title="Duplicar clipe (Ctrl+C)"
              >
                <Copy className="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onClipDelete(selectedClip)}
                title="Excluir clipe (Delete)"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">Zoom:</span>
          <Slider
            value={[zoom]}
            onValueChange={(value) => onZoomChange(value[0])}
            min={25}
            max={400}
            step={25}
            className="w-20"
          />
          <span className="text-xs text-gray-400 w-12">{zoom}%</span>
        </div>
      </div>

      {/* Timeline Content */}
      <div className="relative">
        {/* Track Labels */}
        <div className="absolute left-0 top-0 w-24 bg-gray-800 border-r border-gray-700 z-10">
          {/* Ruler Space */}
          <div className="h-8 border-b border-gray-700" />
          
          {/* Track Labels */}
          {LAYERS.map((layer, index) => (
            <div
              key={layer}
              className="h-16 border-b border-gray-700 flex items-center justify-center text-xs text-gray-400 bg-gray-800"
            >
              {layer}
            </div>
          ))}
        </div>

        {/* Scrollable Timeline */}
        <ScrollArea className="ml-24">
          <div
            ref={timelineRef}
            className="relative min-w-full bg-gray-900 select-none"
            style={{ minWidth: `${Math.max(1000, zoom * 10)}px` }}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onClick={handleTimelineClick}
          >
            {/* Time Ruler */}
            <div className="h-8 bg-gray-800 border-b border-gray-700 relative">
              {Array.from({ length: Math.ceil(duration / 10) }, (_, i) => (
                <div
                  key={i}
                  className="absolute top-0 bottom-0 border-l border-gray-600"
                  style={{ left: `${timeToPixels(i * 10)}px` }}
                >
                  <span className="absolute top-1 left-1 text-xs text-gray-400">
                    {formatTime(i * 10)}
                  </span>
                </div>
              ))}
            </div>

            {/* Playhead */}
            <div
              className="absolute top-0 bottom-0 w-0.5 bg-red-500 z-20 pointer-events-none"
              style={{ left: `${timeToPixels(currentTime)}px` }}
            >
              <div className="absolute -top-1 -left-2 w-4 h-4 bg-red-500 rounded-full" />
            </div>

            {/* Tracks */}
            <div className="relative">
              {LAYERS.map((_, layerIndex) => (
                <div
                  key={layerIndex}
                  className="h-16 border-b border-gray-700 relative bg-gray-900"
                >
                  {/* Layer background with grid */}
                  <div className="absolute inset-0 opacity-20">
                    {Array.from({ length: Math.ceil(duration / 5) }, (_, i) => (
                      <div
                        key={i}
                        className="absolute top-0 bottom-0 w-px bg-gray-600"
                        style={{ left: `${timeToPixels(i * 5)}px` }}
                      />
                    ))}
                  </div>
                </div>
              ))}

              {/* Clips */}
              {clips.map((clip) => (
                <div
                  key={clip.id}
                  className={`absolute rounded cursor-move border-2 transition-all ${
                    getClipColor(clip.type)
                  } ${
                    selectedClip === clip.id 
                      ? 'ring-2 ring-blue-400 ring-opacity-50' 
                      : ''
                  } ${
                    clip.locked ? 'opacity-60' : ''
                  }`}
                  style={{
                    left: `${timeToPixels(clip.startTime)}px`,
                    width: `${timeToPixels(clip.endTime - clip.startTime)}px`,
                    top: `${layerIndex * TRACK_HEIGHT + 4}px`,
                    height: `${TRACK_HEIGHT - 8}px`,
                    zIndex: selectedClip === clip.id ? 15 : 10
                  }}
                  onMouseDown={(e) => handleMouseDown(e, clip.id, 'move')}
                  onClick={(e) => {
                    e.stopPropagation();
                    onClipSelect(clip.id);
                  }}
                >
                  {/* Resize Handles */}
                  {!clip.locked && (
                    <>
                      <div
                        className="absolute left-0 top-0 bottom-0 w-2 cursor-w-resize bg-blue-400 opacity-0 hover:opacity-100 transition-opacity"
                        onMouseDown={(e) => handleMouseDown(e, clip.id, 'resize-start')}
                      />
                      <div
                        className="absolute right-0 top-0 bottom-0 w-2 cursor-e-resize bg-blue-400 opacity-0 hover:opacity-100 transition-opacity"
                        onMouseDown={(e) => handleMouseDown(e, clip.id, 'resize-end')}
                      />
                    </>
                  )}

                  {/* Clip Content */}
                  <div className="h-full flex items-center px-2 text-white relative overflow-hidden">
                    <div className="flex items-center gap-1 flex-1 min-w-0">
                      {clip.type === 'video' && <FileVideo className="w-3 h-3 flex-shrink-0" />}
                      {clip.type === 'audio' && <Volume2 className="w-3 h-3 flex-shrink-0" />}
                      {clip.type === 'image' && <ImageIcon className="w-3 h-3 flex-shrink-0" />}
                      {clip.type === 'text' && <Type className="w-3 h-3 flex-shrink-0" />}
                      
                      <span className="text-xs truncate">{clip.name}</span>
                    </div>

                    {/* Status Icons */}
                    <div className="flex items-center gap-1">
                      {clip.locked && <Lock className="w-3 h-3" />}
                      {!clip.visible && <EyeOff className="w-3 h-3" />}
                      {clip.volume === 0 && <VolumeX className="w-3 h-3" />}
                    </div>
                  </div>

                  {/* Waveform/Thumbnail overlay */}
                  {clip.type === 'audio' && (
                    <div className="absolute inset-0 pointer-events-none">
                      {/* Aqui seria renderizada a waveform */}
                      <div className="h-full flex items-center justify-center opacity-30">
                        <div className="flex items-end gap-px h-6">
                          {Array.from({ length: 20 }, (_, i) => (
                            <div
                              key={i}
                              className="bg-green-300 w-px"
                              style={{ height: `${Math.random() * 100}%` }}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </ScrollArea>
      </div>
    </div>
  );
};

export default Timeline;
