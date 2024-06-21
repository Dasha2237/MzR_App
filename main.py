import pygame
import sys
import asyncio
import websockets
import pyaudio



async def send_audio(uri):
    async with websockets.connect(uri) as websocket:
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        frames_per_buffer=8192)

        print("Recording...")

        try:
            while True:
                data = stream.read(8192, exception_on_overflow=False)
                await websocket.send(data)
                #print("send")
                response = await websocket.recv()
                print(f"Server: {response}")
                if "Detected target word" in response:
                    print("stop, detected")
                    break
        except KeyboardInterrupt:
            print("Recording stopped")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

# Initialisieren von Pygame
pygame.init()

# Festlegen der Fenstergröße
screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Screen")

# Farben
white = (255, 255, 255)
black = (0, 0, 0)
gray = (200, 200, 200)

# Button Eigenschaften
button_width = 200
button_height = 50
button_color = gray
button_hover_color = (170, 170, 170)
button_text_welcome = "Willkommen am Arbeitsplatz"
button_text_start = "Loslegen"
button_text_continue = "Weiter"
button_text_end = "Weiter arbeiten"
button_font = pygame.font.Font(None, 36)

# Nachrichten und Aktionen
messages = [
    "Öffne Tüte",
    "Drehe Mutter an die Schraube",
    "Lege Schraube eins in die Tüte",
    "Drehe Mutter an die Schraube",
    "Lege Schraube zwei in die Tüte und schließe sie anschließend",
    "Sehr gut gemacht! Jetzt hast du dir eine kleine Pause verdient!"
]

videos = [
    "Video 1 abspielen",
    "Video 2 abspielen",
    "Video 3 abspielen",
    "Video 4 abspielen",
    "Video 5 abspielen",
    "Nächstes Video abspielen"
]

# Bild für die letzte Seite
last_page_image = pygame.image.load('healthy.png')
last_page_image = pygame.transform.scale(last_page_image, (300, 300))  # Größe des Bildes anpassen

current_page_index = -1  # Startseite
SAID_STOP = pygame.USEREVENT + 1

def draw_button(screen, x, y, width, height, color, text, font):
    pygame.draw.rect(screen, color, (x, y, width, height))
    text_surface = font.render(text, True, black)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)

def draw_message(screen, message, font, x, y):
    text_surface = font.render(message, True, black)
    screen.blit(text_surface, (x, y))

def play_video(video):
    print(f"Abspielen von '{video}'")  # Hier könnte der Code zum Abspielen des Videos stehen

def main():
    global current_page_index
    running = True
    while running:
        screen.fill(white)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        if current_page_index == -1:
            draw_message(screen, button_text_welcome, button_font, 20, 20)
            button_x = screen_width - button_width - 20
            button_y = screen_height - button_height - 20
            draw_button(screen, button_x, button_y, button_width, button_height, button_color, button_text_start, button_font)
        elif current_page_index == len(messages) - 1:
            # Bild mittig platzieren
            image_x = (screen_width - last_page_image.get_width()) // 2
            image_y = (screen_height - last_page_image.get_height()) // 2
            screen.blit(last_page_image, (image_x, image_y))

            button_x = screen_width - button_width - 20  # 20 Pixel Abstand vom rechten Rand
            button_y = screen_height - button_height - 20  # 20 Pixel Abstand vom unteren Rand
            # Button Hover-Effekt
            if button_x < mouse_x < button_x + button_width and button_y < mouse_y < button_y + button_height:
                button_current_color = button_hover_color
            else:
                button_current_color = button_color
            draw_button(screen, button_x, button_y, button_width, button_height, button_current_color, button_text_end, button_font)
        else:
            button_x = screen_width - button_width - 20  # 20 Pixel Abstand vom rechten Rand
            button_y = screen_height - button_height - 20  # 20 Pixel Abstand vom unteren Rand
            # Button Hover-Effekt
            if button_x < mouse_x < button_x + button_width and button_y < mouse_y < button_y + button_height:
                button_current_color = button_hover_color
            else:
                button_current_color = button_color
            draw_button(screen, button_x, button_y, button_width, button_height, button_current_color, button_text_continue, button_font)

        if current_page_index >= 0 and current_page_index < len(messages):
            draw_message(screen, messages[current_page_index], button_font, 20, 20)  # Nachricht oben links

        if current_page_index == 0:
            asyncio.get_event_loop().run_until_complete(send_audio("ws://localhost:8000/ws"))
            pygame.event.post(pygame.event.Event(SAID_STOP))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == SAID_STOP:
                current_page_index += 1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if current_page_index == -1:
                    # Weiter zur ersten Seite
                    current_page_index += 1
                elif current_page_index == len(messages) - 1:
                    # Weiter zur ersten Seite
                    current_page_index = 0
                else:
                    if button_x < mouse_x < button_x + button_width and button_y < mouse_y < button_y + button_height:
                        # Weiter zum nächsten Schritt
                        current_page_index += 1
                        # Führe die zugehörige Aktion aus
                        play_video(videos[current_page_index])

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
