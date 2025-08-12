
# Mega Man X (Pygame) – Fan Game

**Controles:** A/D ou ←/→ para correr, ESC para sair.

## Como rodar
1. Crie um ambiente e instale o pygame:
   ```bash
   python -m venv .venv
   .venv/Scripts/activate  # Windows
   source .venv/bin/activate  # macOS/Linux

   pip install pygame
   ```

2. **[Opcional] Adicione um background:**
   - Salve sua imagem de background como `assets/background.png`
   - O jogo irá carregar automaticamente e aplicar efeito parallax

3. Execute:
   ```bash
   python main.py
   ```

## Características
- **Background com Parallax**: Coloque uma imagem PNG na pasta `assets/background.png` e ela será exibida com efeito de profundidade
- **Animações suaves**: Os frames de corrida foram recortados automaticamente da **3ª linha** da spritesheet
- **Controles responsivos**: Movimento, pulo, dash e tiro implementados

Os frames de corrida estão definidos na lista `run_rects` dentro do código.
Você pode ajustar `SCALE`, `SPEED` e o `GROUND_Y` nas configurações conforme necessário.
