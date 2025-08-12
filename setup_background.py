"""Script para salvar a imagem do background"""
import base64
from pathlib import Path

# Esta é a imagem do background que você forneceu
# Você precisa substituir esta parte com os dados reais da imagem
def save_background_image():
    """Salva a imagem do background na pasta assets."""
    assets_path = Path(__file__).parent / "assets"
    bg_path = assets_path / "background.png"
    
    print(f"Para adicionar o background ao jogo:")
    print(f"1. Salve a imagem do background como: {bg_path}")
    print(f"2. Certifique-se de que a imagem está no formato PNG")
    print(f"3. Execute o jogo novamente")
    print(f"\nO sistema de background já foi implementado!")
    print(f"A imagem será repetida horizontalmente com efeito parallax.")

if __name__ == "__main__":
    save_background_image()
