
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
2. Execute:
   ```bash
   python main.py
   ```

Os frames de corrida foram recortados automaticamente da **3ª linha** da spritesheet e estão definidos na lista `run_rects` dentro do `main.py`.
Você pode ajustar `SCALE`, `SPEED` e o `GROUND_Y` conforme necessário.
