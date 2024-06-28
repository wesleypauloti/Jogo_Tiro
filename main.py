import pygame
import os
import random
import csv

project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)

pygame.init()

terra_path = os.path.join('img', 'terra')

TELA_LARGURA = 800
TELA_ALTURA = int(TELA_LARGURA * 0.8)

tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
pygame.display.set_caption('JOGO EM PYGAME :')

relogio = pygame.time.Clock()
FPS = 60

GRAVIDADE = 0.75
TERRA_TAMANHO = 40
LINHAS = 16
COLUNAS = 150
TERRA_TAMANHO = TELA_ALTURA // LINHAS
TERRA_TIPO = 21
nivel = 1

movimento_esquerda = False
movimento_direita = False
atirar = False
granada = False
granada_jogador = False

imagens_terra = []
numero_de_frames_terra = len(os.listdir(terra_path))
for x in range(numero_de_frames_terra):
    img = pygame.image.load(os.path.join(terra_path, f'{x}.png'))
    imagens_terra.append(img)

ultimo_lancamento_granada = 0
delay_entre_granadas = 1000

bala_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
granada_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
caixa_granada_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
caixa_municao_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
caixa_vida_img = pygame.image.load('img/icons/health_box.png').convert_alpha()

item_caixas = {
    'Vida': caixa_vida_img, 
    'Municao': caixa_municao_img, 
    'Granada': caixa_granada_img 
}

BG = (128, 128, 128)
GREEN = (60, 179, 113)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

def desenho_bg():
    tela.fill(BG)

font = pygame.font.SysFont('Futura', 25)

def desenhar_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    tela.blit(img, (x, y))

class Soldado(pygame.sprite.Sprite):
    def __init__(self, jogador_tipo, x, y, escala, velocidade, municao, granadas):
        pygame.sprite.Sprite.__init__(self)
        self.vivo = True
        self.jogador_tipo = jogador_tipo
        self.velocidade = velocidade
        self.municao = municao
        self.granadas = granadas
        self.vida = 100
        self.max_vida = self.vida
        self.direction = 1
        self.vel_y = 0
        self.pulando = False
        self.no_chao = False
        self.tiro = False
        self.granada = False
        self.granada_atirada = False
        self.atirar_fechado = False
        self.morto = False
        self.cima = False
        self.pular = False
        self.virar = False
        self.atirar_bala_count = 0 
        self.ultima_tentativa_tiro = pygame.time.get_ticks()
        self.ultima_tentativa_granada = pygame.time.get_ticks()
        self.animacao_lista = []
        self.frame_index = 0
        self.acao = 0
        self.direcao = 1
        self.move_counter = 0
        self.ocioso = False
        self.ocioso_counter = 0
        self.visao = pygame.Rect(0, 0, 150, 20)
        self.atualiza_tempo = pygame.time.get_ticks()

        tipos_de_animacao = ['Idle', 'Run', 'Jump', 'Death']
        for animacao in tipos_de_animacao:
            temp_lista = []
            numero_de_frames = len(os.listdir(os.path.join('img', self.jogador_tipo, animacao)))
            for i in range(numero_de_frames):
                img = pygame.image.load(os.path.join('img', self.jogador_tipo, animacao, f'{i}.png'))
                img = pygame.transform.scale(img, (int(img.get_width() * escala), int(img.get_height() * escala)))
                temp_lista.append(img)
            self.animacao_lista.append(temp_lista)
        
        self.image = self.animacao_lista[self.acao][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def atualizar(self):
        self.atualizar_animacao()
        self.checar_a_vida()
        if self.atirar_bala_count > 0:
            self.atirar_bala_count -= 1

    def movimento(self, movimento_esquerda, movimento_direita):
        dx = 0
        dy = 0

        if movimento_esquerda:
            dx = -self.velocidade
            self.virar = True
            self.direcao = -1
        if movimento_direita:
            dx = self.velocidade
            self.virar = False
            self.direcao = 1

        if self.pular == True and self.no_ar == False:
            self.vel_y = -11
            self.pular = False
            self.no_ar = True

        self.vel_y += GRAVIDADE
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.no_ar = False

        self.rect.x += dx
        self.rect.y += dy

    def atirar(self):
        if self.atirar_bala_count == 0 and self.municao > 0:
            self.atirar_bala_count = 20
            bala = Bala(self.rect.centerx + (0.6 * self.rect.size[0] * self.direcao), self.rect.centery, self.direcao)
            bala_grupo.add(bala)
            self.municao -= 1

    def ai_inimigo(self):
        if self.vivo and jogador.vivo:
            if self.ocioso == False and random.randint(1, 200) == 1:
                self.atualizar_acao(0)
                self.ocioso = True
                self.ocioso_counter = 50

            if self.visao.colliderect(jogador.rect):
                self.atualizar_acao(0)
                self.atirar()
            else:
                if self.ocioso == False:
                    if self.direcao == 1:
                        ai_inimigo_direita = True
                    else:
                        ai_inimigo_direita = False
                    ai_inimigo_esquerda = not ai_inimigo_direita
                    self.movimento(ai_inimigo_esquerda, ai_inimigo_direita)
                    self.atualizar_acao(1)
                    self.move_counter += 1

                    self.visao.center = (self.rect.centerx + 75 * self.direcao, self.rect.centery)
                    if self.move_counter > TERRA_TAMANHO:
                        self.direcao *= -1
                        self.move_counter *= -1
                else:
                    self.ocioso_counter -= 1
                    if self.ocioso_counter <= 0:
                        self.ocioso = False

    def atualizar_animacao(self):
        ANIMACAO_FRESH = 100
        self.image = self.animacao_lista[self.acao][self.frame_index]

        if pygame.time.get_ticks() - self.atualiza_tempo > ANIMACAO_FRESH:
            self.atualiza_tempo = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animacao_lista[self.acao]):
            if self.acao == 3:
                self.frame_index = len(self.animacao_lista[self.acao]) - 1
            else:
                self.frame_index = 0

    def atualizar_acao(self, new_action):
        if new_action != self.acao:
            self.acao = new_action
            self.frame_index = 0
            self.atualiza_tempo = pygame.time.get_ticks()

    def checar_a_vida(self):
        if self.vida <= 0:
            self.vida = 0
            self.velocidade = 0
            self.vivo = False
            self.atualizar_acao(3)

    def desenho(self):
        tela.blit(pygame.transform.flip(self.image, self.virar, False), self.rect)

class Mundo():
    def __init__(self):
        self.obstaculo_list = []

    def processo_data(self, data):
        for y, linha in enumerate(data):
            for x, terra in enumerate(linha):
                if terra >= 0:
                    img = imagens_terra[terra]
                    img_rect = img.get_rect()
                    img_rect.x = x * TERRA_TAMANHO
                    img_rect.y = y * TERRA_TAMANHO
                    terra = (img, img_rect)
                    self.obstaculo_list.append(terra)

    def desenho(self):
        for terra in self.obstaculo_list:
            tela.blit(terra[0], terra[1])

class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y, direcao):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bala_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direcao = direcao

    def update(self):
        self.rect.x += (self.direcao * self.speed)
        if self.rect.right < 0 or self.rect.left > TELA_LARGURA:
            self.kill()
        if pygame.sprite.spritecollide(jogador, bala_grupo, False):
            if jogador.vivo:
                jogador.vida -= 5
                self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direcao):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = granada_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direcao = direcao

    def update(self):
        self.vel_y += GRAVIDADE
        dx = self.direcao * self.speed
        dy = self.vel_y

        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.speed = 0

        if self.rect.left + dx < 0 or self.rect.right + dx > TELA_LARGURA:
            self.direcao *= -1
            dx = self.direcao * self.speed

        self.rect.x += dx
        self.rect.y += dy

        self.timer -= 1
        if self.timer <= 0:
            self.kill()

            explosao = Explosao(self.rect.x, self.rect.y, 0.5)
            explosao_grupo.add(explosao)
            if abs(self.rect.centerx - jogador.rect.centerx) < TERRA_TAMANHO * 2 and abs(self.rect.centery - jogador.rect.centery) < TERRA_TAMANHO * 2:
                jogador.vida -= 25

class Explosao(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'img/explode/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        ANIMACAO_FRESH = 4
        self.counter += 1

        if self.counter >= ANIMACAO_FRESH:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

bala_grupo = pygame.sprite.Group()
granada_grupo = pygame.sprite.Group()
explosao_grupo = pygame.sprite.Group()
item_caixa_grupo = pygame.sprite.Group()
inimigo_grupo = pygame.sprite.Group()

jogador = Soldado('jogador', 200, 200, 1.65, 5, 20, 5)
inimigo = Soldado('inimigo', 400, 200, 1.65, 2, 20, 0)
inimigo_grupo.add(inimigo)

mundo_data = []
for linha in range(LINHAS):
    r = [-1] * COLUNAS
    mundo_data.append(r)

with open(f'nivel{nivel}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            mundo_data[x][y] = int(tile)

mundo = Mundo()
mundo.processo_data(mundo_data)

run = True
while run:
    relogio.tick(FPS)
    desenho_bg()
    mundo.desenho()
    jogador.desenho()
    jogador.atualizar()
    jogador.movimento(movimento_esquerda, movimento_direita)
    inimigo.desenho()
    inimigo.atualizar()
    inimigo.ai_inimigo()

    bala_grupo.update()
    granada_grupo.update()
    explosao_grupo.update()
    item_caixa_grupo.update()
    bala_grupo.draw(tela)
    granada_grupo.draw(tela)
    explosao_grupo.draw(tela)
    item_caixa_grupo.draw(tela)

    desenhar_text(f'Municao: {jogador.municao}', font, GRAY, 10, 35)
    desenhar_text(f'Granadas: {jogador.granadas}', font, GRAY, 10, 60)

    jogador.vida += 1
    pygame.display.update()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            run = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_a:
                movimento_esquerda = True
            if evento.key == pygame.K_d:
                movimento_direita = True
            if evento.key == pygame.K_w and jogador.vivo:
                jogador.pular = True
            if evento.key == pygame.K_SPACE:
                atirar = True
            if evento.key == pygame.K_q:
                granada = True

        if evento.type == pygame.KEYUP:
            if evento.key == pygame.K_a:
                movimento_esquerda = False
            if evento.key == pygame.K_d:
                movimento_direita = False
            if evento.key == pygame.K_SPACE:
                atirar = False
            if evento.key == pygame.K_q:
                granada = False

    if atirar:
        jogador.atirar()
    if granada and jogador.granadas > 0:
        if pygame.time.get_ticks() - ultimo_lancamento_granada > delay_entre_granadas:
            granada_lancada = Grenade(jogador.rect.centerx + (jogador.rect.size[0] * jogador.direcao), jogador.rect.top, jogador.direcao)
            granada_grupo.add(granada_lancada)
            jogador.granadas -= 1
            ultimo_lancamento_granada = pygame.time.get_ticks()

pygame.quit()
