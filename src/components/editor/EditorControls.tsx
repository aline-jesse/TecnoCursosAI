import React, { useState } from 'react'
import {
  PlusIcon,
  PhotoIcon,
  DocumentTextIcon,
  SpeakerWaveIcon,
  UserIcon,
  Cog6ToothIcon,
  EyeIcon,
  EyeSlashIcon,
  TrashIcon
} from '@heroicons/react/24/outline'

interface EditorControlsProps {
  onAddElement?: (type: string) => void
  onToggleLayer?: (layerId: string) => void
  onDeleteSelected?: () => void
}

export const EditorControls: React.FC<EditorControlsProps> = ({
  onAddElement,
  onToggleLayer,
  onDeleteSelected
}) => {
  const [activeTab, setActiveTab] = useState<'elements' | 'layers' | 'settings'>('elements')

  const elementTypes = [
    { id: 'text', label: 'Texto', icon: DocumentTextIcon, color: '#3b82f6' },
    { id: 'image', label: 'Imagem', icon: PhotoIcon, color: '#10b981' },
    { id: 'audio', label: 'Áudio', icon: SpeakerWaveIcon, color: '#f59e0b' },
    { id: 'avatar', label: 'Avatar', icon: UserIcon, color: '#8b5cf6' }
  ]

  const mockLayers = [
    { id: 'layer-1', name: 'Fundo', visible: true, locked: false },
    { id: 'layer-2', name: 'Texto Principal', visible: true, locked: false },
    { id: 'layer-3', name: 'Avatar', visible: false, locked: true }
  ]

  const handleAddElement = (elementType: string) => {
    if (onAddElement) {
      onAddElement(elementType)
    }
  }

  const TabButton = ({ 
    tab, 
    label, 
    isActive 
  }: { 
    tab: typeof activeTab, 
    label: string, 
    isActive: boolean 
  }) => (
    <button
      onClick={() => setActiveTab(tab)}
      className={`tab-button ${isActive ? 'active' : ''}`}
      style={{
        padding: '0.5rem 1rem',
        border: 'none',
        background: isActive ? '#3b82f6' : 'transparent',
        color: isActive ? 'white' : '#64748b',
        borderRadius: '0.375rem',
        cursor: 'pointer',
        fontSize: '0.875rem',
        fontWeight: '500',
        transition: 'all 0.2s ease'
      }}
    >
      {label}
    </button>
  )

  return (
    <div className="editor-controls" style={{
      width: '100%',
      maxWidth: '320px',
      background: 'white',
      borderRadius: '0.5rem',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
      overflow: 'hidden'
    }}>
      {/* Header com tabs */}
      <div className="controls-header" style={{
        padding: '1rem',
        borderBottom: '1px solid #e2e8f0',
        background: '#f8fafc'
      }}>
        <h3 style={{
          margin: '0 0 0.75rem 0',
          fontSize: '1rem',
          fontWeight: '600',
          color: '#1e293b'
        }}>
          🎛️ Controles do Editor
        </h3>
        
        <div className="tab-buttons" style={{
          display: 'flex',
          gap: '0.25rem',
          background: '#e2e8f0',
          padding: '0.25rem',
          borderRadius: '0.375rem'
        }}>
          <TabButton tab="elements" label="Elementos" isActive={activeTab === 'elements'} />
          <TabButton tab="layers" label="Camadas" isActive={activeTab === 'layers'} />
          <TabButton tab="settings" label="Config" isActive={activeTab === 'settings'} />
        </div>
      </div>

      {/* Conteúdo dos tabs */}
      <div className="controls-content" style={{
        padding: '1rem',
        maxHeight: '400px',
        overflowY: 'auto'
      }}>
        {/* Tab: Elementos */}
        {activeTab === 'elements' && (
          <div className="elements-tab">
            <h4 style={{
              margin: '0 0 0.75rem 0',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: '#374151'
            }}>
              Adicionar Elementos
            </h4>
            
            <div className="element-grid" style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '0.5rem'
            }}>
              {elementTypes.map((element) => {
                const IconComponent = element.icon
                return (
                  <button
                    key={element.id}
                    onClick={() => handleAddElement(element.id)}
                    className="element-button"
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      padding: '0.75rem',
                      border: `2px solid ${element.color}20`,
                      borderRadius: '0.5rem',
                      background: `${element.color}10`,
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      fontSize: '0.75rem',
                      fontWeight: '500',
                      color: element.color
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-2px)'
                      e.currentTarget.style.boxShadow = `0 4px 12px ${element.color}30`
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)'
                      e.currentTarget.style.boxShadow = 'none'
                    }}
                  >
                    <IconComponent 
                      style={{ 
                        width: '1.5rem', 
                        height: '1.5rem', 
                        marginBottom: '0.25rem' 
                      }} 
                    />
                    {element.label}
                  </button>
                )
              })}
            </div>

            <div style={{ marginTop: '1rem' }}>
              <button
                onClick={onDeleteSelected}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: '#ef4444',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.375rem',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.5rem',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = '#dc2626'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = '#ef4444'
                }}
              >
                <TrashIcon style={{ width: '1rem', height: '1rem' }} />
                Excluir Selecionado
              </button>
            </div>
          </div>
        )}

        {/* Tab: Camadas */}
        {activeTab === 'layers' && (
          <div className="layers-tab">
            <h4 style={{
              margin: '0 0 0.75rem 0',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: '#374151'
            }}>
              Gerenciar Camadas
            </h4>
            
            <div className="layers-list" style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem'
            }}>
              {mockLayers.map((layer) => (
                <div
                  key={layer.id}
                  className="layer-item"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.5rem',
                    background: '#f8fafc',
                    borderRadius: '0.375rem',
                    border: '1px solid #e2e8f0'
                  }}
                >
                  <span style={{
                    fontSize: '0.875rem',
                    color: '#374151',
                    fontWeight: '500'
                  }}>
                    {layer.name}
                  </span>
                  
                  <div style={{ display: 'flex', gap: '0.25rem' }}>
                    <button
                      onClick={() => onToggleLayer && onToggleLayer(layer.id)}
                      style={{
                        padding: '0.25rem',
                        background: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        color: layer.visible ? '#10b981' : '#64748b',
                        transition: 'color 0.2s ease'
                      }}
                      title={layer.visible ? 'Ocultar camada' : 'Mostrar camada'}
                    >
                      {layer.visible ? (
                        <EyeIcon style={{ width: '1rem', height: '1rem' }} />
                      ) : (
                        <EyeSlashIcon style={{ width: '1rem', height: '1rem' }} />
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab: Configurações */}
        {activeTab === 'settings' && (
          <div className="settings-tab">
            <h4 style={{
              margin: '0 0 0.75rem 0',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: '#374151'
            }}>
              Configurações
            </h4>
            
            <div className="settings-list" style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '0.75rem'
            }}>
              {/* Canvas Size */}
              <div className="setting-group">
                <label style={{
                  fontSize: '0.75rem',
                  fontWeight: '500',
                  color: '#64748b',
                  marginBottom: '0.25rem',
                  display: 'block'
                }}>
                  Tamanho do Canvas
                </label>
                <select style={{
                  width: '100%',
                  padding: '0.5rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '0.375rem',
                  fontSize: '0.875rem',
                  background: 'white'
                }}>
                  <option>1920x1080 (Full HD)</option>
                  <option>1280x720 (HD)</option>
                  <option>800x600 (4:3)</option>
                  <option>1080x1080 (Quadrado)</option>
                </select>
              </div>

              {/* Background Color */}
              <div className="setting-group">
                <label style={{
                  fontSize: '0.75rem',
                  fontWeight: '500',
                  color: '#64748b',
                  marginBottom: '0.25rem',
                  display: 'block'
                }}>
                  Cor de Fundo
                </label>
                <input
                  type="color"
                  defaultValue="#ffffff"
                  style={{
                    width: '100%',
                    height: '2.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '0.375rem',
                    cursor: 'pointer'
                  }}
                />
              </div>

              {/* Snap to Grid */}
              <div className="setting-group">
                <label style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  fontSize: '0.875rem',
                  color: '#374151',
                  cursor: 'pointer'
                }}>
                  <input
                    type="checkbox"
                    defaultChecked
                    style={{
                      width: '1rem',
                      height: '1rem',
                      cursor: 'pointer'
                    }}
                  />
                  Snap to Grid
                </label>
              </div>

              {/* Show Rulers */}
              <div className="setting-group">
                <label style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  fontSize: '0.875rem',
                  color: '#374151',
                  cursor: 'pointer'
                }}>
                  <input
                    type="checkbox"
                    defaultChecked
                    style={{
                      width: '1rem',
                      height: '1rem',
                      cursor: 'pointer'
                    }}
                  />
                  Mostrar Réguas
                </label>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default EditorControls 