/**
 * Properties Panel - Painel de propriedades do editor
 */

import React, { useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  Settings,
  Palette,
  Volume2,
  Move,
  RotateCw,
  Crop,
  Layers,
  Eye,
  EyeOff,
  Lock,
  Unlock,
  Trash2,
  Copy,
  Download
} from 'lucide-react';

interface ClipProperties {
  id: string;
  name: string;
  type: 'video' | 'audio' | 'image' | 'text';
  startTime: number;
  endTime: number;
  layer: number;
  volume?: number;
  opacity?: number;
  position?: {
    x: number;
    y: number;
    width: number;
    height: number;
    rotation: number;
  };
  effects?: string[];
  filters?: {
    brightness: number;
    contrast: number;
    saturation: number;
    hue: number;
    blur: number;
  };
  text?: {
    content: string;
    fontSize: number;
    fontFamily: string;
    color: string;
    backgroundColor: string;
    align: string;
    bold: boolean;
    italic: boolean;
  };
  visible: boolean;
  locked: boolean;
}

interface ProjectSettings {
  resolution: { width: number; height: number };
  frameRate: number;
  duration: number;
  backgroundColor: string;
  audioSampleRate: number;
}

interface PropertiesPanelProps {
  selectedClip: ClipProperties | null;
  projectSettings: ProjectSettings;
  onClipUpdate: (clipId: string, updates: Partial<ClipProperties>) => void;
  onProjectUpdate: (updates: Partial<ProjectSettings>) => void;
  onClipDelete: (clipId: string) => void;
  onClipDuplicate: (clipId: string) => void;
}

const PropertiesPanel: React.FC<PropertiesPanelProps> = ({
  selectedClip,
  projectSettings,
  onClipUpdate,
  onProjectUpdate,
  onClipDelete,
  onClipDuplicate
}) => {
  const [activeTab, setActiveTab] = useState('general');

  // Formatação de tempo
  const formatTime = useCallback((seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = (seconds % 60).toFixed(2);
    return `${mins.toString().padStart(2, '0')}:${parseFloat(secs).toFixed(2).padStart(5, '0')}`;
  }, []);

  const parseTime = useCallback((timeString: string) => {
    const [mins, secs] = timeString.split(':').map(parseFloat);
    return mins * 60 + secs;
  }, []);

  // Handlers para atualização de propriedades
  const updateClipProperty = useCallback((property: string, value: any) => {
    if (!selectedClip) return;
    
    const updates: any = {};
    
    // Propriedades aninhadas
    if (property.includes('.')) {
      const [parent, child] = property.split('.');
      updates[parent] = {
        ...selectedClip[parent as keyof ClipProperties],
        [child]: value
      };
    } else {
      updates[property] = value;
    }
    
    onClipUpdate(selectedClip.id, updates);
  }, [selectedClip, onClipUpdate]);

  if (!selectedClip) {
    return (
      <Card className="w-80 bg-gray-800 border-gray-700 rounded-none h-full">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm text-white flex items-center gap-2">
            <Settings className="w-4 h-4" />
            Propriedades do Projeto
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Configurações do Projeto */}
          <div className="space-y-3">
            <div>
              <Label className="text-xs text-gray-400">Resolução</Label>
              <Select
                value={`${projectSettings.resolution.width}x${projectSettings.resolution.height}`}
                onValueChange={(value) => {
                  const [width, height] = value.split('x').map(Number);
                  onProjectUpdate({ resolution: { width, height } });
                }}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1920x1080">1920x1080 (Full HD)</SelectItem>
                  <SelectItem value="1280x720">1280x720 (HD)</SelectItem>
                  <SelectItem value="3840x2160">3840x2160 (4K)</SelectItem>
                  <SelectItem value="1080x1920">1080x1920 (Vertical)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label className="text-xs text-gray-400">Frame Rate</Label>
              <Select
                value={projectSettings.frameRate.toString()}
                onValueChange={(value) => onProjectUpdate({ frameRate: parseInt(value) })}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="24">24 fps</SelectItem>
                  <SelectItem value="25">25 fps</SelectItem>
                  <SelectItem value="30">30 fps</SelectItem>
                  <SelectItem value="60">60 fps</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label className="text-xs text-gray-400">Duração do Projeto</Label>
              <Input
                type="text"
                value={formatTime(projectSettings.duration)}
                onChange={(e) => {
                  const duration = parseTime(e.target.value);
                  if (!isNaN(duration)) {
                    onProjectUpdate({ duration });
                  }
                }}
                className="mt-1"
              />
            </div>

            <div>
              <Label className="text-xs text-gray-400">Cor de Fundo</Label>
              <div className="flex gap-2 mt-1">
                <Input
                  type="color"
                  value={projectSettings.backgroundColor}
                  onChange={(e) => onProjectUpdate({ backgroundColor: e.target.value })}
                  className="w-12 h-8 p-1 rounded"
                />
                <Input
                  type="text"
                  value={projectSettings.backgroundColor}
                  onChange={(e) => onProjectUpdate({ backgroundColor: e.target.value })}
                  className="flex-1"
                />
              </div>
            </div>
          </div>

          <Separator />

          <div className="space-y-2">
            <Button variant="outline" className="w-full justify-start">
              <Download className="w-4 h-4 mr-2" />
              Exportar Projeto
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-80 bg-gray-800 border-gray-700 rounded-none h-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm text-white flex items-center gap-2">
          <Layers className="w-4 h-4" />
          Propriedades do Clipe
          <Badge variant="secondary" className="ml-auto">
            {selectedClip.type}
          </Badge>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="p-0">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 bg-gray-700 rounded-none">
            <TabsTrigger value="general" className="text-xs">Geral</TabsTrigger>
            <TabsTrigger value="transform" className="text-xs">Transform</TabsTrigger>
            <TabsTrigger value="effects" className="text-xs">Efeitos</TabsTrigger>
            <TabsTrigger value="audio" className="text-xs">Áudio</TabsTrigger>
          </TabsList>

          {/* Tab Geral */}
          <TabsContent value="general" className="mt-0 p-4 space-y-4">
            <div>
              <Label className="text-xs text-gray-400">Nome</Label>
              <Input
                value={selectedClip.name}
                onChange={(e) => updateClipProperty('name', e.target.value)}
                className="mt-1"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <Label className="text-xs text-gray-400">Início</Label>
                <Input
                  type="text"
                  value={formatTime(selectedClip.startTime)}
                  onChange={(e) => {
                    const time = parseTime(e.target.value);
                    if (!isNaN(time)) {
                      updateClipProperty('startTime', time);
                    }
                  }}
                  className="mt-1"
                />
              </div>
              <div>
                <Label className="text-xs text-gray-400">Fim</Label>
                <Input
                  type="text"
                  value={formatTime(selectedClip.endTime)}
                  onChange={(e) => {
                    const time = parseTime(e.target.value);
                    if (!isNaN(time)) {
                      updateClipProperty('endTime', time);
                    }
                  }}
                  className="mt-1"
                />
              </div>
            </div>

            <div>
              <Label className="text-xs text-gray-400">Camada</Label>
              <Input
                type="number"
                min="0"
                max="10"
                value={selectedClip.layer}
                onChange={(e) => updateClipProperty('layer', parseInt(e.target.value))}
                className="mt-1"
              />
            </div>

            <div>
              <Label className="text-xs text-gray-400">Opacidade</Label>
              <div className="mt-2">
                <Slider
                  value={[selectedClip.opacity || 100]}
                  onValueChange={(value) => updateClipProperty('opacity', value[0])}
                  max={100}
                  step={1}
                />
                <div className="text-xs text-gray-400 mt-1">{selectedClip.opacity || 100}%</div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => updateClipProperty('visible', !selectedClip.visible)}
                >
                  {selectedClip.visible ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => updateClipProperty('locked', !selectedClip.locked)}
                >
                  {selectedClip.locked ? <Lock className="w-4 h-4" /> : <Unlock className="w-4 h-4" />}
                </Button>
              </div>
              
              <div className="flex items-center gap-1">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onClipDuplicate(selectedClip.id)}
                >
                  <Copy className="w-4 h-4" />
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => onClipDelete(selectedClip.id)}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {/* Propriedades específicas de texto */}
            {selectedClip.type === 'text' && (
              <>
                <Separator />
                <div>
                  <Label className="text-xs text-gray-400">Conteúdo</Label>
                  <Textarea
                    value={selectedClip.text?.content || ''}
                    onChange={(e) => updateClipProperty('text.content', e.target.value)}
                    className="mt-1 min-h-20"
                    placeholder="Digite o texto aqui..."
                  />
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <Label className="text-xs text-gray-400">Fonte</Label>
                    <Select
                      value={selectedClip.text?.fontFamily || 'Arial'}
                      onValueChange={(value) => updateClipProperty('text.fontFamily', value)}
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Arial">Arial</SelectItem>
                        <SelectItem value="Helvetica">Helvetica</SelectItem>
                        <SelectItem value="Times New Roman">Times New Roman</SelectItem>
                        <SelectItem value="Georgia">Georgia</SelectItem>
                        <SelectItem value="Verdana">Verdana</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <Label className="text-xs text-gray-400">Tamanho</Label>
                    <Input
                      type="number"
                      min="8"
                      max="200"
                      value={selectedClip.text?.fontSize || 32}
                      onChange={(e) => updateClipProperty('text.fontSize', parseInt(e.target.value))}
                      className="mt-1"
                    />
                  </div>
                </div>

                <div>
                  <Label className="text-xs text-gray-400">Cor do Texto</Label>
                  <div className="flex gap-2 mt-1">
                    <Input
                      type="color"
                      value={selectedClip.text?.color || '#ffffff'}
                      onChange={(e) => updateClipProperty('text.color', e.target.value)}
                      className="w-12 h-8 p-1 rounded"
                    />
                    <Input
                      type="text"
                      value={selectedClip.text?.color || '#ffffff'}
                      onChange={(e) => updateClipProperty('text.color', e.target.value)}
                      className="flex-1"
                    />
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Switch
                      checked={selectedClip.text?.bold || false}
                      onCheckedChange={(value) => updateClipProperty('text.bold', value)}
                    />
                    <Label className="text-xs">Negrito</Label>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Switch
                      checked={selectedClip.text?.italic || false}
                      onCheckedChange={(value) => updateClipProperty('text.italic', value)}
                    />
                    <Label className="text-xs">Itálico</Label>
                  </div>
                </div>
              </>
            )}
          </TabsContent>

          {/* Tab Transform */}
          <TabsContent value="transform" className="mt-0 p-4 space-y-4">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <Label className="text-xs text-gray-400">X</Label>
                <Input
                  type="number"
                  value={selectedClip.position?.x || 0}
                  onChange={(e) => updateClipProperty('position.x', parseFloat(e.target.value))}
                  className="mt-1"
                />
              </div>
              <div>
                <Label className="text-xs text-gray-400">Y</Label>
                <Input
                  type="number"
                  value={selectedClip.position?.y || 0}
                  onChange={(e) => updateClipProperty('position.y', parseFloat(e.target.value))}
                  className="mt-1"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <Label className="text-xs text-gray-400">Largura</Label>
                <Input
                  type="number"
                  min="1"
                  value={selectedClip.position?.width || 100}
                  onChange={(e) => updateClipProperty('position.width', parseFloat(e.target.value))}
                  className="mt-1"
                />
              </div>
              <div>
                <Label className="text-xs text-gray-400">Altura</Label>
                <Input
                  type="number"
                  min="1"
                  value={selectedClip.position?.height || 100}
                  onChange={(e) => updateClipProperty('position.height', parseFloat(e.target.value))}
                  className="mt-1"
                />
              </div>
            </div>

            <div>
              <Label className="text-xs text-gray-400">Rotação</Label>
              <div className="mt-2">
                <Slider
                  value={[selectedClip.position?.rotation || 0]}
                  onValueChange={(value) => updateClipProperty('position.rotation', value[0])}
                  min={-180}
                  max={180}
                  step={1}
                />
                <div className="text-xs text-gray-400 mt-1">{selectedClip.position?.rotation || 0}°</div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2">
              <Button variant="outline" size="sm">
                <Move className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="sm">
                <RotateCw className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="sm">
                <Crop className="w-4 h-4" />
              </Button>
            </div>
          </TabsContent>

          {/* Tab Efeitos */}
          <TabsContent value="effects" className="mt-0 p-4 space-y-4">
            {selectedClip.type !== 'audio' && (
              <>
                <div>
                  <Label className="text-xs text-gray-400">Brilho</Label>
                  <div className="mt-2">
                    <Slider
                      value={[selectedClip.filters?.brightness || 0]}
                      onValueChange={(value) => updateClipProperty('filters.brightness', value[0])}
                      min={-100}
                      max={100}
                      step={1}
                    />
                    <div className="text-xs text-gray-400 mt-1">{selectedClip.filters?.brightness || 0}%</div>
                  </div>
                </div>

                <div>
                  <Label className="text-xs text-gray-400">Contraste</Label>
                  <div className="mt-2">
                    <Slider
                      value={[selectedClip.filters?.contrast || 0]}
                      onValueChange={(value) => updateClipProperty('filters.contrast', value[0])}
                      min={-100}
                      max={100}
                      step={1}
                    />
                    <div className="text-xs text-gray-400 mt-1">{selectedClip.filters?.contrast || 0}%</div>
                  </div>
                </div>

                <div>
                  <Label className="text-xs text-gray-400">Saturação</Label>
                  <div className="mt-2">
                    <Slider
                      value={[selectedClip.filters?.saturation || 0]}
                      onValueChange={(value) => updateClipProperty('filters.saturation', value[0])}
                      min={-100}
                      max={100}
                      step={1}
                    />
                    <div className="text-xs text-gray-400 mt-1">{selectedClip.filters?.saturation || 0}%</div>
                  </div>
                </div>

                <div>
                  <Label className="text-xs text-gray-400">Desfoque</Label>
                  <div className="mt-2">
                    <Slider
                      value={[selectedClip.filters?.blur || 0]}
                      onValueChange={(value) => updateClipProperty('filters.blur', value[0])}
                      min={0}
                      max={20}
                      step={0.1}
                    />
                    <div className="text-xs text-gray-400 mt-1">{selectedClip.filters?.blur || 0}px</div>
                  </div>
                </div>
              </>
            )}

            <Separator />

            <div>
              <Label className="text-xs text-gray-400">Efeitos Aplicados</Label>
              <div className="mt-2 space-y-1">
                {selectedClip.effects?.map((effect, index) => (
                  <Badge key={index} variant="secondary" className="mr-1">
                    {effect}
                  </Badge>
                )) || <p className="text-xs text-gray-500">Nenhum efeito aplicado</p>}
              </div>
            </div>
          </TabsContent>

          {/* Tab Áudio */}
          <TabsContent value="audio" className="mt-0 p-4 space-y-4">
            <div>
              <Label className="text-xs text-gray-400">Volume</Label>
              <div className="mt-2">
                <Slider
                  value={[selectedClip.volume || 100]}
                  onValueChange={(value) => updateClipProperty('volume', value[0])}
                  max={200}
                  step={1}
                />
                <div className="text-xs text-gray-400 mt-1">{selectedClip.volume || 100}%</div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Switch
                checked={selectedClip.volume === 0}
                onCheckedChange={(muted) => updateClipProperty('volume', muted ? 0 : 100)}
              />
              <Label className="text-xs">Mudo</Label>
            </div>

            {selectedClip.type === 'audio' && (
              <>
                <Separator />
                
                <div>
                  <Label className="text-xs text-gray-400">Fade In (segundos)</Label>
                  <Input
                    type="number"
                    min="0"
                    max="10"
                    step="0.1"
                    defaultValue="0"
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label className="text-xs text-gray-400">Fade Out (segundos)</Label>
                  <Input
                    type="number"
                    min="0"
                    max="10"
                    step="0.1"
                    defaultValue="0"
                    className="mt-1"
                  />
                </div>
              </>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default PropertiesPanel;
