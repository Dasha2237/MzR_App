import threading

import pygame
import sys
import os

import socketClient

pygame.init()

factory = socketClient.PygameClientFactory()
server_thread = threading.Thread(target=socketClient.twisted_thread, args=(factory,), daemon=True)
server_thread.start()
# Constants
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
FPS = 30

# Colors
BACKGROUND_COLOR = (230, 255, 230)  # Light green
BUTTON_COLOR = (34, 139, 34)  # Forest green
BUTTON_HOVER_COLOR = (50, 205, 50)  # Lime green
TEXT_COLOR = (255, 255, 255)  # White
INSTRUCTION_COLOR = (0, 100, 0)  # Dark green

# Animation Duration
ANIMATION_DURATION = 2  # seconds
#ROBOT_DONE = pygame.USEREVENT + 1
#data = "smth"
# event = pygame.event.Event(ROBOT_DONE, message=data)


class Page:
    def __init__(self, name, screen, instruction):
        self.name = name
        self.screen = screen
        self.next = None
        self.instruction = instruction
        self.font = pygame.font.Font(None, 36)
        self.button_rect = pygame.Rect(0, 0, 0, 0)
        self.button_color = BUTTON_COLOR
        self.hovered = False

    def handle_events(self, event):
        pass

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.button_rect.collidepoint(mouse_pos)
        self.button_color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR

    def render(self):
        screen_width, screen_height = self.screen.get_size()
        self.screen.fill(BACKGROUND_COLOR)

        # Update button position and size
        self.button_rect = pygame.Rect(0.2 * screen_width, 0.7 * screen_height, 0.6 * screen_width, 0.2 * screen_height)

        # Render text for the button
        button_font_size = int(0.65 * min(self.button_rect.width, self.button_rect.height))
        self.font = pygame.font.Font(None, button_font_size)
        text = self.font.render('Fertig', True, TEXT_COLOR)
        text_rect = text.get_rect(center=self.button_rect.center)

        # Draw rounded button
        pygame.draw.rect(self.screen, self.button_color, self.button_rect, border_radius=20)
 
        # Draw button text
        self.screen.blit(text, text_rect)

        # Render instruction text
        font_instruction = pygame.font.Font(None, int(0.08 * screen_height))
        text_instruction = font_instruction.render(self.instruction, True, INSTRUCTION_COLOR)
        text_instruction_rect = text_instruction.get_rect(center=(screen_width // 2, screen_height // 10))
        self.screen.blit(text_instruction, text_instruction_rect)


class WelcomePage(Page):
    def __init__(self, name, screen, instruction):
        super().__init__(name, screen, instruction)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.next = 'animation'


class SecondPage(Page):
    def __init__(self, name, screen, instruction):
        super().__init__(name, screen, instruction)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.next = 'third'

class ThirdPage(Page):
    def __init__(self, name, screen, instruction):
        super().__init__(name, screen, instruction)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.next = 'fourth'
                
class FourthPage(Page):
    def __init__(self, name, screen, instruction):
        super().__init__(name, screen, instruction)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.next = 'welcome'

class AnimationPage(Page):
    def __init__(self, name, screen, image_sequence, next_page):
        super().__init__(name, screen, "")
        self.images = [pygame.image.load(img).convert_alpha() for img in image_sequence]
        self.current_frame = 0
        self.frame_count = len(self.images)
        self.next_page = next_page
        self.start_time = None

    def handle_events(self, event):
        pass

    def update(self):
        if self.start_time is None:
            self.start_time = pygame.time.get_ticks()

        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
        print(pygame.time.get_ticks(), self.start_time, elapsed_time)
        self.current_frame = int(elapsed_time * FPS) % self.frame_count

        if elapsed_time > ANIMATION_DURATION:
            self.next = self.next_page

    def render(self):
        self.screen.fill(BACKGROUND_COLOR)
        screen_width, screen_height = self.screen.get_size()

        if self.images:
            image = self.images[self.current_frame]
            image_rect = image.get_rect(center=(screen_width // 2, screen_height // 2))
            self.screen.blit(image, image_rect)


def fade_out(screen, color, speed=5):
    """Fade out the screen."""
    fade_surface = pygame.Surface(screen.get_size())
    fade_surface.fill(color)
    for alpha in range(0, 256, speed):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)


def fade_in(screen, color, speed=5):
    """Fade in the screen."""
    fade_surface = pygame.Surface(screen.get_size())
    fade_surface.fill(color)
    for alpha in range(255, -1, -speed):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    pygame.display.set_caption("App with Animations")

    # Image sequences for animations
    # animation_images = [f"frame_{i}.png" for i in range(1, 6)]  # Replace with actual paths to your image frames
    animation_images = ["healthy.png"]

    # Ensure image files exist
    for img in animation_images:
        if not os.path.exists(img):
            raise FileNotFoundError(f"Image {img} not found. Ensure images are placed correctly.")

    pages = {
        'welcome': WelcomePage("welcome", screen, "Hallo Markus! Willkommen am Arbeitsplatz"),
        'second': SecondPage("second", screen, "Lege die Tüte wie gezeigt in die Klammer"),
        'third': ThirdPage("third",screen,"Öffne die Tüte und lege sie in die andere Klammer"),
        'fourth': FourthPage("fourth",screen,"Drehe Mutter an die Schraube"),
        'animation': AnimationPage("animation", screen, animation_images, 'second'),
    }
    current_page = pages['welcome']
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == socketClient.ROBOT_DONE:
                print("Robot")
                factory.client.sendMessage("message")
            current_page.handle_events(event)

        if current_page.next:
            fade_out(screen, BACKGROUND_COLOR, speed=10)
            next_page = pages[current_page.next]
            current_page.next = None
            current_page = next_page
            if type(current_page) == AnimationPage:
                print("animation")
                current_page.start_time = pygame.time.get_ticks()
            fade_in(screen, BACKGROUND_COLOR, speed=10)

        current_page.update()
        current_page.render()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


main()

