import pygame as pg
import os
import random

TELA_LARGURA = 500
TELA_ALTURA = 800

IMAGEM_CANO = pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'pipe.png')))
IMAGEM_CHAO = pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'base.png')))
IMAGEM_BACKGROUND = pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bg.png')))
IMAGENS_PASSARO = [
    pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'atizapi.png'))),
    pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'atizapi.png'))),
    pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'atizapi.png'))),
]

pg.font.init()
FONTE_PONTOS = pg.font.SysFont('arial', 50)


class Passaro:
    IMGS = IMAGENS_PASSARO
    # animações da rotação
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        # calcular o deslocamento
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo

        # restringir o deslocamento
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        # o angulo do passaro
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        # definir qual imagem do passaro vai usar
        self.contagem_imagem += 1

        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem >= self.TEMPO_ANIMACAO*4 + 1:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0


        # se o passaro tiver caindo eu não vou bater asa
        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO*2

        # desenhar a imagem
        imagem_rotacionada = pg.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pg.mask.from_surface(self.imagem)


class Cano:
    DISTANCIA = 200
    VELOCIDADE = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = pg.transform.flip(IMAGEM_CANO, False, True)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pg.mask.from_surface(self.CANO_TOPO)
        base_mask = pg.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return False


class Chao:
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))


def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)

    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))
    chao.desenhar(tela)
    pg.display.update()

def iniciar_jogo():
    """Função para inicializar ou reiniciar o estado do jogo."""
    return [Passaro(230, 350)], Chao(730), [Cano(700)], 0, False # passaros, chao, canos, pontos, game_over

def main():
    tela = pg.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    relogio = pg.time.Clock()

    rodando = True
    
    passaros, chao, canos, pontos, game_over = iniciar_jogo() # Inicializa o jogo

    while rodando:
        relogio.tick(30)

        if not game_over: # Se o jogo NÃO acabou, processa a lógica normal do jogo
            for evento in pg.event.get():
                if evento.type == pg.QUIT:
                    rodando = False
                if evento.type == pg.KEYDOWN:
                    if evento.key == pg.K_SPACE:
                        for passaro in passaros:
                            passaro.pular()

            # Mover as coisas
            for passaro in passaros:
                passaro.mover()
            chao.mover()

            adicionar_cano = False
            remover_canos = []
            for cano in canos:
                for i, passaro in enumerate(passaros):
                    if cano.colidir(passaro):
                        passaros.pop(i)
                        game_over = True # O jogo acaba ao colidir com o cano
                        break # Sai do loop interno se o passaro colidiu
                
                # Se o game_over foi setado aqui, não precisamos processar mais este cano ou adicionar novos
                if game_over:
                    break

                if not cano.passou and len(passaros) > 0 and passaros[0].x > cano.x: # Verifica se ainda há pássaros
                    cano.passou = True
                    adicionar_cano = True
                cano.mover()
                if cano.x + cano.CANO_TOPO.get_width() < 0:
                    remover_canos.append(cano)
            
            if adicionar_cano:
                pontos += 1
                canos.append(Cano(600))
            for cano in remover_canos:
                canos.remove(cano)

            for i, passaro in enumerate(passaros):
                if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                    passaros.pop(i)
                    game_over = True # O jogo acaba ao tocar no chão ou sair da tela para cima

            if not passaros and not game_over: # Se não há mais pássaros e não setamos game_over antes (ex: por colisão)
                game_over = True

            desenhar_tela(tela, passaros, canos, chao, pontos)
        
        else: # Se o jogo acabou (game_over é True)
            # Desenha a tela de Game Over
            tela.fill((0, 0, 0))
            texto_game_over = FONTE_PONTOS.render("Game Over!", 1, (255, 255, 255))
            tela.blit(texto_game_over, (TELA_LARGURA // 2 - texto_game_over.get_width() // 2, TELA_ALTURA // 2 - texto_game_over.get_height() // 2))
            
            texto_reiniciar = FONTE_PONTOS.render("Pressione ENTER para reiniciar", 1, (255, 255, 255))
            tela.blit(texto_reiniciar, (TELA_LARGURA // 2 - texto_reiniciar.get_width() // 2, TELA_ALTURA // 2 + 50))
            pg.display.update()

            # Processa eventos APENAS para reiniciar ou sair
            for evento in pg.event.get():
                if evento.type == pg.QUIT:
                    rodando = False
                elif evento.type == pg.KEYDOWN:
                    if evento.key == pg.K_RETURN: # Detecta a tecla ENTER para reiniciar
                        passaros, chao, canos, pontos, game_over = iniciar_jogo() # Reinicia o jogo
                        
    pg.quit()
    quit()

if __name__ == '__main__':
    main()
