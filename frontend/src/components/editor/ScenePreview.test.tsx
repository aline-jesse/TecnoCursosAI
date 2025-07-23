import { render } from '@testing-library/react';
import ScenePreview from './ScenePreview';
import { Scene } from '../../types/editor';

describe('ScenePreview', () => {
  it('renderiza texto e imagem no canvas', () => {
    const scene: Scene = {
      id: '1',
      name: 'Test Scene',
      elements: [],
      background: {
        type: 'color',
        value: '#fffbe6',
      },
      texto: 'Teste de preview',
      imagens: ['https://via.placeholder.com/480x270.png?text=Slide'],
    };
    const { container } = render(<ScenePreview scene={scene} />);
    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
    // Não é possível testar visualmente o canvas, mas garante que está presente
  });
});
