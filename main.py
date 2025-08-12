"""Ponto de entrada do jogo"""
from core.game import Game


def main():
    """Função principal."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()