/**
 * Teste simples para verificar se o Jest está funcionando
 */

describe('Teste Simples', () => {
  test('deve passar', () => {
    expect(1 + 1).toBe(2);
  });

  test('deve fazer operação matemática', () => {
    expect(5 * 3).toBe(15);
  });
}); 