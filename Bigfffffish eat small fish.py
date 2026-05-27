import pygame
import sys
import random
import math

# 初始化Pygame
pygame.init()
pygame.mixer.init()

# 游戏窗口设置
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("大鱼吃小鱼")

# 游戏时钟
clock = pygame.time.Clock()
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
OCEAN_BLUE = (0, 100, 200)
DARK_BLUE = (0, 50, 100)

# 游戏状态枚举
class GameState:
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    WIN = 4

# 游戏模式
class GameMode:
    SINGLE = 0
    DOUBLE = 1

class PlayerFish:
    """玩家鱼类"""
    def __init__(self, x, y, controls, color, name):
        self.x = x
        self.y = y
        self.size = 30
        self.speed = 5
        self.lives = 3
        self.score = 0
        self.controls = controls
        self.color = color
        self.name = name
        self.direction = 1  # 1向右，-1向左
        self.alive = True
        
    def update(self):
        if not self.alive:
            return
            
        keys = pygame.key.get_pressed()
        
        # WASD控制
        if self.controls == "WASD":
            if keys[pygame.K_w]:
                self.y -= self.speed
            if keys[pygame.K_s]:
                self.y += self.speed
            if keys[pygame.K_a]:
                self.x -= self.speed
                self.direction = -1
            if keys[pygame.K_d]:
                self.x += self.speed
                self.direction = 1
                
        # 方向键控制
        elif self.controls == "ARROWS":
            if keys[pygame.K_UP]:
                self.y -= self.speed
            if keys[pygame.K_DOWN]:
                self.y += self.speed
            if keys[pygame.K_LEFT]:
                self.x -= self.speed
                self.direction = -1
            if keys[pygame.K_RIGHT]:
                self.x += self.speed
                self.direction = 1
        
        # 边界检查
        self.x = max(self.size, min(WIDTH - self.size, self.x))
        self.y = max(self.size, min(HEIGHT - self.size, self.y))
    
    def draw(self, surface):
        if not self.alive:
            return
            
        # 绘制鱼身体（椭圆）
        body_rect = pygame.Rect(
            self.x - self.size, 
            self.y - self.size // 2,
            self.size * 2, 
            self.size
        )
        pygame.draw.ellipse(surface, self.color, body_rect)
        pygame.draw.ellipse(surface, BLACK, body_rect, 2)
        
        # 绘制鱼尾巴（三角形）
        tail_points = [
            (self.x - self.size * self.direction, self.y),
            (self.x - self.size * 1.5 * self.direction, self.y - self.size // 3),
            (self.x - self.size * 1.5 * self.direction, self.y + self.size // 3)
        ]
        pygame.draw.polygon(surface, self.color, tail_points)
        pygame.draw.polygon(surface, BLACK, tail_points, 2)
        
        # 绘制鱼鳍
        fin_points = [
            (self.x, self.y - self.size // 2),
            (self.x - self.size // 2 * self.direction, self.y - self.size),
            (self.x + self.size // 3 * self.direction, self.y - self.size // 2)
        ]
        pygame.draw.polygon(surface, self.color, fin_points)
        pygame.draw.polygon(surface, BLACK, fin_points, 2)
        
        # 绘制鱼眼睛
        eye_x = self.x + self.size // 3 * self.direction
        eye_y = self.y - self.size // 6
        pygame.draw.circle(surface, WHITE, (eye_x, eye_y), self.size // 5)
        pygame.draw.circle(surface, BLACK, (eye_x, eye_y), self.size // 8)
        
        # 绘制鱼嘴
        mouth_start = (self.x + self.size * self.direction, self.y)
        mouth_end = (self.x + self.size * 0.8 * self.direction, self.y + self.size // 6)
        pygame.draw.line(surface, BLACK, mouth_start, mouth_end, 2)
    
    def grow(self, amount):
        """鱼长大"""
        self.size += amount
        self.speed = max(2, 5 - (self.size - 30) // 20)  # 速度随大小略微降低
    
    def lose_life(self):
        """失去一条命"""
        self.lives -= 1
        if self.lives <= 0:
            self.alive = False
            return True
        return False

class EnemyFish:
    """敌方鱼类"""
    def __init__(self, difficulty_multiplier=1.0):
        # 随机选择生成位置（屏幕边缘）
        side = random.choice(["left", "right", "top", "bottom"])
        
        if side == "left":
            self.x = -50
            self.y = random.randint(0, HEIGHT)
            self.direction = 1
        elif side == "right":
            self.x = WIDTH + 50
            self.y = random.randint(0, HEIGHT)
            self.direction = -1
        elif side == "top":
            self.x = random.randint(0, WIDTH)
            self.y = -50
            self.direction = random.choice([1, -1])
        else:  # bottom
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT + 50
            self.direction = random.choice([1, -1])
        
        # 随机大小和速度
        self.size = random.randint(20, 80)
        self.base_speed = random.uniform(1, 3)
        self.speed = self.base_speed * difficulty_multiplier
        
        # 随机颜色（偏向海洋色调）
        self.color = (
            random.randint(50, 200),
            random.randint(100, 255),
            random.randint(150, 255)
        )
        
        # 移动模式
        self.move_pattern = random.choice(["straight", "sine", "zigzag"])
        self.time = random.randint(0, 100)
        
        # 垂直速度（用于上下移动）
        self.vertical_speed = random.uniform(-1, 1)
    
    def update(self):
        self.time += 1
        
        # 基础移动
        self.x += self.speed * self.direction
        
        # 特殊移动模式
        if self.move_pattern == "sine":
            self.y += math.sin(self.time * 0.05) * 2
        elif self.move_pattern == "zigzag":
            if self.time % 60 < 30:
                self.y += self.speed
            else:
                self.y -= self.speed
        else:  # straight
            self.y += self.vertical_speed
        
        # 垂直边界检查（反弹）
        if self.y < self.size or self.y > HEIGHT - self.size:
            self.vertical_speed *= -1
        
        # 检查是否离开屏幕
        if (self.x < -100 or self.x > WIDTH + 100):
            return False  # 需要移除
        
        return True  # 保留
    
    def draw(self, surface):
        # 绘制敌方鱼（与玩家鱼类似但更简单）
        # 鱼身体
        body_rect = pygame.Rect(
            self.x - self.size, 
            self.y - self.size // 2,
            self.size * 2, 
            self.size
        )
        pygame.draw.ellipse(surface, self.color, body_rect)
        pygame.draw.ellipse(surface, BLACK, body_rect, 1)
        
        # 鱼尾巴
        tail_points = [
            (self.x - self.size * self.direction, self.y),
            (self.x - self.size * 1.3 * self.direction, self.y - self.size // 4),
            (self.x - self.size * 1.3 * self.direction, self.y + self.size // 4)
        ]
        pygame.draw.polygon(surface, self.color, tail_points)
        
        # 鱼眼睛
        eye_x = self.x + self.size // 3 * self.direction
        eye_y = self.y - self.size // 6
        pygame.draw.circle(surface, WHITE, (eye_x, eye_y), self.size // 6)
        pygame.draw.circle(surface, BLACK, (eye_x, eye_y), self.size // 10)

class DifficultyManager:
    """难度管理器"""
    def __init__(self):
        self.level = 1
        self.time_elapsed = 0
        self.spawn_rate = 60  # 每60帧生成一个敌方鱼
        self.enemy_speed_multiplier = 1.0
        self.max_enemies = 10
        self.enemy_size_range = (15, 40)  # 初始敌方鱼较小
        
    def update(self):
        self.time_elapsed += 1
        
        # 每30秒增加难度
        if self.time_elapsed % (FPS * 30) == 0:
            self.level += 1
            self.increase_difficulty()
    
    def increase_difficulty(self):
        """增加游戏难度"""
        # 增加生成速率
        self.spawn_rate = max(20, self.spawn_rate - 5)
        
        # 增加敌方鱼速度
        self.enemy_speed_multiplier += 0.1
        
        # 增加最大敌方鱼数量
        self.max_enemies = min(30, self.max_enemies + 2)
        
        # 增加敌方鱼大小范围（最小值略微增加，最大值明显增加）
        min_size, max_size = self.enemy_size_range
        new_min = min(30, min_size + 2)
        new_max = min(120, max_size + 15)
        self.enemy_size_range = (new_min, new_max)
        
        print(f"难度提升！当前等级: {self.level}")
    
    def should_spawn(self, frame_count):
        """是否应该生成新的敌方鱼"""
        return frame_count % self.spawn_rate == 0
    
    def get_difficulty_info(self):
        """获取难度信息"""
        return {
            "level": self.level,
            "spawn_rate": self.spawn_rate,
            "speed_multiplier": self.enemy_speed_multiplier,
            "max_enemies": self.max_enemies,
            "size_range": self.enemy_size_range
        }

class SoundManager:
    """音效管理器"""
    def __init__(self):
        self.sounds = {}
        self.music_playing = False
        self.sound_enabled = True
        
        # 尝试加载音效
        self.load_sounds()
    
    def load_sounds(self):
        """加载或生成音效"""
        try:
            # 创建简单音效
            self.create_simple_sounds()
        except Exception as e:
            print(f"音效加载失败: {e}")
            self.sound_enabled = False
    
    def create_simple_sounds(self):
        """创建简单的音效（使用array模块，无需numpy）"""
        import array
        import math
        
        sample_rate = 22050
        
        def make_tone(freq, duration, volume=0.3):
            n_samples = int(sample_rate * duration)
            buf = array.array('h', [0] * n_samples)
            for i in range(n_samples):
                t = i / sample_rate
                val = int(volume * 32767 * math.sin(2 * math.pi * freq * t))
                # 简单的淡出效果
                fade = max(0, 1 - (i / n_samples) * 0.5)
                buf[i] = int(val * fade)
            return pygame.mixer.Sound(buffer=buf)
        
        # 吃鱼音效（上升音调）
        self.sounds["eat"] = make_tone(523, 0.1)
        
        # 受伤音效（下降音调）
        self.sounds["hurt"] = make_tone(200, 0.2)
        
        # 游戏结束音效
        self.sounds["game_over"] = make_tone(150, 0.5)
    
    def play(self, sound_name):
        """播放音效"""
        if not self.sound_enabled:
            return
            
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()
    
    def toggle_sound(self):
        """切换音效开关"""
        self.sound_enabled = not self.sound_enabled
        return self.sound_enabled

class UIManager:
    """用户界面管理器"""
    def __init__(self):
        # 尝试加载中文字体
        import os
        font_path = None
        possible_paths = [
            "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",     # 黑体
            "C:/Windows/Fonts/simsun.ttc",     # 宋体
        ]
        for path in possible_paths:
            if os.path.exists(path):
                font_path = path
                break
        
        if font_path:
            self.font_large = pygame.font.Font(font_path, 72)
            self.font_medium = pygame.font.Font(font_path, 48)
            self.font_small = pygame.font.Font(font_path, 36)
            self.font_tiny = pygame.font.Font(font_path, 24)
        else:
            # 回退到默认字体
            self.font_large = pygame.font.Font(None, 72)
            self.font_medium = pygame.font.Font(None, 48)
            self.font_small = pygame.font.Font(None, 36)
            self.font_tiny = pygame.font.Font(None, 24)
        
        # 按钮颜色
        self.button_color = (50, 150, 50)
        self.button_hover_color = (70, 180, 70)
        self.button_text_color = WHITE
        
        # 按钮状态
        self.buttons = {}
    
    def create_button(self, name, text, x, y, width, height, action=None):
        """创建按钮"""
        self.buttons[name] = {
            "rect": pygame.Rect(x, y, width, height),
            "text": text,
            "action": action,
            "hovered": False
        }
    
    def draw_button(self, surface, name):
        """绘制按钮，返回是否被点击"""
        if name not in self.buttons:
            return False
            
        button = self.buttons[name]
        rect = button["rect"]
        text = button["text"]
        
        mouse = pygame.mouse.get_pos()
        
        # 检查鼠标是否在按钮上
        hovered = rect.collidepoint(mouse)
        button["hovered"] = hovered
        
        # 绘制按钮背景
        color = self.button_hover_color if hovered else self.button_color
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, WHITE, rect, 2)
        
        # 绘制按钮文字
        text_surface = self.font_small.render(text, True, self.button_text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)
        
        return hovered
    
    def is_button_clicked(self, name):
        """检查按钮是否被点击"""
        if name not in self.buttons:
            return False
        return self.buttons[name].get("hovered", False)
    
    def draw_menu(self, surface, sound_enabled=True):
        """绘制开始菜单"""
        # 绘制背景
        surface.fill(OCEAN_BLUE)
        
        # 绘制装饰性气泡
        for i in range(20):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            radius = random.randint(5, 20)
            alpha = random.randint(50, 150)
            bubble_color = (200, 220, 255, alpha)
            pygame.draw.circle(surface, bubble_color, (x, y), radius)
        
        # 标题
        title = self.font_large.render("大鱼吃小鱼", True, YELLOW)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 5))
        surface.blit(title, title_rect)
        
        # 操作说明
        controls = [
            "单人模式: WASD控制",
            "双人模式: 玩家1 WASD / 玩家2 方向键",
            "吃掉比自己小的鱼，躲避比自己大的鱼",
            "达到3000分即可获胜！"
        ]
        
        for i, text in enumerate(controls):
            color = CYAN if i < 2 else WHITE
            control_text = self.font_small.render(text, True, color)
            control_rect = control_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + i * 35))
            surface.blit(control_text, control_rect)
        
        # 单人模式按钮
        self.create_button("single", "单人模式", WIDTH // 2 - 220, HEIGHT * 2 // 3, 200, 50)
        self.draw_button(surface, "single")
        
        # 双人模式按钮
        self.create_button("double", "双人模式", WIDTH // 2 + 20, HEIGHT * 2 // 3, 200, 50)
        self.draw_button(surface, "double")
        
        # 音效按钮
        sound_text = "音效: 开启" if sound_enabled else "音效: 关闭"
        self.create_button("sound", sound_text, WIDTH // 2 - 100, HEIGHT * 2 // 3 + 70, 200, 50)
        self.draw_button(surface, "sound")
    
    def draw_game_ui(self, surface, player1, player2, difficulty_info, game_mode=GameMode.DOUBLE):
        """绘制游戏UI"""
        # 绘制分数和状态
        if player1.alive:
            score1_text = self.font_small.render(f"{player1.name}: {player1.score}", True, player1.color)
        else:
            score1_text = self.font_small.render(f"{player1.name}: 已死亡", True, (128, 128, 128))
        surface.blit(score1_text, (10, 10))
        
        # 双人模式显示玩家2信息
        if game_mode == GameMode.DOUBLE:
            if player2.alive:
                score2_text = self.font_small.render(f"{player2.name}: {player2.score}", True, player2.color)
            else:
                score2_text = self.font_small.render(f"{player2.name}: 已死亡", True, (128, 128, 128))
            surface.blit(score2_text, (WIDTH - 200, 10))
        
        # 绘制目标分数
        target_text = self.font_small.render(f"目标: 3000分", True, YELLOW)
        surface.blit(target_text, (WIDTH // 2 - 60, 10))
        
        # 绘制生命值
        self.draw_lives(surface, player1, 10, 50)
        if game_mode == GameMode.DOUBLE:
            self.draw_lives(surface, player2, WIDTH - 100, 50)
        
        # 绘制难度等级
        level_text = self.font_tiny.render(f"难度: {difficulty_info['level']}", True, WHITE)
        surface.blit(level_text, (WIDTH // 2 - 30, HEIGHT - 30))
        
        # 绘制玩家大小
        size1_text = self.font_tiny.render(f"大小: {player1.size}", True, player1.color)
        surface.blit(size1_text, (10, 90))
        
        if game_mode == GameMode.DOUBLE:
            size2_text = self.font_tiny.render(f"大小: {player2.size}", True, player2.color)
            surface.blit(size2_text, (WIDTH - 100, 90))
    
    def draw_lives(self, surface, player, x, y):
        """绘制生命值"""
        if not player.alive:
            # 玩家已死亡，显示灰色X
            for i in range(3):
                heart_x = x + i * 25
                heart_y = y
                pygame.draw.line(surface, (128, 128, 128), (heart_x - 5, heart_y - 5), (heart_x + 5, heart_y + 5), 2)
                pygame.draw.line(surface, (128, 128, 128), (heart_x + 5, heart_y - 5), (heart_x - 5, heart_y + 5), 2)
            return
        
        for i in range(player.lives):
            # 绘制小鱼图标
            heart_x = x + i * 25
            heart_y = y
            
            # 简单的心形
            pygame.draw.circle(surface, player.color, (heart_x, heart_y), 8)
            pygame.draw.circle(surface, player.color, (heart_x + 8, heart_y), 8)
            pygame.draw.polygon(surface, player.color, [
                (heart_x - 8, heart_y),
                (heart_x + 16, heart_y),
                (heart_x + 4, heart_y + 12)
            ])
    
    def draw_pause_screen(self, surface):
        """绘制暂停画面"""
        # 半透明背景
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        # 暂停文字
        pause_text = self.font_large.render("游戏暂停", True, WHITE)
        pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        surface.blit(pause_text, pause_rect)
        
        # 提示文字
        resume_text = self.font_small.render("按ESC继续游戏", True, CYAN)
        resume_rect = resume_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        surface.blit(resume_text, resume_rect)
        
        # 返回菜单按钮
        self.create_button("menu", "返回菜单", WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50)
        self.draw_button(surface, "menu")
    
    def draw_game_over(self, surface, player1, player2):
        """绘制游戏结束画面"""
        # 半透明背景
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        # 游戏结束文字
        game_over_text = self.font_large.render("游戏结束", True, RED)
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        surface.blit(game_over_text, game_over_rect)
        
        # 最终分数
        total_score = player1.score + player2.score
        score_text = self.font_medium.render(f"最终得分: {total_score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        surface.blit(score_text, score_rect)
        
        # 各玩家分数
        p1_score = self.font_small.render(f"{player1.name}: {player1.score}", True, player1.color)
        surface.blit(p1_score, (WIDTH // 2 - 150, HEIGHT // 2 + 20))
        
        p2_score = self.font_small.render(f"{player2.name}: {player2.score}", True, player2.color)
        surface.blit(p2_score, (WIDTH // 2 + 50, HEIGHT // 2 + 20))
        
        # 重新开始按钮
        self.create_button("restart", "重新开始", WIDTH // 2 - 100, HEIGHT * 3 // 4, 200, 50)
        self.draw_button(surface, "restart")
        
        # 返回菜单按钮
        self.create_button("back_menu", "返回菜单", WIDTH // 2 - 100, HEIGHT * 3 // 4 + 70, 200, 50)
        self.draw_button(surface, "back_menu")
    
    def draw_win(self, surface, player1, player2, game_mode):
        """绘制胜利画面"""
        # 半透明背景（金色调）
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((50, 50, 0))
        surface.blit(overlay, (0, 0))
        
        # 胜利文字
        win_text = self.font_large.render("游戏胜利！", True, YELLOW)
        win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        surface.blit(win_text, win_rect)
        
        # 确定获胜者
        if player1.score >= 3000:
            winner_text = self.font_medium.render(f"{player1.name} 获胜！", True, player1.color)
        else:
            winner_text = self.font_medium.render(f"{player2.name} 获胜！", True, player2.color)
        winner_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 20))
        surface.blit(winner_text, winner_rect)
        
        # 最终分数
        total_score = player1.score + player2.score
        score_text = self.font_medium.render(f"总分: {total_score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        surface.blit(score_text, score_rect)
        
        # 各玩家分数
        p1_score = self.font_small.render(f"{player1.name}: {player1.score}", True, player1.color)
        surface.blit(p1_score, (WIDTH // 2 - 150, HEIGHT // 2 + 40))
        
        if game_mode == GameMode.DOUBLE:
            p2_score = self.font_small.render(f"{player2.name}: {player2.score}", True, player2.color)
            surface.blit(p2_score, (WIDTH // 2 + 50, HEIGHT // 2 + 40))
        
        # 重新开始按钮
        self.create_button("restart", "再来一局", WIDTH // 2 - 100, HEIGHT * 3 // 4, 200, 50)
        self.draw_button(surface, "restart")
        
        # 返回菜单按钮
        self.create_button("back_menu", "返回菜单", WIDTH // 2 - 100, HEIGHT * 3 // 4 + 70, 200, 50)
        self.draw_button(surface, "back_menu")

class Game:
    """主游戏类"""
    def __init__(self):
        self.state = GameState.MENU
        self.frame_count = 0
        self.game_mode = GameMode.DOUBLE  # 默认双人模式
        
        # 创建游戏对象
        self.player1 = PlayerFish(WIDTH // 4, HEIGHT // 2, "WASD", GREEN, "玩家1")
        self.player2 = PlayerFish(3 * WIDTH // 4, HEIGHT // 2, "ARROWS", RED, "玩家2")
        
        self.enemies = []
        self.difficulty = DifficultyManager()
        self.sound_manager = SoundManager()
        self.ui_manager = UIManager()
        
        # 游戏统计
        self.game_time = 0
        self.total_fish_eaten = 0
        
        # 胜利分数
        self.win_score = 3000
        
        # 创建背景元素
        self.bubbles = []
        for _ in range(50):
            self.bubbles.append({
                "x": random.randint(0, WIDTH),
                "y": random.randint(0, HEIGHT),
                "speed": random.uniform(0.5, 2),
                "size": random.randint(2, 8)
            })
    
    def reset_game(self):
        """重置游戏"""
        self.player1 = PlayerFish(WIDTH // 4, HEIGHT // 2, "WASD", GREEN, "玩家1")
        if self.game_mode == GameMode.DOUBLE:
            self.player2 = PlayerFish(3 * WIDTH // 4, HEIGHT // 2, "ARROWS", RED, "玩家2")
        else:
            self.player2 = PlayerFish(-100, -100, "ARROWS", RED, "玩家2")  # 单人模式隐藏玩家2
            self.player2.alive = False
        self.enemies.clear()
        self.difficulty = DifficultyManager()
        self.frame_count = 0
        self.game_time = 0
        self.total_fish_eaten = 0
    
    def start_game(self, mode):
        """开始游戏"""
        self.game_mode = mode
        self.reset_game()
        self.state = GameState.PLAYING
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                
                if event.key == pygame.K_RETURN:
                    if self.state == GameState.MENU:
                        self.start_game(GameMode.DOUBLE)
                    elif self.state == GameState.GAME_OVER or self.state == GameState.WIN:
                        self.reset_game()
                        self.state = GameState.PLAYING
            
            # 鼠标点击事件
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == GameState.MENU:
                    # 检查单人模式按钮
                    if self.ui_manager.is_button_clicked("single"):
                        self.start_game(GameMode.SINGLE)
                    # 检查双人模式按钮
                    elif self.ui_manager.is_button_clicked("double"):
                        self.start_game(GameMode.DOUBLE)
                    # 检查音效按钮
                    elif self.ui_manager.is_button_clicked("sound"):
                        self.sound_manager.toggle_sound()
                
                elif self.state == GameState.PAUSED:
                    # 检查返回菜单按钮
                    if self.ui_manager.is_button_clicked("menu"):
                        self.reset_game()
                        self.state = GameState.MENU
                
                elif self.state == GameState.GAME_OVER or self.state == GameState.WIN:
                    # 检查重新开始按钮
                    if self.ui_manager.is_button_clicked("restart"):
                        self.reset_game()
                        self.state = GameState.PLAYING
                    # 检查返回菜单按钮
                    elif self.ui_manager.is_button_clicked("back_menu"):
                        self.reset_game()
                        self.state = GameState.MENU
    
    def update(self):
        """更新游戏逻辑"""
        if self.state == GameState.PLAYING:
            self.frame_count += 1
            self.game_time += 1 / FPS
            
            # 更新玩家
            self.player1.update()
            self.player2.update()
            
            # 生成敌方鱼
            if (self.difficulty.should_spawn(self.frame_count) and 
                len(self.enemies) < self.difficulty.max_enemies):
                new_enemy = EnemyFish(self.difficulty.enemy_speed_multiplier)
                # 根据难度调整敌方鱼大小
                min_size, max_size = self.difficulty.enemy_size_range
                new_enemy.size = random.randint(min_size, max_size)
                self.enemies.append(new_enemy)
            
            # 更新敌方鱼
            self.enemies = [enemy for enemy in self.enemies if enemy.update()]
            
            # 碰撞检测
            self.check_collisions()
            
            # 更新难度
            self.difficulty.update()
            
            # 检查胜利条件（任一玩家达到胜利分数）
            if self.player1.score >= self.win_score or self.player2.score >= self.win_score:
                self.state = GameState.WIN
                self.sound_manager.play("game_over")  # 复用音效
            
            # 检查游戏结束条件（两个玩家都死亡才结束）
            elif not self.player1.alive and not self.player2.alive:
                self.state = GameState.GAME_OVER
                self.sound_manager.play("game_over")
        
        # 更新背景气泡
        self.update_bubbles()
    
    def update_bubbles(self):
        """更新背景气泡"""
        for bubble in self.bubbles:
            bubble["y"] -= bubble["speed"]
            if bubble["y"] < -10:
                bubble["y"] = HEIGHT + 10
                bubble["x"] = random.randint(0, WIDTH)
    
    def check_collisions(self):
        """检查碰撞"""
        for enemy in self.enemies[:]:
            # 玩家1与敌方鱼碰撞
            if self.check_collision(self.player1, enemy):
                self.handle_collision(self.player1, enemy)
            
            # 玩家2与敌方鱼碰撞
            if self.check_collision(self.player2, enemy):
                self.handle_collision(self.player2, enemy)
    
    def check_collision(self, fish1, fish2):
        """检查两条鱼是否碰撞"""
        if not fish1.alive:
            return False
            
        distance = math.sqrt(
            (fish1.x - fish2.x) ** 2 + 
            (fish1.y - fish2.y) ** 2
        )
        
        # 碰撞距离 = 两鱼半径之和
        collision_distance = fish1.size + fish2.size
        
        return distance < collision_distance
    
    def handle_collision(self, player, enemy):
        """处理碰撞"""
        if player.size > enemy.size:
            # 玩家吃掉敌方鱼
            growth = enemy.size // 10
            player.grow(growth)
            player.score += enemy.size
            self.total_fish_eaten += 1
            
            if enemy in self.enemies:
                self.enemies.remove(enemy)
            
            self.sound_manager.play("eat")
        else:
            # 玩家被吃
            if player.lose_life():
                # 玩家死亡
                pass
            
            if enemy in self.enemies:
                self.enemies.remove(enemy)
            
            self.sound_manager.play("hurt")
    
    def draw(self):
        """绘制游戏画面"""
        # 绘制背景
        screen.fill(OCEAN_BLUE)
        
        # 绘制背景气泡
        for bubble in self.bubbles:
            pygame.draw.circle(screen, (200, 220, 255, 100), 
                             (int(bubble["x"]), int(bubble["y"])), bubble["size"])
        
        # 根据游戏状态绘制不同内容
        if self.state == GameState.MENU:
            self.ui_manager.draw_menu(screen, self.sound_manager.sound_enabled)
        
        elif self.state == GameState.PLAYING:
            # 绘制敌方鱼
            for enemy in self.enemies:
                enemy.draw(screen)
            
            # 绘制玩家鱼
            self.player1.draw(screen)
            self.player2.draw(screen)
            
            # 绘制UI
            self.ui_manager.draw_game_ui(screen, self.player1, self.player2, 
                                        self.difficulty.get_difficulty_info(), self.game_mode)
        
        elif self.state == GameState.PAUSED:
            # 绘制游戏画面（暂停状态下仍然显示）
            for enemy in self.enemies:
                enemy.draw(screen)
            self.player1.draw(screen)
            self.player2.draw(screen)
            self.ui_manager.draw_game_ui(screen, self.player1, self.player2, 
                                        self.difficulty.get_difficulty_info(), self.game_mode)
            
            # 绘制暂停界面
            self.ui_manager.draw_pause_screen(screen)
        
        elif self.state == GameState.GAME_OVER:
            # 绘制游戏画面
            for enemy in self.enemies:
                enemy.draw(screen)
            self.player1.draw(screen)
            self.player2.draw(screen)
            
            # 绘制游戏结束界面
            self.ui_manager.draw_game_over(screen, self.player1, self.player2)
        
        elif self.state == GameState.WIN:
            # 绘制游戏画面
            for enemy in self.enemies:
                enemy.draw(screen)
            self.player1.draw(screen)
            self.player2.draw(screen)
            
            # 绘制胜利界面
            self.ui_manager.draw_win(screen, self.player1, self.player2, self.game_mode)
        
        # 更新显示
        pygame.display.flip()
    
    def run(self):
        """运行游戏主循环"""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)

def main():
    """主函数"""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()