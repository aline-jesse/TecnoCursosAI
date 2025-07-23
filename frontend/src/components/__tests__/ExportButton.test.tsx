import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import axios from 'axios';
import ExportButton from '../ExportButton';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('ExportButton', () => {
  it('deve exportar vídeo e exibir link de download', async () => {
    mockedAxios.post.mockResolvedValueOnce({});
    mockedAxios.get
      .mockResolvedValueOnce({ data: { status: 'processing' } })
      .mockResolvedValueOnce({ data: { status: 'completed', download_url: '/static/videos/final.mp4' } });
    render(<ExportButton projectId={1} />);
    fireEvent.click(screen.getByText('Exportar Vídeo'));
    expect(screen.getByText('Exportando...')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText('Exportação concluída!')).toBeInTheDocument(), { timeout: 4000 });
    expect(screen.getByText('Baixar vídeo exportado')).toBeInTheDocument();
  });
});
