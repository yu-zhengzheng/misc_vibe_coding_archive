import pygame
import math
import sys

# 初始化
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("简易坎巴拉太空计划")
clock = pygame.time.Clock()
FPS = 60

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (100, 149, 237)
RED = (255, 99, 71)
GRAY = (80, 80, 80)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# 主天体属性 (例如：Kerbin)
PLANET_MASS = 1.2915e23  # kg
PLANET_RADIUS = 100  # 缩小行星半径，使其在屏幕内可见
GRAVITATIONAL_CONSTANT = 6.67430e-17  # m^3 kg^-1 s^-2


class Rocket(pygame.sprite.Sprite):
    def __init__(self, mass=1, fuel=5, thrust=100):
        super().__init__()
        # 创建一个简单的火箭图像（一个三角形）
        self.original_image = pygame.Surface((30, 50), pygame.SRCALPHA)
        pygame.draw.polygon(self.original_image, WHITE, [(15, 0), (30, 50), (0, 50)])
        # 添加火箭细节
        pygame.draw.rect(self.original_image, RED, (10, 40, 10, 10))
        self.image = self.original_image
        self.rect = self.image.get_rect()

        # 初始位置：行星上方
        planet_center = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
        self.rect.centerx = WIDTH // 2 - 2
        self.rect.centery = HEIGHT // 2 - PLANET_RADIUS - 200

        # 物理属性
        self.mass = mass  # 干重 (kg)
        self.fuel = fuel  # 燃料 (kg)
        self.thrust = thrust  # 推力 (N)
        self.fuel_consumption = 0.01  # 燃料消耗率 (kg/s)

        # 状态向量
        self.pos = pygame.Vector2(self.rect.center)
        self.vel = pygame.Vector2(55, 0)
        self.acc = pygame.Vector2(0, 0)

        # 火箭朝向 (0度指向屏幕右侧，-90度指向屏幕上方)
        self.angle = 15
        self.angular_velocity = 0
        self.throttle = 0.0  # 油门 0.0 到 1.0
        self.engine_on = False

    def update(self, dt, planet_center):
        # 处理键盘输入，控制火箭
        keys = pygame.key.get_pressed()
        self.engine_on = False

        # 油门控制 (Shift/Ctrl 或 上下箭头)
        if keys[pygame.K_UP]:
            self.throttle = min(1.0, self.throttle + 0.5 * dt)
        elif keys[pygame.K_DOWN]:
            self.throttle = max(0, self.throttle - 0.5 * dt)

        # 姿态控制 (左右箭头)
        if keys[pygame.K_LEFT]:
            self.angular_velocity = -30  # 度/秒
        elif keys[pygame.K_RIGHT]:
            self.angular_velocity = 30
        else:
            self.angular_velocity = 0

        # 应用姿态控制
        self.angle += self.angular_velocity * dt
        # 限制角度在0-360度
        self.angle %= 360

        # 计算推力矢量
        thrust_angle_rad = math.radians(self.angle)
        thrust_vector = pygame.Vector2(math.cos(thrust_angle_rad), math.sin(thrust_angle_rad))

        # 计算引力矢量 (指向行星中心)
        to_planet = planet_center - self.pos
        distance_to_planet_center = to_planet.length()
        to_planet_normalized = to_planet.normalize() if to_planet else pygame.Vector2(0, 0)

        # 万有引力计算 F = G * M * m / r^2
        if distance_to_planet_center > 0:
            gravitational_force_magnitude = GRAVITATIONAL_CONSTANT * PLANET_MASS * self.mass / (
                        distance_to_planet_center ** 2)
            gravitational_force = to_planet_normalized * gravitational_force_magnitude
        else:
            gravitational_force = pygame.Vector2(0, 0)

        # 推力计算
        thrust_force = pygame.Vector2(0, 0)
        if self.throttle > -10 and self.fuel > 0:
            self.engine_on = True
            fuel_used = self.fuel_consumption * self.throttle * dt
            # 确保燃料不为负
            fuel_used = min(fuel_used, self.fuel)
            self.fuel -= fuel_used

            # 推力矢量 F = thrust * throttle
            thrust_force = thrust_vector * (self.thrust * self.throttle)

        # 总加速度 a = F_total / m
        total_force = thrust_force + gravitational_force
        self.acc = total_force / (self.mass + self.fuel)  # 总质量 = 干重 + 剩余燃料

        # 更新速度和位置 (使用简单的欧拉积分)
        self.vel += self.acc * dt
        self.pos += self.vel * dt
        # print(self.vel)
        # 更新火箭图像位置和旋转
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        # 旋转火箭图像，注意角度调整
        old_center = self.rect.center
        self.image = pygame.transform.rotate(self.original_image, -self.angle - 90)  # 调整使-90度时指向上
        self.rect = self.image.get_rect(center=old_center)

        # 检查是否与行星相撞
        if distance_to_planet_center < PLANET_RADIUS:
            # 碰撞处理：可以结束游戏或重置
            print("Crash!")
            return "CRASH"
        return "FLYING"

    def draw(self, surface):
        surface.blit(self.image, self.rect)

        # 如果引擎启动，绘制火焰效果
        if self.engine_on:
            flame_length = 20 + 10 * self.throttle
            flame_angle_rad = math.radians(self.angle)
            # 火焰起点在火箭底部中心
            rocket_bottom_center = pygame.Vector2(self.rect.centerx, self.rect.centery) + pygame.Vector2(0, 25).rotate(
                -self.angle)
            # 火焰方向与火箭朝向相反
            flame_direction = pygame.Vector2(-math.cos(flame_angle_rad), -math.sin(flame_angle_rad))
            flame_end = rocket_bottom_center + flame_direction * flame_length

            # 绘制多层火焰，使其看起来更真实
            pygame.draw.line(surface, YELLOW, rocket_bottom_center, flame_end, 5)
            pygame.draw.line(surface, ORANGE, rocket_bottom_center,
                             rocket_bottom_center + flame_direction * (flame_length * 0.7), 3)
            pygame.draw.line(surface, RED, rocket_bottom_center,
                             rocket_bottom_center + flame_direction * (flame_length * 0.4), 2)


def draw_stars(surface, width, height, num_stars=100):
    return
    """在背景上绘制星星"""
    for _ in range(num_stars):
        x = pygame.time.get_ticks() // 50 % width  # 简单的动画效果
        y = pygame.time.get_ticks() // 70 % height
        size = (pygame.time.get_ticks() // 100) % 3 + 1
        brightness = 150 + (pygame.time.get_ticks() // 20) % 105
        pygame.draw.circle(surface, (brightness, brightness, brightness), (x, y), size)


def main():
    running = True
    rocket = Rocket()
    planet_center = pygame.Vector2(WIDTH // 2, HEIGHT // 2)  # 行星在屏幕中心

    # 游戏状态
    game_state = "FLYING"

    # 创建字体对象
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)

    while running:
        dt = clock.tick(FPS) / 1000.0  # 转换为秒

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_state == "CRASHED":
                    # 重置游戏
                    rocket = Rocket()
                    game_state = "FLYING"

        # 更新游戏状态
        if game_state == "FLYING":
            result = rocket.update(dt, planet_center)
            if result == "CRASH":
                game_state = "CRASHED"

        # 绘制
        screen.fill(BLACK)

        # 绘制星空背景
        draw_stars(screen, WIDTH, HEIGHT)

        # 绘制行星 (一个圆形，带有一点细节)
        pygame.draw.circle(screen, BLUE, (int(planet_center.x), int(planet_center.y)), PLANET_RADIUS)
        # 添加行星细节
        pygame.draw.circle(screen, (70, 70, 200),
                           (int(planet_center.x - PLANET_RADIUS // 3), int(planet_center.y - PLANET_RADIUS // 3)),
                           PLANET_RADIUS // 4)
        pygame.draw.circle(screen, (70, 70, 200),
                           (int(planet_center.x + PLANET_RADIUS // 2), int(planet_center.y + PLANET_RADIUS // 3)),
                           PLANET_RADIUS // 5)

        # 绘制火箭
        rocket.draw(screen)

        # 显示游戏状态和信息
        altitude = (pygame.Vector2(rocket.rect.center) - planet_center).length() - PLANET_RADIUS
        altitude_text = font.render(f"h: {altitude:.0f} m", True, WHITE)
        velocity_text = font.render(f"v: {rocket.vel.length():.1f} m/s", True, WHITE)
        fuel_text = font.render(f"f: {rocket.fuel:.1f} kg", True, WHITE)
        throttle_text = font.render(f"t: {rocket.throttle * 100:.0f}%", True, WHITE)

        screen.blit(altitude_text, (10, 10))
        screen.blit(velocity_text, (10, 50))
        screen.blit(fuel_text, (10, 90))
        screen.blit(throttle_text, (10, 130))

        # # 显示控制说明
        # controls_text1 = small_font.render("控制: 上下箭头 - 油门, 左右箭头 - 转向", True, WHITE)
        controls_text2 = small_font.render(f"Pos{rocket.pos}", True, WHITE)
        # screen.blit(controls_text1, (10, HEIGHT - 60))
        screen.blit(controls_text2, (10, HEIGHT - 30))

        if game_state == "CRASHED":
            crash_text = font.render("Fail - R to Reset", True, RED)
            screen.blit(crash_text, (WIDTH // 2 - 180, HEIGHT // 2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()