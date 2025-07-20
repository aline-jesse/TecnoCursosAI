/**
 * EditorCanvas.jsx
 * Canvas editável para cenas: arrastar, redimensionar, rotacionar, editar e excluir elementos.
 * Inclui funções de controle para adicionar/remover/editar elementos e alterar ordem de camadas.
 *
 * Comentários detalhados para facilitar manutenção e entendimento.
 */
import React, { useRef, useEffect, useState, useCallback } from 'react';

// Tipos básicos para elementos
const ELEMENT_TYPE = {
  IMAGE: 'image',
  AVATAR: 'avatar',
  TEXT: 'text',
};

/**
 * Verifica se um ponto (x, y) está dentro do bounding box de um objeto.
 */
function isInside(x, y, obj) {
  return (
    x >= obj.x &&
    x <= obj.x + obj.width &&
    y >= obj.y &&
    y <= obj.y + obj.height
  );
}

const HANDLE_SIZE = 10; // Tamanho dos handles de resize

/**
 * Componente principal do canvas editável.
 * Props:
 *  - activeScene: cena ativa (com lista de objetos)
 *  - onUpdateScene: função para atualizar a cena (sincroniza estado global)
 *  - assets: lista de assets disponíveis (imagens, avatares, etc)
 */
export default function EditorCanvas({ activeScene, onUpdateScene, assets }) {
  // Referência para o elemento canvas
  const canvasRef = useRef(null);
  // Estado para controle de drag/movimentação
  const [draggedId, setDraggedId] = useState(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  // Estado para seleção e edição
  const [selectedId, setSelectedId] = useState(null);
  const [resizeHandle, setResizeHandle] = useState(null); // Qual handle está sendo usado para resize
  const [editingTextId, setEditingTextId] = useState(null); // ID do texto em edição
  const [editTextValue, setEditTextValue] = useState(''); // Valor do input de texto

  // ==================== Funções de Controle ====================

  /**
   * Adiciona um avatar à cena, usando um assetId do painel de assets.
   */
  function handleAddAvatar(assetId) {
    const asset = assets.find(a => a.id === assetId);
    if (!asset) return;
    const newObj = {
      id: `obj_${Date.now()}`,
      type: 'avatar',
      assetId,
      x: 100,
      y: 100,
      width: 120,
      height: 180,
      rotation: 0,
      zIndex: activeScene.objects.length,
    };
    onUpdateScene({ ...activeScene, objects: [...activeScene.objects, newObj] });
  }

  /**
   * Adiciona uma imagem à cena, usando um assetId do painel de assets.
   */
  function handleAddImage(assetId) {
    const asset = assets.find(a => a.id === assetId);
    if (!asset) return;
    const newObj = {
      id: `obj_${Date.now()}`,
      type: 'image',
      assetId,
      x: 150,
      y: 150,
      width: 200,
      height: 120,
      rotation: 0,
      zIndex: activeScene.objects.length,
    };
    onUpdateScene({ ...activeScene, objects: [...activeScene.objects, newObj] });
  }

  /**
   * Adiciona um texto à cena e ativa edição inline imediatamente.
   */
  function handleAddText() {
    const newObj = {
      id: `obj_${Date.now()}`,
      type: 'text',
      text: 'Novo texto',
      x: 200,
      y: 200,
      width: 200,
      height: 40,
      fontSize: 28,
      fontFamily: 'Arial',
      color: '#222',
      rotation: 0,
      zIndex: activeScene.objects.length,
    };
    onUpdateScene({ ...activeScene, objects: [...activeScene.objects, newObj] });
    setTimeout(() => setEditingTextId(newObj.id), 100); // Ativa input de edição
  }

  /**
   * Remove o elemento selecionado da cena.
   */
  function handleDeleteSelected() {
    if (!selectedId) return;
    const objects = activeScene.objects.filter(o => o.id !== selectedId);
    onUpdateScene({ ...activeScene, objects });
    setSelectedId(null);
  }

  /**
   * Move o elemento selecionado para o topo da pilha (última camada).
   */
  function bringToFront(id) {
    const idx = activeScene.objects.findIndex(o => o.id === id);
    if (idx === -1) return;
    const objects = [...activeScene.objects];
    const [obj] = objects.splice(idx, 1);
    objects.push(obj);
    onUpdateScene({ ...activeScene, objects });
  }

  /**
   * Move o elemento selecionado para o fundo da pilha (primeira camada).
   */
  function sendToBack(id) {
    const idx = activeScene.objects.findIndex(o => o.id === id);
    if (idx === -1) return;
    const objects = [...activeScene.objects];
    const [obj] = objects.splice(idx, 1);
    objects.unshift(obj);
    onUpdateScene({ ...activeScene, objects });
  }

  /**
   * Handler para drop de asset do painel de assets no canvas.
   * Espera que o painel de assets use dataTransfer com assetId e assetType.
   */
  function handleDrop(e) {
    e.preventDefault();
    const assetId = e.dataTransfer.getData('assetId');
    const assetType = e.dataTransfer.getData('assetType');
    if (assetType === ELEMENT_TYPE.AVATAR) handleAddAvatar(assetId);
    if (assetType === ELEMENT_TYPE.IMAGE) handleAddImage(assetId);
  }
  function handleDragOver(e) { e.preventDefault(); }

  // ==================== Renderização e Eventos do Canvas ====================

  /**
   * Redesenha toda a cena no canvas, incluindo elementos, seleção e handles.
   */
  const drawScene = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !activeScene) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Desenha todos os objetos da cena
    activeScene.objects.forEach((obj) => {
      ctx.save();
      // Aplica rotação e centraliza
      ctx.translate(obj.x + obj.width / 2, obj.y + obj.height / 2);
      ctx.rotate((obj.rotation || 0) * Math.PI / 180);
      ctx.translate(-obj.width / 2, -obj.height / 2);
      // Desenha imagem/avatar
      if (obj.type === ELEMENT_TYPE.IMAGE || obj.type === ELEMENT_TYPE.AVATAR) {
        const asset = assets.find(a => a.id === obj.assetId);
        if (asset && asset.url) {
          const img = new window.Image();
          img.src = asset.url;
          ctx.drawImage(img, 0, 0, obj.width, obj.height);
        } else {
          ctx.fillStyle = '#eee';
          ctx.fillRect(0, 0, obj.width, obj.height);
        }
      } else if (obj.type === ELEMENT_TYPE.TEXT) {
        // Desenha texto
        ctx.font = `${obj.fontSize || 24}px ${obj.fontFamily || 'Arial'}`;
        ctx.fillStyle = obj.color || '#222';
        ctx.textBaseline = 'top';
        ctx.fillText(obj.text || '', 0, 0, obj.width);
      }
      // Se selecionado, desenha borda e handles
      if (obj.id === selectedId) {
        ctx.strokeStyle = '#007bff';
        ctx.lineWidth = 2;
        ctx.strokeRect(0, 0, obj.width, obj.height);
        // Handles de resize nos cantos
        ctx.fillStyle = '#fff';
        ctx.strokeStyle = '#007bff';
        [
          [0, 0],
          [obj.width, 0],
          [0, obj.height],
          [obj.width, obj.height],
        ].forEach(([hx, hy]) => {
          ctx.beginPath();
          ctx.arc(hx, hy, HANDLE_SIZE, 0, 2 * Math.PI);
          ctx.fill();
          ctx.stroke();
        });
      }
      ctx.restore();
    });
  }, [activeScene, assets, selectedId]);

  // Redesenha sempre que a cena, seleção ou assets mudarem
  useEffect(() => { drawScene(); }, [drawScene]);

  /**
   * Retorna a posição do mouse relativa ao canvas.
   */
  const getMousePos = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
  };

  /**
   * Handler para mouseDown: seleciona elemento ou inicia drag/resize.
   */
  const handleMouseDown = (e) => {
    const pos = getMousePos(e);
    // Primeiro verifica se clicou em algum handle de resize
    for (const obj of [...activeScene.objects].reverse()) {
      if (obj.id === selectedId) {
        const handlePos = [
          { name: 'br', x: obj.x + obj.width, y: obj.y + obj.height },
          { name: 'tr', x: obj.x + obj.width, y: obj.y },
          { name: 'bl', x: obj.x, y: obj.y + obj.height },
          { name: 'tl', x: obj.x, y: obj.y },
        ];
        for (const h of handlePos) {
          if (
            Math.abs(pos.x - h.x) < HANDLE_SIZE &&
            Math.abs(pos.y - h.y) < HANDLE_SIZE
          ) {
            setResizeHandle(h.name);
            setDraggedId(obj.id);
            return;
          }
        }
      }
    }
    // Se não clicou em handle, verifica se clicou em algum objeto para selecionar/mover
    for (const obj of [...activeScene.objects].reverse()) {
      if (isInside(pos.x, pos.y, obj)) {
        setSelectedId(obj.id);
        setDraggedId(obj.id);
        setDragOffset({ x: pos.x - obj.x, y: pos.y - obj.y });
        return;
      }
    }
    // Se clicou fora, deseleciona
    setSelectedId(null);
  };

  /**
   * Handler para mouseMove: move ou redimensiona elemento enquanto arrasta.
   */
  const handleMouseMove = (e) => {
    if (!draggedId) return;
    const pos = getMousePos(e);
    const idx = activeScene.objects.findIndex((o) => o.id === draggedId);
    if (idx === -1) return;
    const objects = [...activeScene.objects];
    const obj = { ...objects[idx] };
    if (resizeHandle) {
      // Redimensionamento simples (canto inferior direito)
      if (resizeHandle === 'br') {
        obj.width = Math.max(20, pos.x - obj.x);
        obj.height = Math.max(20, pos.y - obj.y);
      }
      // TODO: outros handles (tr, bl, tl)
    } else {
      // Movimentação
      obj.x = pos.x - dragOffset.x;
      obj.y = pos.y - dragOffset.y;
    }
    objects[idx] = obj;
    onUpdateScene({ ...activeScene, objects });
  };

  /**
   * Handler para mouseUp: finaliza drag/resize.
   */
  const handleMouseUp = () => {
    setDraggedId(null);
    setResizeHandle(null);
  };

  /**
   * Handler para duplo clique: ativa edição inline de texto.
   */
  const handleDoubleClick = (e) => {
    const pos = getMousePos(e);
    for (const obj of activeScene.objects) {
      if (obj.type === ELEMENT_TYPE.TEXT && isInside(pos.x, pos.y, obj)) {
        setEditingTextId(obj.id);
        setEditTextValue(obj.text || '');
        return;
      }
    }
  };

  /**
   * Handler para alteração do input de texto inline.
   */
  const handleTextEditChange = (e) => setEditTextValue(e.target.value);
  /**
   * Handler para blur do input de texto: salva alteração no objeto.
   */
  const handleTextEditBlur = () => {
    if (!editingTextId) return;
    const idx = activeScene.objects.findIndex((o) => o.id === editingTextId);
    if (idx === -1) return;
    const objects = [...activeScene.objects];
    objects[idx] = { ...objects[idx], text: editTextValue };
    onUpdateScene({ ...activeScene, objects });
    setEditingTextId(null);
  };

  /**
   * Handler global para tecla Delete: remove elemento selecionado.
   */
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Delete' && selectedId) handleDeleteSelected();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedId, activeScene]);

  /**
   * Renderiza input de texto inline sobre o canvas para edição de texto.
   */
  const renderTextInput = () => {
    if (!editingTextId) return null;
    const obj = activeScene.objects.find((o) => o.id === editingTextId);
    if (!obj) return null;
    return (
      <input
        type="text"
        value={editTextValue}
        onChange={handleTextEditChange}
        onBlur={handleTextEditBlur}
        style={{
          position: 'absolute',
          left: obj.x,
          top: obj.y,
          width: obj.width,
          fontSize: obj.fontSize || 24,
          fontFamily: obj.fontFamily || 'Arial',
          color: obj.color || '#222',
          zIndex: 10,
        }}
        autoFocus
      />
    );
  };

  // ==================== UI de Controle ====================

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}
      onDrop={handleDrop} onDragOver={handleDragOver}>
      {/* Botões de controle do canvas */}
      <div style={{ position: 'absolute', top: 10, left: 10, zIndex: 20, display: 'flex', gap: 8 }}>
        <button onClick={handleAddText}>Adicionar Texto</button>
        <button onClick={handleDeleteSelected} disabled={!selectedId}>Excluir Selecionado</button>
        <button onClick={() => bringToFront(selectedId)} disabled={!selectedId}>Trazer para Frente</button>
        <button onClick={() => sendToBack(selectedId)} disabled={!selectedId}>Enviar para Trás</button>
      </div>
      {/* Canvas principal */}
      <canvas
        ref={canvasRef}
        width={activeScene.width || 1280}
        height={activeScene.height || 720}
        style={{
          border: '1px solid #ccc',
          background: activeScene.background || '#fff',
          width: '100%',
          height: '100%',
          display: 'block',
        }}
        tabIndex={0}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onDoubleClick={handleDoubleClick}
      />
      {/* Input de texto inline para edição */}
      {renderTextInput()}
    </div>
  );
} 