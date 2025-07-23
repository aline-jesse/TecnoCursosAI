import { render, screen, waitFor } from '@testing-library/react';
import axios from 'axios';
import ProjectHistory from '../ProjectHistory';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('ProjectHistory', () => {
  it('deve listar projetos e vídeos exportados', async () => {
    mockedAxios.get
      .mockResolvedValueOnce({ data: [ { id: 1, name: 'Projeto 1' } ] }) // projetos
      .mockResolvedValueOnce({ data: [ { id: 10, title: 'Vídeo 1', status: 'completed', file_path: '/static/videos/v1.mp4' } ] }); // vídeos
    render(<ProjectHistory />);
    await waitFor(() => expect(screen.getByText('Projeto 1')).toBeInTheDocument());
    expect(screen.getByText('Vídeo 1')).toBeInTheDocument();
    expect(screen.getByText('Download')).toBeInTheDocument();
    expect(screen.getByText('Compartilhar')).toBeInTheDocument();
  });
});
