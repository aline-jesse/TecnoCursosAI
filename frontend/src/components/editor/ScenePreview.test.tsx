import { render } from '@testing-library/react';
import ScenePreview from './ScenePreview';

describe('ScenePreview', () => {
  it('renderiza texto e imagem no canvas', () => {
    const scene = {
      texto: 'Teste de preview',
      imagens: ['https://via.placeholder.com/480x270.png?text=Slide'],
      background: '#fffbe6',
    };
    const { container } = render(<ScenePreview scene={scene} />);
    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
    // Não é possível testar visualmente o canvas, mas garante que está presente
  });
});
