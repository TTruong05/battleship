import numpy as np
import random
import time
import pygame

class launch_missiles:
    def __init__(self, screen, pygame, socket, board, is_client, is_server):
        self.screen = screen
        self.pygame = pygame
        self.socket = socket
        self.board = board
        self.missile_board = np.zeros((10, 10), dtype=int)
        self.is_client = is_client
        self.is_server = is_server
        self.our_turn = is_client
        self.cell_offset = 0
        self.first = True
        self.very_first = True
        self.server = None
        self.client = None
        self.last_shot = None
        self.opponent_ships_remaining = 24
        self.game_over = False
        self.victory = False

    def title(self):
        font = self.pygame.font.Font("coolvetica rg.ttf", 48)
        self.screen.fill((13, 17, 31))
        your_board = font.render("Bạn", True, (255, 255, 255))
        self.screen.blit(your_board, (200, 10))
        enemy_board = font.render("Đối thủ", True, (255, 255, 255))
        self.screen.blit(enemy_board, (820, 10))

    def createSocket(self, IP):
        if self.is_server:
            self.server = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM)
            self.server.bind(('', 8088))
            self.server.listen()
            self.conn, self.addr = self.server.accept()
        else:
            self.client = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM)
            time.sleep(3)
            self.client.connect((IP, 8088))

    def draw_your_board(self):
        x_loc = 20
        for idx, row in enumerate(self.board):
            for jdx, cell in enumerate(row):
                pos = (x_loc + 60 * jdx, 90 + self.cell_offset, 58, 58)
                if cell == 0:
                    self.pygame.draw.rect(self.screen, (214, 229, 255), pos, 1)
                    self.pygame.draw.circle(self.screen, (163, 163, 162), (x_loc + 60 * jdx + 30, 88 + self.cell_offset + 30), 6)
                elif cell == 1:
                    self.pygame.draw.rect(self.screen, (25, 209, 83), pos, 1)
                    self.pygame.draw.circle(self.screen, (25, 209, 83), (x_loc + 60 * jdx + 30, 88 + self.cell_offset + 30), 6)
                elif cell == 2:
                    self.pygame.draw.rect(self.screen, (242, 19, 19), pos, 1)
                    self.pygame.draw.circle(self.screen, (242, 19, 19), (x_loc + 60 * jdx + 30, 88 + self.cell_offset + 30), 6)
            self.cell_offset += 60
        self.cell_offset = 0

    def draw_missile_board(self):
        x_loc = 650
        for idx, row in enumerate(self.missile_board):
            for jdx, cell in enumerate(row):
                pos = (x_loc + 60 * jdx, 90 + self.cell_offset, 58, 58)
                if cell == 0:  # Chưa bắn
                    self.pygame.draw.rect(self.screen, (214, 229, 255), pos, 1)
                    self.pygame.draw.circle(self.screen, (163, 163, 162), (x_loc + 60 * jdx + 30, 88 + self.cell_offset + 30), 6)
                elif cell == 2:  # Bắn trượt
                    self.pygame.draw.rect(self.screen, (242, 19, 19), pos, 1)
                    self.pygame.draw.circle(self.screen, (242, 19, 19), (x_loc + 60 * jdx + 30, 88 + self.cell_offset + 30), 6)
                elif cell == 3:  # Bắn trúng
                    self.pygame.draw.rect(self.screen, (255, 255, 0), pos, 1)
                    self.pygame.draw.circle(self.screen, (255, 255, 0), (x_loc + 60 * jdx + 30, 88 + self.cell_offset + 30), 6)
            self.cell_offset += 60
        self.cell_offset = 0

    def turn(self):
        font = self.pygame.font.Font("coolvetica rg.ttf", 36)
        if self.our_turn:
            turn_text = font.render("Lượt của bạn!", True, (255, 255, 255))
            self.screen.blit(turn_text, (560, 20))
        else:
            turn_text = font.render("Lượt đối thủ!", True, (255, 255, 255))
            self.screen.blit(turn_text, (510, 20))

    def change_board(self, x, y):
        self.last_shot = (x, y)
        self.first = True
        self.our_turn = False
        message = bytes(f"{x}_{y}", 'utf-8')
        if self.client:
            self.client.send(message)
        else:
            self.conn.send(message)

    def check_game_over(self):
        # Chiến thắng: đối thủ hết tàu (đếm số tàu bị bắn trúng)
        if self.opponent_ships_remaining <= 0:
            self.display_victory()
            return True

        # Thua: board của bạn không còn ô nào chứa tàu (1)
        if np.all((self.board == 0) | (self.board == 2)):
            self.display_defeat()
            return True

        return False

    def display_victory(self):
        font = self.pygame.font.Font("coolvetica rg.ttf", 72)
        victory_text = font.render("You Win!", True, (255, 255, 0))
        self.screen.blit(victory_text, ((self.screen.get_width() - victory_text.get_width()) // 2,
                                        (self.screen.get_height() - victory_text.get_height()) // 2))
        self.pygame.display.update()
        time.sleep(3)
        self.game_over = True
        self.victory = True
        self.close_connections()

    def display_defeat(self):
        font = self.pygame.font.Font("coolvetica rg.ttf", 72)
        defeat_text = font.render("You Lose!", True, (255, 0, 0))
        self.screen.blit(defeat_text, ((self.screen.get_width() - defeat_text.get_width()) // 2,
                                       (self.screen.get_height() - defeat_text.get_height()) // 2))
        self.pygame.display.update()
        time.sleep(3)
        self.game_over = True
        self.victory = False
        self.close_connections()

    def close_connections(self):
        if hasattr(self, 'conn'):
            self.conn.close()
        if hasattr(self, 'server'):
            self.server.close()
        if hasattr(self, 'client'):
            self.client.close()

    def missed_hit(self, description):
        font = self.pygame.font.Font("coolvetica rg.ttf", 32)
        description_text = font.render(f"{description}!", True, (255, 255, 255))
        self.screen.blit(description_text, (30, 20))

        if description == "Target Hit":
            self.opponent_ships_remaining -= 1
            self.missile_board[self.last_shot[1]][self.last_shot[0]] = 3
        else:
            self.missile_board[self.last_shot[1]][self.last_shot[0]] = 2

        # Kiểm tra game over ngay sau khi xử lý đòn bắn
        self.check_game_over()

    def drawui(self, IP):
        # Tạo kết nối nếu chưa được thiết lập
        if self.very_first:
            self.createSocket(IP=IP)
            self.very_first = False

        if self.first:
            self.title()
            self.draw_your_board()
            self.draw_missile_board()
            self.turn()
            self.pygame.display.update()
            self.first = False

            # Nếu không phải lượt của mình và game chưa kết thúc, chờ nhận dữ liệu từ đối thủ
            if not self.our_turn and not self.game_over:
                try:
                    if self.server:
                        data = self.conn.recv(1024).decode()
                    else:  # Client
                        data = self.client.recv(1024).decode()

                    # Nếu nhận được phản hồi về đòn bắn của mình (Target Hit/Missed)
                    if data in ["Target Hit", "Missed"]:
                        x, y = self.last_shot
                        self.missed_hit(data)
                        self.first = True
                    else:
                        # Nhận dữ liệu tọa độ từ đối thủ
                        x, y = map(int, data.split("_"))
                        if self.board[y][x] == 1:
                            response = "Target Hit"
                            self.board[y][x] = 2
                        else:
                            response = "Missed"
                            self.board[y][x] = 2

                        # Gửi phản hồi cho đối thủ
                        if self.server:
                            self.conn.send(bytes(response, 'utf-8'))
                        else:
                            self.client.send(bytes(response, 'utf-8'))

                        # Sau khi cập nhật board, kiểm tra game over (thua nếu hết tàu)
                        self.check_game_over()
                        self.our_turn = True
                        self.first = True
                except Exception as e:
                    print(f"Connection error: {e}")
                    self.game_over = True

    def run(self, IP):
        if not self.game_over:
            self.drawui(IP)
        return self.game_over, self.victory
