import json
import threading

import pyaudio
from moviepy.editor import VideoFileClip
import pygame
import sys
import os
import socketClient
from vosk import Model, KaldiRecognizer
from PIL import Image
import random


pygame.init()
lastrandom= ""

factory = socketClient.PygameClientFactory()
server_thread = threading.Thread(target=socketClient.twisted_thread, args=(factory,), daemon=True)
server_thread.start()

model = Model(r"C:\Users\alexk\PycharmProjects\pyspeech\vosk-model-de-0.21")
recognizer = KaldiRecognizer(model, 16000, '["fertig", "gemacht", "stop", "[unk]"]')
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)

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
ANIMATION_DURATION = 5  # seconds

class Page:
    def __init__(self, name, screen, instruction, videopath=None):
        self.name = name
        self.screen = screen
        self.next = None
        self.instruction = instruction
        self.font = pygame.font.Font(None, 36)
        self.button_rect = pygame.Rect(0, 0, 0, 0)
        self.button_color = BUTTON_COLOR
        self.hovered = False
        self.video_clip = None
        self.video_surface = None
        self.video_frame_gen = None
        self.videopath = videopath

    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within a given width when rendered."""
        words = text.split(' ')
        lines = []
        current_line = ''

        for word in words:
            # Check if adding the next word exceeds the max width
            test_line = current_line + word + ' '
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                # Add the current line to lines and start a new line
                lines.append(current_line)
                current_line = word + ' '

        # Add any remaining text as the last line
        if current_line:
            lines.append(current_line)

        return lines
    def handle_events(self, event):
        pass

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.button_rect.collidepoint(mouse_pos)
        self.button_color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR

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
        pygame.draw.rect(self.screen, self.button_color, self.button_rect, border_radius=20)

        # Draw button text
        self.screen.blit(text, text_rect)

        # Render instruction text
        max_width = screen_width * 0.8  # Define the maximum width for the text area
        font_instruction = pygame.font.Font(None, int(0.08 * screen_height))
        lines = self.wrap_text(self.instruction, font_instruction, max_width)
        y = screen_height * 0.1
        for line in lines:
            text_surface = font_instruction.render(line, True, INSTRUCTION_COLOR)
            self.screen.blit(text_surface, (screen_width * 0.1, y))
            y += font_instruction.get_linesize()
        # text_instruction = font_instruction.render(self.instruction, True, INSTRUCTION_COLOR)
        # text_instruction_rect = text_instruction.get_rect(center=(screen_width // 2, screen_height // 10))
        # self.screen.blit(text_instruction, text_instruction_rect)


class WelcomePage(Page):
    def __init__(self, name, screen, instruction):
        super().__init__(name, screen, instruction)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.next = 'second'
                factory.client.sendMessage("fertig")


class SecondPage(Page):
    def __init__(self, name, screen, instruction, videopath):
        super().__init__(name, screen, instruction, videopath)

    def render(self):
        screen_width, screen_height = self.screen.get_size()
        self.screen.fill(BACKGROUND_COLOR)

        if self.videopath and self.video_surface:
            video_x = (screen_width - self.video_width) // 2
            video_y = (screen_height - self.video_height) // 2 - screen_height//10
            self.screen.blit(self.video_surface, (video_x, video_y))

        # Render instruction text
        font_instruction = pygame.font.Font(None, int(0.08 * screen_height))
        text_instruction = font_instruction.render(self.instruction, True, INSTRUCTION_COLOR)
        text_instruction_rect = text_instruction.get_rect(center=(screen_width // 2, screen_height // 10))
        self.screen.blit(text_instruction, text_instruction_rect)
        data = stream.read(8192)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            a = result['text']
            print(a)
            if ("fertig" in a):
                print("Du bist fertig")
                self.next = 'third'
                factory.client.sendMessage("fertig")

class ThirdPage(Page):
    def __init__(self, name, screen, instruction, videopath):
        super().__init__(name, screen, instruction, videopath)

    def render(self):
        screen_width, screen_height = self.screen.get_size()
        self.screen.fill(BACKGROUND_COLOR)
        if self.videopath and self.video_surface:
            video_x = (screen_width - self.video_width) // 2
            video_y = (screen_height - self.video_height) // 2 - screen_height // 10
            self.screen.blit(self.video_surface, (video_x, video_y))

        # Render instruction text
        font_instruction = pygame.font.Font(None, int(0.08 * screen_height))
        text_instruction = font_instruction.render(self.instruction, True, INSTRUCTION_COLOR)
        text_instruction_rect = text_instruction.get_rect(center=(screen_width // 2, screen_height // 10))
        self.screen.blit(text_instruction, text_instruction_rect)
        data = stream.read(8192)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            a = result['text']
            print(a)
            if ("fertig" in a):
                print("Du bist fertig")
                self.next = 'fourth'
                factory.client.sendMessage("fertig")


class FourthPage(Page):
    def __init__(self, name, screen, instruction, videopath):
        super().__init__(name, screen, instruction, videopath)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.next = 'fifth'
                factory.client.sendMessage("fertig")


class FifthPage(Page):
    def __init__(self, name, screen, instruction, videopath):
        super().__init__(name, screen, instruction, videopath)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.next = 'sixth'
                factory.client.sendMessage("fertig")


class SixthPage(Page):
    def __init__(self, name, screen, instruction, videopath):
        super().__init__(name, screen, instruction, videopath)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.next = 'seventh'
                factory.client.sendMessage("fertig")


class SeventhPage(Page):
    def __init__(self, name, screen, instruction, videopath):
        super().__init__(name, screen, instruction, videopath)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.next = 'eighth'
                factory.client.sendMessage("fertig")

class EighthPage(Page):
    def __init__(self, name, screen, instruction, videopath):
        super().__init__(name, screen, instruction, videopath)

    def render(self):
        screen_width, screen_height = self.screen.get_size()
        self.screen.fill(BACKGROUND_COLOR)
        if self.videopath and self.video_surface:
            video_x = (screen_width - self.video_width) // 2
            video_y = (screen_height - self.video_height) // 2 - screen_height // 10
            self.screen.blit(self.video_surface, (video_x, video_y))
        # Render instruction text
        font_instruction = pygame.font.Font(None, int(0.08 * screen_height))
        text_instruction = font_instruction.render(self.instruction, True, INSTRUCTION_COLOR)
        text_instruction_rect = text_instruction.get_rect(center=(screen_width // 2, screen_height // 10))
        self.screen.blit(text_instruction, text_instruction_rect)
        data = stream.read(8192)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            a = result['text']
            print(a)
            if ("fertig" in a):
                print("Du bist fertig")
                self.next = 'ninth'
                factory.client.sendMessage("fertig")

class NinthPage(Page):
    def __init__(self, name, screen, instruction, videopath):
        super().__init__(name, screen, instruction, videopath)

    def render(self):
        screen_width, screen_height = self.screen.get_size()
        self.screen.fill(BACKGROUND_COLOR)
        if self.videopath and self.video_surface:
            video_x = (screen_width - self.video_width) // 2
            video_y = (screen_height - self.video_height) // 2 - screen_height // 10
            self.screen.blit(self.video_surface, (video_x, video_y))
        # Render instruction text
        font_instruction = pygame.font.Font(None, int(0.08 * screen_height))
        lines = self.wrap_text(self.instruction, font_instruction, max_width)
        y = screen_height * 0.1
        for line in lines:
            text_surface = font_instruction.render(line, True, INSTRUCTION_COLOR)
            self.screen.blit(text_surface, (screen_width * 0.1, y))
            y += font_instruction.get_linesize()
        # text_instruction = font_instruction.render(self.instruction, True, INSTRUCTION_COLOR)
        # text_instruction_rect = text_instruction.get_rect(center=(screen_width // 2, screen_height // 10))
        # self.screen.blit(text_instruction, text_instruction_rect)
        data = stream.read(8192)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            a = result['text']
            print(a)
            if ("fertig" in a):
                print("Du bist fertig")
                self.next = 'tenth'
                factory.client.sendMessage("fertig")

class PausePage(Page):
    def __init__(self, name, screen, instruction):
        super().__init__(name, screen, instruction)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.next = 'second'
class TenthPage(Page):
    def __init__(self, name, screen, instruction):
        super().__init__(name, screen, instruction)
        self.pause_rect = pygame.Rect(0, 0, 0, 0)
    def render(self):
        screen_width, screen_height = self.screen.get_size()
        self.screen.fill(BACKGROUND_COLOR)

        # Update button position and size
        self.button_rect = pygame.Rect(0.2 * screen_width, 0.7 * screen_height, 0.25 * screen_width, 0.2 * screen_height)
        self.pause_rect = pygame.Rect(0.55 * screen_width, 0.7 * screen_height, 0.25 * screen_width, 0.2 * screen_height)


        # Render text for the button
        button_font_size = int(0.4 * min(self.button_rect.width, self.button_rect.height))
        self.font = pygame.font.Font(None, button_font_size)
        text = self.font.render('Weiter Arbeiten', True, TEXT_COLOR)
        text_rect = text.get_rect(center=self.button_rect.center)
        text_p = self.font.render('Pause', True, TEXT_COLOR)
        text_rect_p = text.get_rect(center=self.pause_rect.center)

        # Draw rounded button
        pygame.draw.rect(self.screen, self.button_color, self.button_rect, border_radius=20)
        pygame.draw.rect(self.screen, self.button_color, self.pause_rect, border_radius=20)


        # Draw button text
        self.screen.blit(text, text_rect)
        self.screen.blit(text_p, text_rect_p)

        # Render instruction text
        font_instruction = pygame.font.Font(None, int(0.08 * screen_height))
        text_instruction = font_instruction.render(self.instruction, True, INSTRUCTION_COLOR)
        text_instruction_rect = text_instruction.get_rect(center=(screen_width // 2, screen_height // 10))
        self.screen.blit(text_instruction, text_instruction_rect)
    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.next = 'second'
            if self.pause_rect.collidepoint(event.pos):
                self.next = 'pause'
# class AnimationPage(Page):
#     def __init__(self, name, screen, image_sequence, next_page):
#         super().__init__(name, screen, "", None)
#         self.images = [pygame.image.load(img).convert_alpha() for img in image_sequence]
#         self.current_frame = 0
#         self.frame_count = len(self.images)
#         self.next_page = next_page
#         self.start_time = None
#
#     def handle_events(self, event):
#         pass
#
#     def update(self):
#         if self.start_time is None:
#             self.start_time = pygame.time.get_ticks()
#
#         elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
#         self.current_frame = int(elapsed_time * FPS) % self.frame_count
#
#         if elapsed_time > ANIMATION_DURATION:
#             self.next = self.next_page
class AnimationPage(Page):
    def __init__(self, name, screen, gif_path):
        super().__init__(name, screen, "", None)
        self.gif_path = gif_path
        self.frames = []
        self.current_frame = 0
        self.frame_count = 0
        self.start_time = None
        self.isGifPage = False
        self.next_page = None
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
            print("time")
            self.sound_effect.stop()
            self.next = self.next_page
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
    # def render(self):
    #     self.screen.fill(BACKGROUND_COLOR)
    #     screen_width, screen_height = self.screen.get_size()
    #
    #     if self.images:
    #         image = self.images[self.current_frame]
    #         image_rect = image.get_rect(center=(screen_width // 2, screen_height // 2))
    #         self.screen.blit(image, image_rect)


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

    # Image sequences for animations
    # animation_images = [f"frame_{i}.png" for i in range(1, 6)]  # Replace with actual paths to your image frames
    animation_images = ["healthy.png"]

    # Ensure image files exist
    for img in animation_images:
        if not os.path.exists(img):
            raise FileNotFoundError(f"Image {img} not found. Ensure images are placed correctly.")

    pages = {
        'welcome': WelcomePage("welcome", screen, "Hallo Markus! Willkommen am Arbeitsplatz. Drücke Fertig wenn du willst Arbeit starten."),
        'second': SecondPage("second", screen, "Lege die Tüte wie gezeigt in die rechte Klammer und sage Fertig", "test.mp4"),
        'third': ThirdPage("third", screen, "Öffne die Tüte und lege sie in die linke Klammer und sage Fertig", "test2.mp4"),
        'fourth': FourthPage("fourth", screen, "Drehe Mutter an die erste Schraube", "test2.mp4"),
        'fifth': FifthPage("fifth", screen, "Nehme Schraube vom Tisch und Lege sie in die Tüte", "test2.mp4"),
        'sixth': SixthPage("sixth", screen, "Drehe Mutter an die zweite Schraube", "test2.mp4"),
        'seventh': SeventhPage("seventh", screen, "Nehme Schraube vom Tisch und Lege sie in die Tüte und sage Fertig", "test2.mp4"),
        'eighth': EighthPage("eighth", screen, "Nehme die Tüte von die rechte Klammer und sage Fertig", "test2.mp4"),
        'ninth': NinthPage("ninth", screen, "Nehme die Tüte von die linke Klammer, schließe sie und lege in die fertigen Korb", "test2.mp4"),
        'tenth': TenthPage("tenth", screen, "Willst du eine Pause haben oder weiter arbeiten?"),
        'pause': PausePage("pause", screen, "Wenn du bist bereit weiter zu arbeiten drücke bitte weiter"),
        'animation': AnimationPage("animation", screen, random_Gif(gif_list)),
    }
    current_page = pages['welcome']
    current_page.play_video()  # Starte das Video für die Seiten außer der Willkommensseite
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                current_page.play_video()  # Resize video when the window is resized
            # if event.type == socketClient.ROBOT_DONE:
            #     print("Robot")
                # factory.client.sendMessage("message")

            current_page.handle_events(event)

        if current_page.next:
            fade_out(screen, BACKGROUND_COLOR, speed=10)
            if type(current_page) != WelcomePage and type(current_page) != AnimationPage \
                    and type(current_page) != TenthPage and type(current_page) != PausePage:
                next_page = current_page.next
                current_page.next = None
                current_page = pages['animation']
                current_page.next_page = next_page
                current_page.gif_path = random_Gif(gif_list)
                current_page.load_gif_frames()
                current_page.reset()  # Reset the animation page attributes
            else:
                next_page = pages[current_page.next]
                current_page.next = None
                current_page = next_page

            # Start animation page
            if type(current_page) == AnimationPage:
                print("animation")
                current_page.start_time = pygame.time.get_ticks()

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