import axios from 'axios';
import React, { useState } from 'react';

interface ExportButtonProps {
  projectId: number;
}

const ExportButton: React.FC<ExportButtonProps> = ({ projectId }) => {
  const [exporting, setExporting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

  // Função para iniciar exportação
  const handleExport = async () => {
    setExporting(true);
    setStatus('Aguardando exportação...');
    setProgress(10);
    setDownloadUrl(null);
    try {
      await axios.post('/api/export-ia-async', { project_id: projectId });
      setStatus('Processando...');
      setProgress(30);
      // Polling para status
      const pollStatus = async () => {
        const res = await axios.get(`/api/export-ia-status/${projectId}`);
        if (res.data.status === 'completed') {
          setStatus('Exportação concluída!');
          setProgress(100);
          setDownloadUrl(res.data.download_url);
          setExporting(false);
        } else {
          setProgress((p) => Math.min(p + 10, 90));
          setTimeout(pollStatus, 2000);
        }
      };
      setTimeout(pollStatus, 2000);
    } catch (e) {
      setStatus('Erro ao exportar vídeo.');
      setExporting(false);
    }
  };

  return (
    <div style={{ margin: '1rem 0' }}>
      <button onClick={handleExport} disabled={exporting} style={{ padding: '0.5rem 1.5rem', fontSize: 16 }}>
        {exporting ? 'Exportando...' : 'Exportar Vídeo'}
      </button>
      {exporting && (
        <div style={{ marginTop: 8 }}>
          <div style={{ width: 200, height: 8, background: '#eee', borderRadius: 4 }}>
            <div style={{ width: `${progress}%`, height: 8, background: '#4caf50', borderRadius: 4, transition: 'width 0.5s' }} />
          </div>
          <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>{status}</div>
        </div>
      )}
      {downloadUrl && (
        <div style={{ marginTop: 12 }}>
          <a href={downloadUrl} target="_blank" rel="noopener noreferrer" style={{ color: '#1976d2', fontWeight: 600 }}>
            Baixar vídeo exportado
          </a>
        </div>
      )}
    </div>
  );
};

export default ExportButton;
