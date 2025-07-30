/**
 * Editor de Vídeos TecnoCursos AI
 * Interface moderna para edição de vídeos educacionais
 */

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  Play, 
  Pause, 
  Square, 
  SkipBack, 
  SkipForward, 
  Volume2, 
  VolumeX,
  Scissors,
  Download,
  Upload,
  Layers,
  Settings,
  Zap,
  FileVideo,
  Music,
  Type,
  Image as ImageIcon,
  Save,
  Undo,
  Redo,
  Maximize,
  Grid
} from 'lucide-react';

// Interfaces
interface VideoClip {
  id: string;
  name: string;
  src: string;
  duration: number;
  startTime: number;
  endTime: number;
  layer: number;
  type: 'video' | 'audio' | 'image' | 'text';
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  effects?: string[];
  volume?: number;
}

interface ProjectSettings {
  resolution: { width: number; height: number };
  frameRate: number;
  duration: number;
  audioSampleRate: number;
}

const VideoEditor: React.FC = () => {
  // Estados principais
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [volume, setVolume] = useState(100);
  const [isMuted, setIsMuted] = useState(false);
  const [selectedClip, setSelectedClip] = useState<string | null>(null);
  const [zoom, setZoom] = useState(100);
  const [clips, setClips] = useState<VideoClip[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  // Refs
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const timelineRef = useRef<HTMLDivElement>(null);

  // Configurações do projeto
  const [projectSettings] = useState<ProjectSettings>({
    resolution: { width: 1920, height: 1080 },
    frameRate: 30,
    duration: 300, // 5 minutos
    audioSampleRate: 44100
  });

  // Controles de reprodução
  const togglePlayPause = useCallback(() => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  }, [isPlaying]);

  const stopPlayback = useCallback(() => {
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.currentTime = 0;
      setCurrentTime(0);
      setIsPlaying(false);
    }
  }, []);

  const seekTo = useCallback((time: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = time;
      setCurrentTime(time);
    }
  }, []);

  // Controle de volume
  const handleVolumeChange = useCallback((value: number[]) => {
    const newVolume = value[0];
    setVolume(newVolume);
    if (videoRef.current) {
      videoRef.current.volume = newVolume / 100;
    }
  }, []);

  const toggleMute = useCallback(() => {
    if (videoRef.current) {
      const newMuted = !isMuted;
      videoRef.current.muted = newMuted;
      setIsMuted(newMuted);
    }
  }, [isMuted]);

  // Formatação de tempo
  const formatTime = useCallback((seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }, []);

  // Adicionar clipe à timeline
  const addClip = useCallback((clipData: Partial<VideoClip>) => {
    const newClip: VideoClip = {
      id: `clip_${Date.now()}`,
      name: clipData.name || 'Novo Clipe',
      src: clipData.src || '',
      duration: clipData.duration || 10,
      startTime: clipData.startTime || currentTime,
      endTime: clipData.endTime || currentTime + 10,
      layer: clipData.layer || 0,
      type: clipData.type || 'video',
      position: clipData.position || { x: 0, y: 0, width: 100, height: 100 },
      effects: clipData.effects || [],
      volume: clipData.volume || 100
    };

    setClips(prev => [...prev, newClip]);
  }, [currentTime]);

  // Remover clipe
  const removeClip = useCallback((clipId: string) => {
    setClips(prev => prev.filter(clip => clip.id !== clipId));
    if (selectedClip === clipId) {
      setSelectedClip(null);
    }
  }, [selectedClip]);

  // Exportar vídeo
  const exportVideo = useCallback(async () => {
    setIsProcessing(true);
    try {
      // Aqui seria implementada a lógica de export
      // Por exemplo, enviar dados para o backend para processamento
      await new Promise(resolve => setTimeout(resolve, 3000)); // Simulação
      
      // Notificar sucesso
      console.log('Vídeo exportado com sucesso!');
    } catch (error) {
      console.error('Erro ao exportar vídeo:', error);
    } finally {
      setIsProcessing(false);
    }
  }, [clips]);

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold">TecnoCursos Video Editor</h1>
          <Badge variant="secondary">Projeto Sem Título</Badge>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Undo className="w-4 h-4 mr-2" />
            Desfazer
          </Button>
          <Button variant="outline" size="sm">
            <Redo className="w-4 h-4 mr-2" />
            Refazer
          </Button>
          <Button variant="outline" size="sm">
            <Save className="w-4 h-4 mr-2" />
            Salvar
          </Button>
          <Button 
            onClick={exportVideo}
            disabled={isProcessing}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {isProcessing ? (
              <Zap className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Download className="w-4 h-4 mr-2" />
            )}
            {isProcessing ? 'Processando...' : 'Exportar'}
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar Left - Media Library */}
        <Card className="w-80 bg-gray-800 border-gray-700 rounded-none">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Biblioteca de Mídia</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Tabs defaultValue="media" className="w-full">
              <TabsList className="grid w-full grid-cols-4 bg-gray-700">
                <TabsTrigger value="media" className="text-xs">
                  <FileVideo className="w-3 h-3" />
                </TabsTrigger>
                <TabsTrigger value="audio" className="text-xs">
                  <Music className="w-3 h-3" />
                </TabsTrigger>
                <TabsTrigger value="text" className="text-xs">
                  <Type className="w-3 h-3" />
                </TabsTrigger>
                <TabsTrigger value="effects" className="text-xs">
                  <Zap className="w-3 h-3" />
                </TabsTrigger>
              </TabsList>

              <TabsContent value="media" className="mt-0">
                <ScrollArea className="h-96">
                  <div className="p-4 space-y-2">
                    <Button 
                      variant="outline" 
                      className="w-full justify-start"
                      size="sm"
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Importar Vídeo
                    </Button>
                    
                    {/* Lista de mídia */}
                    <div className="grid grid-cols-2 gap-2 mt-4">
                      {[1, 2, 3, 4].map((item) => (
                        <div 
                          key={item}
                          className="aspect-video bg-gray-700 rounded cursor-pointer hover:bg-gray-600 flex items-center justify-center"
                          onClick={() => addClip({ 
                            name: `Video ${item}`,
                            type: 'video',
                            duration: 30 
                          })}
                        >
                          <FileVideo className="w-6 h-6 text-gray-400" />
                        </div>
                      ))}
                    </div>
                  </div>
                </ScrollArea>
              </TabsContent>

              <TabsContent value="audio" className="mt-0">
                <ScrollArea className="h-96">
                  <div className="p-4">
                    <Button 
                      variant="outline" 
                      className="w-full justify-start"
                      size="sm"
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Importar Áudio
                    </Button>
                  </div>
                </ScrollArea>
              </TabsContent>

              <TabsContent value="text" className="mt-0">
                <div className="p-4 space-y-2">
                  <Button 
                    variant="outline" 
                    className="w-full justify-start"
                    size="sm"
                    onClick={() => addClip({ 
                      name: 'Texto',
                      type: 'text',
                      duration: 5 
                    })}
                  >
                    <Type className="w-4 h-4 mr-2" />
                    Adicionar Texto
                  </Button>
                </div>
              </TabsContent>

              <TabsContent value="effects" className="mt-0">
                <div className="p-4 space-y-2">
                  <div className="text-xs text-gray-400 mb-2">Transições</div>
                  {['Fade In', 'Fade Out', 'Slide', 'Zoom'].map((effect) => (
                    <Button 
                      key={effect}
                      variant="ghost" 
                      className="w-full justify-start text-xs"
                      size="sm"
                    >
                      {effect}
                    </Button>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Center - Preview and Timeline */}
        <div className="flex-1 flex flex-col">
          {/* Preview Area */}
          <div className="flex-1 bg-black relative">
            <div className="absolute inset-4 bg-gray-900 rounded flex items-center justify-center">
              <video
                ref={videoRef}
                className="max-w-full max-h-full rounded"
                onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
                onLoadedMetadata={(e) => {
                  // Configurar duração do projeto baseado no vídeo
                }}
              />
              <canvas 
                ref={canvasRef}
                className="absolute inset-0 pointer-events-none"
                width={projectSettings.resolution.width}
                height={projectSettings.resolution.height}
              />
            </div>

            {/* Preview Controls */}
            <div className="absolute top-4 right-4 flex gap-2">
              <Button variant="outline" size="sm">
                <Maximize className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="sm">
                <Grid className="w-4 h-4" />
              </Button>
            </div>

            {/* Zoom Control */}
            <div className="absolute bottom-4 right-4 flex items-center gap-2 bg-gray-800 rounded p-2">
              <span className="text-xs">{zoom}%</span>
              <Slider
                value={[zoom]}
                onValueChange={(value) => setZoom(value[0])}
                min={25}
                max={400}
                step={25}
                className="w-20"
              />
            </div>
          </div>

          {/* Transport Controls */}
          <div className="bg-gray-800 p-4 border-t border-gray-700">
            <div className="flex items-center justify-center gap-4">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => seekTo(Math.max(0, currentTime - 10))}
              >
                <SkipBack className="w-4 h-4" />
              </Button>
              
              <Button 
                variant="outline"
                onClick={togglePlayPause}
                className="w-12 h-12"
              >
                {isPlaying ? (
                  <Pause className="w-6 h-6" />
                ) : (
                  <Play className="w-6 h-6" />
                )}
              </Button>

              <Button 
                variant="outline" 
                size="sm"
                onClick={stopPlayback}
              >
                <Square className="w-4 h-4" />
              </Button>

              <Button 
                variant="outline" 
                size="sm"
                onClick={() => seekTo(Math.min(projectSettings.duration, currentTime + 10))}
              >
                <SkipForward className="w-4 h-4" />
              </Button>

              <Separator orientation="vertical" className="h-8" />

              <div className="flex items-center gap-2">
                <span className="text-sm font-mono">
                  {formatTime(currentTime)}
                </span>
                <span className="text-gray-400">/</span>
                <span className="text-sm font-mono text-gray-400">
                  {formatTime(projectSettings.duration)}
                </span>
              </div>

              <Separator orientation="vertical" className="h-8" />

              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleMute}
                >
                  {isMuted || volume === 0 ? (
                    <VolumeX className="w-4 h-4" />
                  ) : (
                    <Volume2 className="w-4 h-4" />
                  )}
                </Button>
                <Slider
                  value={[volume]}
                  onValueChange={handleVolumeChange}
                  max={100}
                  step={1}
                  className="w-20"
                />
                <span className="text-xs w-8">{volume}%</span>
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-gray-900 p-4 border-t border-gray-700 h-48">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium">Timeline</h3>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm">
                  <Scissors className="w-4 h-4" />
                </Button>
                <Button variant="outline" size="sm">
                  <Layers className="w-4 h-4" />
                </Button>
              </div>
            </div>

            <div ref={timelineRef} className="relative bg-gray-800 rounded h-32 overflow-x-auto">
              {/* Timeline Ruler */}
              <div className="absolute top-0 left-0 right-0 h-6 bg-gray-700 border-b border-gray-600">
                {Array.from({ length: Math.ceil(projectSettings.duration / 10) }, (_, i) => (
                  <div
                    key={i}
                    className="absolute text-xs text-gray-400 px-1"
                    style={{ left: `${(i * 10 / projectSettings.duration) * 100}%` }}
                  >
                    {formatTime(i * 10)}
                  </div>
                ))}
              </div>

              {/* Playhead */}
              <div
                className="absolute top-0 bottom-0 w-0.5 bg-red-500 z-10"
                style={{ left: `${(currentTime / projectSettings.duration) * 100}%` }}
              />

              {/* Video Tracks */}
              <div className="absolute top-6 left-0 right-0 bottom-0">
                {clips.map((clip, index) => (
                  <div
                    key={clip.id}
                    className={`absolute h-8 bg-blue-600 rounded border border-blue-500 cursor-pointer flex items-center px-2 ${
                      selectedClip === clip.id ? 'ring-2 ring-blue-400' : ''
                    }`}
                    style={{
                      left: `${(clip.startTime / projectSettings.duration) * 100}%`,
                      width: `${((clip.endTime - clip.startTime) / projectSettings.duration) * 100}%`,
                      top: `${(clip.layer * 32) + 8}px`
                    }}
                    onClick={() => setSelectedClip(clip.id)}
                  >
                    <span className="text-xs truncate text-white">{clip.name}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar Right - Properties */}
        <Card className="w-80 bg-gray-800 border-gray-700 rounded-none">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Propriedades</CardTitle>
          </CardHeader>
          <CardContent>
            {selectedClip ? (
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-gray-400">Nome do Clipe</label>
                  <input 
                    type="text" 
                    className="w-full mt-1 px-3 py-1 bg-gray-700 border border-gray-600 rounded text-sm"
                    value={clips.find(c => c.id === selectedClip)?.name || ''}
                    onChange={(e) => {
                      setClips(prev => prev.map(clip => 
                        clip.id === selectedClip 
                          ? { ...clip, name: e.target.value }
                          : clip
                      ));
                    }}
                  />
                </div>

                <div>
                  <label className="text-xs text-gray-400">Volume</label>
                  <Slider
                    value={[clips.find(c => c.id === selectedClip)?.volume || 100]}
                    onValueChange={(value) => {
                      setClips(prev => prev.map(clip => 
                        clip.id === selectedClip 
                          ? { ...clip, volume: value[0] }
                          : clip
                      ));
                    }}
                    max={100}
                    step={1}
                    className="mt-2"
                  />
                </div>

                <Button 
                  variant="destructive" 
                  size="sm" 
                  className="w-full"
                  onClick={() => selectedClip && removeClip(selectedClip)}
                >
                  Remover Clipe
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-gray-400">Resolução</label>
                  <p className="text-sm">{projectSettings.resolution.width} x {projectSettings.resolution.height}</p>
                </div>
                
                <div>
                  <label className="text-xs text-gray-400">Frame Rate</label>
                  <p className="text-sm">{projectSettings.frameRate} fps</p>
                </div>

                <div>
                  <label className="text-xs text-gray-400">Duração</label>
                  <p className="text-sm">{formatTime(projectSettings.duration)}</p>
                </div>

                <Button variant="outline" size="sm" className="w-full">
                  <Settings className="w-4 h-4 mr-2" />
                  Configurações do Projeto
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default VideoEditor;
