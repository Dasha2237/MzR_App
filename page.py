import random
import threading
from moviepy.editor import VideoFileClip
import pygame
import sys
import os
import socketClient
from PIL import Image

pygame.init()
pygame.mixer.init()

factory = socketClient.PygameClientFactory()
server_thread = threading.Thread(target=socketClient.twisted_thread, args=(factory,), daemon=True)
server_thread.start()
#Initialize
lastrandom= ""

# Constants
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
FPS = 30
SCALE_FACTOR = 2.5

# Colors
BACKGROUND_COLOR = (230, 255, 230)  # Light green
BUTTON_COLOR = (34, 139, 34)  # Forest green
BUTTON_HOVER_COLOR = (50, 205, 50)  # Lime green
TEXT_COLOR = (255, 255, 255)  # White
INSTRUCTION_COLOR = (0, 100, 0)  # Dark green

# Animation Duration
ANIMATION_DURATION = 2  # seconds

class Page:
    def __init__(self, name, screen, instruction, videopath=None):
        self.name = name
        self.screen = screen
        self.next = None
        self.instruction = instruction
        self.font = pygame.font.Font(None, 36)
        self.button_rect1 = pygame.Rect(0, 0, 0, 0)  # Erster Button
        self.button_rect2 = pygame.Rect(0, 0, 0, 0)  # Zweiter Button
        self.button_color1 = BUTTON_COLOR
        self.button_color2 = BUTTON_COLOR
        self.hovered1 = False  # Für den ersten Button
        self.hovered2 = False  # Für den zweiten Button
        self.video_clip = None
        self.video_surface = None
        self.video_frame_gen = None
        self.videopath = videopath
        self.next_page = None
        self.isGifPage = True
        
    def handle_events(self, event):
        pass

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered1 = self.button_rect1.collidepoint(mouse_pos)
        self.hovered2 = self.button_rect2.collidepoint(mouse_pos)
        self.button_color1 = BUTTON_HOVER_COLOR if self.hovered1 else BUTTON_COLOR
        self.button_color2 = BUTTON_HOVER_COLOR if self.hovered2 else BUTTON_COLOR

        # Aktualisiere das Video
        if self.video_frame_gen:
            try:
                frame = next(self.video_frame_gen)
                self.video_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                self.video_surface = pygame.transform.scale(self.video_surface, (self.video_width, self.video_height))
            except StopIteration:
                self.video_frame_gen = None  # Video ist zu Ende

    def play_video(self):
        if self.videopath:
            self.video_clip = VideoFileClip(self.videopath)
            screen_width, screen_height = self.screen.get_size()

            # Berechne das Seitenverhältnis des Videos
            video_aspect_ratio = self.video_clip.w / self.video_clip.h

            # Berechne die neuen Dimensionen basierend auf einem Drittel der Bildschirmgröße
            target_width = screen_width // SCALE_FACTOR
            target_height = screen_height // SCALE_FACTOR

            if video_aspect_ratio > 1:
                # Wenn das Video breiter ist im Verhältnis zum Bildschirm
                self.video_width = target_width
                self.video_height = int(target_width / video_aspect_ratio)
            else:
                # Wenn das Video höher ist im Verhältnis zum Bildschirm
                self.video_height = target_height
                self.video_width = int(target_height * video_aspect_ratio)

            # Initialisiere den Frame-Generator
            self.video_frame_gen = self.video_clip.iter_frames(fps=24, dtype='uint8')

            # Skaliere das Video auf die berechnete Größe
            frame = next(self.video_frame_gen)
            self.video_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            self.video_surface = pygame.transform.scale(self.video_surface, (self.video_width, self.video_height))

    def render(self):
        screen_width, screen_height = self.screen.get_size()
        self.screen.fill(BACKGROUND_COLOR)

        # Render video if not on welcome page
        if self.videopath and self.video_surface:
            video_x = (screen_width - self.video_width) // 2 
            video_y = (screen_height - self.video_height) // 2 - screen_height//10
            self.screen.blit(self.video_surface, (video_x, video_y))

        # Update button position and size
        self.button_rect = pygame.Rect(0.2 * screen_width, 0.7 * screen_height, 0.6 * screen_width, 0.2 * screen_height)

        # Render text for the button
        button_font_size = int(0.65 * min(self.button_rect.width, self.button_rect.height))
        self.font = pygame.font.Font(None, button_font_size)
        text = self.font.render('Fertig', True, TEXT_COLOR)
        text_rect = text.get_rect(center=self.button_rect.center)

        # Draw rounded button
        pygame.draw.rect(self.screen, self.button_color1, self.button_rect, border_radius=20)

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
        self.isGifPage = False

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.next = 'animation'


class SecondPage(Page):
    def __init__(self, name, screen, instruction, videopath):
        super().__init__(name, screen, instruction, videopath)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.next = 'animation'


class ThirdPage(Page):
    def __init__(self, name, screen, instruction, videopath):
        super().__init__(name, screen, instruction, videopath)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.next = 'fourth'


class FourthPage(Page):
    def __init__(self, name, screen, instruction, videopath):
        super().__init__(name, screen, instruction, videopath)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.next = 'fifth'


class FifthPage(Page):
    def __init__(self, name, screen, instruction, videopath):
        super().__init__(name, screen, instruction, videopath)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.next = 'sixth'


class SixthPage(Page):
    def __init__(self, name, screen, instruction, videopath):
        super().__init__(name, screen, instruction, videopath)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.next = 'seventh'


class SeventhPage(Page):
    def __init__(self, name, screen, instruction, videopath):
        super().__init__(name, screen, instruction, videopath)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.next = 'last'

class LastPage(Page):
    def __init__(self, name, screen, instruction, videopath=None):
        super().__init__(name, screen, instruction, videopath)
        self.isGifPage=False

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect1.collidepoint(event.pos):
                self.next = 'second'
            
            if self.button_rect2.collidepoint(event.pos):
                self.next = 'third'
        


    def render(self):
        screen_width, screen_height = self.screen.get_size()
        self.screen.fill(BACKGROUND_COLOR)

        # Update and render position and size of the first button
        self.button_rect1 = pygame.Rect(0.2 * screen_width, 0.7 * screen_height, 0.6 * screen_width, 0.2 * screen_height)
        button_font_size = int(0.65 * min(self.button_rect1.width, self.button_rect1.height))
        self.font = pygame.font.Font(None, button_font_size)
        text1 = self.font.render('Fertig', True, TEXT_COLOR)
        text_rect1 = text1.get_rect(center=self.button_rect1.center)
        pygame.draw.rect(self.screen, self.button_color1, self.button_rect1, border_radius=20)
        self.screen.blit(text1, text_rect1)

        # Update and render position and size of the second button
        self.button_rect2 = pygame.Rect(0.2 * screen_width, 0.4 * screen_height, 0.6 * screen_width, 0.2 * screen_height)
        text2 = self.font.render('Zweiter Button', True, TEXT_COLOR)  # Text für den zweiten Button
        text_rect2 = text2.get_rect(center=self.button_rect2.center)
        pygame.draw.rect(self.screen, self.button_color2, self.button_rect2, border_radius=20)
        self.screen.blit(text2, text_rect2)

        # Render instruction text
        font_instruction = pygame.font.Font(None, int(0.08 * screen_height))
        text_instruction = font_instruction.render(self.instruction, True, INSTRUCTION_COLOR)
        text_instruction_rect = text_instruction.get_rect(center=(screen_width // 2, screen_height // 10))
        self.screen.blit(text_instruction, text_instruction_rect)

        
class AnimationPage(Page):
    def __init__(self, name, screen, gif_path):
        super().__init__(name, screen, "", None)
        self.gif_path = gif_path
        self.frames = []
        self.current_frame = 0
        self.frame_count = 0
        self.start_time = None
        self.next_page = None
        self.isGifPage = False
        self.sound_effect = pygame.mixer.Sound("Applaus.wav")

    def load_gif_frames(self):
        gif = Image.open(self.gif_path)
        self.frames = []
        try:
            while True:
                frame = gif.copy()
                frame = frame.convert('RGBA')
                pygame_image = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
                self.frames.append(pygame_image)
                gif.seek(len(self.frames))
        except EOFError:
            pass
        self.frame_count = len(self.frames)
        print(f"Loaded {self.frame_count} frames from {self.gif_path}")

    def handle_events(self, event):
        pass

    def update(self):
        if self.start_time is None:
            self.start_time = pygame.time.get_ticks()

        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
        self.current_frame = int(elapsed_time * FPS) % self.frame_count

        if elapsed_time > ANIMATION_DURATION:
            self.sound_effect.stop()
            self.next = self.next
        else:
                self.sound_effect.play()

    def render(self):
        self.screen.fill(BACKGROUND_COLOR)
        screen_width, screen_height = self.screen.get_size()

        if self.frames:
            image = self.frames[self.current_frame]
            image_rect = image.get_rect(center=(screen_width // 2, screen_height // 2))
            self.screen.blit(image, image_rect)

    def reset(self):
        self.start_time = None
        self.current_frame = 0


def fade_out(screen, color, speed):
    fade_surface = pygame.Surface(screen.get_size())
    fade_surface = fade_surface.convert()
    alpha = 0
    while alpha < 255:
        fade_surface.fill(color)
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        alpha += speed
        pygame.time.delay(10)


def fade_in(screen, color, speed):
    fade_surface = pygame.Surface(screen.get_size())
    fade_surface = fade_surface.convert()
    alpha = 255
    while alpha > 0:
        fade_surface.fill(color)
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        alpha -= speed
        pygame.time.delay(10)

def random_Gif(gif_list):
    global lastrandom
    randomize = random.choice(gif_list)
    if randomize == lastrandom:
        return random_Gif(gif_list)
    lastrandom = randomize
    return randomize

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    pygame.display.set_caption("App with Animations")
    
    gif_list = ["thumbs-up-nice.gif", "yay.gif", "well-done-3182_256.gif","cool-fun.gif"]  # List of gifs

    pages = {
        'welcome': WelcomePage("welcome", screen, "Hallo Markus! Willkommen am Arbeitsplatz"),
        'second': SecondPage("second", screen, "Lege die Tüte wie gezeigt in die Klammer", "test.mp4"),
        'third': ThirdPage("third", screen, "Öffne die Tüte und lege sie in die andere Klammer", "test2.mp4"),
        'fourth': FourthPage("fourth", screen, "Drehe Mutter an die Schraube", "test2.mp4"),
        'fifth': FifthPage("fifth", screen, "Lege Schraube eins in die Tüte", "test2.mp4"),
        'sixth': SixthPage("sixth", screen, "Drehe Mutter an die Schraube", "test2.mp4"),
        'seventh': SeventhPage("seventh", screen, "Lege Schraube zwei in die Tüte und schließe sie anschließend", "test2.mp4"),
        'animation': AnimationPage("animation", screen, random_Gif(gif_list)),
        'last': LastPage("last",screen, "Sehr gut du hast einen Durchlauf geschafft!")
    }

    # Set the next page for each page
    pages['welcome'].next_page = 'last'
    pages['second'].next_page = 'third'
    pages['third'].next_page = 'fourth'
    pages['fourth'].next_page = 'fifth'
    pages['fifth'].next_page = 'sixth'
    pages['sixth'].next_page = 'seventh'
    pages['seventh'].next_page = 'last'
    pages['last'].next_page = 'second'

    current_page = pages['welcome']
    current_page.play_video()  # Start the video for pages other than the welcome page
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                current_page.play_video()  # Resize video when the window is resized
            if event.type == socketClient.ROBOT_DONE:
                print("Robot")
                factory.client.sendMessage("message")

            current_page.handle_events(event)

        if current_page.next:
            fade_out(screen, BACKGROUND_COLOR, speed=10)
            if current_page.isGifPage == True:
                # Transition to animation page first
                animation_page = pages['animation']
                animation_page.gif_path = random_Gif(gif_list)
                animation_page.load_gif_frames()
                animation_page.reset()  # Reset the animation page attributes
                animation_page.next = current_page.next
                current_page = animation_page
            else:
                # Transition to the actual next page after the animation
                current_page = pages[current_page.next]

            current_page.next = None
            fade_in(screen, BACKGROUND_COLOR, speed=10)

            # Start video for new pages
            if current_page.name != "welcome":
                current_page.play_video()

        current_page.update()
        current_page.render()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

# Call the main function
main()
