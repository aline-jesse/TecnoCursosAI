import axios from 'axios';
import React, { useEffect, useState } from 'react';

interface Project {
  id: number;
  name: string;
}
interface Video {
  id: number;
  title: string;
  status: string;
  file_path: string;
  created_at?: string;
}

// Tela de histórico/lista de projetos e vídeos exportados
const ProjectHistory: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [videos, setVideos] = useState<Record<number, Video[]>>({});
  const [loading, setLoading] = useState(true);

  // Busca projetos e vídeos exportados
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const projRes = await axios.get('/api/projects');
      setProjects(projRes.data);
      const vids: Record<number, Video[]> = {};
      for (const p of projRes.data) {
        const vRes = await axios.get(`/api/projects/${p.id}/videos`);
        vids[p.id] = vRes.data;
      }
      setVideos(vids);
      setLoading(false);
    };
    fetchData();
  }, []);

  return (
    <div style={{ padding: 24, maxWidth: 900, margin: '0 auto' }}>
      <h2>Histórico de Projetos e Exportações</h2>
      {loading ? <div>Carregando...</div> : (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 24 }}>
          {projects.map((project) => (
            <div key={project.id} style={{ flex: '1 1 320px', background: '#fafbfc', borderRadius: 8, boxShadow: '0 2px 8px #0001', padding: 16 }}>
              <h3 style={{ margin: 0 }}>{project.name}</h3>
              <div style={{ fontSize: 13, color: '#888', marginBottom: 8 }}>ID: {project.id}</div>
              <div>
                {(videos[project.id] || []).length === 0 && <div style={{ color: '#aaa' }}>Nenhum vídeo exportado ainda.</div>}
                {(videos[project.id] || []).map((video) => (
                  <div key={video.id} style={{ marginBottom: 10, borderBottom: '1px solid #eee', paddingBottom: 8 }}>
                    <div style={{ fontWeight: 600 }}>{video.title}</div>
                    <div style={{ fontSize: 12, color: video.status === 'completed' ? '#4caf50' : '#fbc02d' }}>
                      Status: {video.status}
                    </div>
                    {video.status === 'completed' && (
                      <>
                        <a href={video.file_path} target="_blank" rel="noopener noreferrer" style={{ color: '#1976d2', fontWeight: 500, marginRight: 12 }}>Download</a>
                        <button style={{ fontSize: 12, padding: '2px 8px' }} onClick={() => navigator.clipboard.writeText(window.location.origin + video.file_path)}>Compartilhar</button>
                      </>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProjectHistory;
