import pygame
import pygame.freetype


class Text:

    # text = Text(pantallita, {'x' : 200, 'y' : 200, 'width' : 200, 'height' : 40}, 10, (255,255,255))

    def __init__(self, screen, chat_pos, font_size: int = 8, color: str = "black"):

        self.CHATBOX_POS = pygame.Rect(chat_pos['x'], chat_pos['y'], chat_pos['width'], chat_pos['height'])

        self.screen = screen

        pygame.key.start_text_input()
        input_rect = pygame.Rect(0, 0, 30, 10)
        pygame.key.set_text_input_rect(input_rect)

        FONTNAMES = ["notosanscjktcregular", "notosansmonocjktcregular", "notosansregular,",
                     "microsoftjhengheimicrosoftjhengheiuilight", "microsoftyaheimicrosoftyaheiuilight",
                     "msgothicmsuigothicmspgothic", "msmincho", "Arial"]

        self.FONTNAMES = ",".join(str(x) for x in FONTNAMES)
        self.Font = pygame.freetype.SysFont(FONTNAMES, font_size)
        self.FontSmall = pygame.freetype.SysFont(FONTNAMES, font_size)
        print("Using font: " + self.Font.name)

        self.TEXTCOLOR = color

        self._IMEEditing = False
        self._IMEText = ""
        self._IMETextPos = 0
        self._IMEEditingText = ""
        self._IMEEditingPos = 0
        self.ChatList = []
        self.CHATLIST_MAXSIZE = 20

    def text_edit(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_BACKSPACE:
                if len(self._IMEText) > 0 and self._IMETextPos > 0:
                    self._IMEText = self._IMEText[0:self._IMETextPos - 1] + self._IMEText[self._IMETextPos:]
                    self._IMETextPos = max(0, self._IMETextPos - 1)

            elif event.key == pygame.K_DELETE:
                self._IMEText = self._IMEText[0:self._IMETextPos] + self._IMEText[self._IMETextPos + 1:]

            elif event.key == pygame.K_LEFT:
                self._IMETextPos = max(0, self._IMETextPos - 1)

            elif event.key == pygame.K_RIGHT:
                self._IMETextPos = min(len(self._IMEText), self._IMETextPos + 1)

            elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER] and len(event.unicode) == 0:
                # Block if we have no text to append
                if len(self._IMEText) == 0:
                    pass

                # Append chat list
                self.ChatList.append(self._IMEText)
                if len(self.ChatList) > self.CHATLIST_MAXSIZE:
                    self.ChatList.pop(0)
                self._IMEText = ""
                self._IMETextPos = 0

        elif event.type == pygame.TEXTINPUT:

            self._IMEEditing = False
            self._IMEEditingText = ""
            self._IMEText = self._IMEText[0:self._IMETextPos] + event.text + self._IMEText[self._IMETextPos:]
            self._IMETextPos += len(event.text)

    def text_update(self):

        # Chat box updates
        start_pos = self.CHATBOX_POS.copy()
        ime_textL = ">" + self._IMEText[0:self._IMETextPos]
        # ime_textM = self._IMEEditingText[0:self._IMEEditingPos] + "|" + self._IMEEditingText[self._IMEEditingPos:]
        # ime_textR = self._IMEText[self._IMETextPos:]

        rect_textL = self.Font.render_to(self.screen, start_pos, ime_textL, self.TEXTCOLOR)
        start_pos.x += rect_textL.width

    @staticmethod
    def text_end():

        pygame.key.stop_text_input()

    def text_return(self):
        return self._IMEText
