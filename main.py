import os 
import socket
import arabic_reshaper
from dotenv import load_dotenv
from openai import OpenAI


from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from bidi.algorithm import get_display
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.filechooser import FileChooserListView


SAVE_DIR = "saved_files"
os.makedirs(SAVE_DIR, exist_ok=True)


load_dotenv(override=True)
openai_api_key = os.getenv("OPENAI_API_KEY")


if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")


openai = OpenAI()
MODEL = 'gpt-4o'

system_message = '''You are an AI translator specialized in Arabic texts (Qur’an, nasheed, poetry). 
Always output results verse by verse in the following format:

1. Original Arabic text (exact as given)  
2. Correct phonetic transcription (how it should be read aloud, no extra vowels)  
3. Meaning in the target language (full verse meaning, natural translation, not literal word order)

If the user requests "word-by-word translation," then for each word show:
- Word in Arabic  
- Correct transcription  
- Meaning in the target language  

After finishing the word-by-word list, always include the full verse meaning at the end.

Rules:
- Ensure the transcription strictly follows Arabic pronunciation rules, without adding vowels that are not read.  
- The meaning must be accurate and natural in the target language (no mistranslation).  
- Work verse by verse, never mixing verses together.  
- Respect the sanctity of Qur’anic text: do not distort or alter meanings.
Word-by-Word Mode (only and only when the user requests it):
- In addition to the normal output, provide a breakdown of each Arabic word:
  - Word in Arabic
  - Its transcription in the target language
  - Its meaning in the target language
- After this breakdown, still include the **full translation of the entire text** at the end.
- This is for learning purposes, so the user can see how each word maps to its meaning and pronunciation.'''


def is_connected(host="8.8.8.8", port=53, timeout=3):
    """Check internet connection"""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False



# Screens

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=50, spacing=20)

        translate_btn = Button(text="Translate", font_size=32)
        translate_btn.bind(on_press=lambda _: setattr(self.manager, 'current', 'translator'))
        saved_btn = Button(text="Saved Files", font_size=32)
        saved_btn.bind(on_press=lambda _: setattr(self.manager, 'current', 'saved_files'))

        layout.add_widget(translate_btn)
        layout.add_widget(saved_btn)
        self.add_widget(layout)


class TranslatorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Chat history / output
        self.output_area = Label(
            text="",
            font_name="fonts/Amiri-Regular.ttf",
            font_size=18,
            halign="right",
            valign="top",
            size_hint_y=None,
            text_size=(480, None),
        )
        self.output_area.bind(texture_size=self._update_height)
        scroll = ScrollView(size_hint=(1, 0.6))
        scroll.add_widget(self.output_area)
        layout.add_widget(scroll)

        # Input box
        self.input_box = TextInput(
            hint_text="Input your text...",
            font_name="fonts/Amiri-Regular.ttf",
            font_size=20,
            size_hint=(1, 0.2),
            multiline=True
        )
        layout.add_widget(self.input_box)

        # Buttons
        back_btn = Button(text="Back")
        back_btn.bind(on_press=lambda _: setattr(self.manager, 'current', 'home'))
        btn_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)
        translate_btn = Button(text="Translate")
        translate_btn.bind(on_press=self.translate_text)
        clear_btn = Button(text="Clear")
        clear_btn.bind(on_press=self.clear_text)
        save_btn = Button(text="Save")
        save_btn.bind(on_press=self.save_file)
        btn_layout.add_widget(back_btn)
        btn_layout.add_widget(translate_btn)
        btn_layout.add_widget(clear_btn)
        btn_layout.add_widget(save_btn)
        layout.add_widget(btn_layout)

        self.add_widget(layout)
        self.messages = [{"role": "system", "content": system_message}]

    def _update_height(self, instance, value):
        self.output_area.height = self.output_area.texture_size[1]

    def clear_text(self, instance):
        self.input_box.text = ""
        self.output_area.text = ""

    def translate_text(self, instance):
        user_message = self.input_box.text.strip()
        if not user_message:
            return

        if not is_connected():
            popup = Popup(title="No Internet", content=Label(text="⚠️ Please check your internet connection."), size_hint=(0.7, 0.3))
            popup.open()
            return

        reshaped = arabic_reshaper.reshape(user_message)
        bidi_text = get_display(reshaped)
        self.output_area.text += f"You: {bidi_text}\n"
        self.input_box.text = ""
        self.messages.append({"role": "user", "content": user_message})

        try:
            # Call OpenAI API
            stream = openai.chat.completions.create(
                model=MODEL,
                messages=self.messages,
                stream=True
            )
            response = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                response += delta
            self.output_area.text += f"AI:\n{response}\n"
            self.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            popup = Popup(title="Error", content=Label(text=f"⚠️ {str(e)}"), size_hint=(0.8, 0.3))
            popup.open()

    def save_file(self, instance):
        if not self.output_area.text.strip():
            return

        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        filename_input = TextInput(hint_text="Enter file name...", multiline=False)
        btns = BoxLayout(size_hint_y=None, height=40, spacing=10)
        save_btn = Button(text="Save")
        cancel_btn = Button(text="Cancel")
        btns.add_widget(save_btn)
        btns.add_widget(cancel_btn)
        content.add_widget(filename_input)
        content.add_widget(btns)
        popup = Popup(title="Save File", content=content, size_hint=(0.8, 0.4))

        def do_save(_):
            filename = filename_input.text.strip()
            if filename:
                path = os.path.join(SAVE_DIR, f"{filename}.txt")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.output_area.text)
                popup.dismiss()
        save_btn.bind(on_press=do_save)
        cancel_btn.bind(on_press=lambda _: popup.dismiss())
        popup.open()


class SavedFilesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        self.file_chooser = FileChooserListView(path=SAVE_DIR)
        self.layout.add_widget(self.file_chooser)

        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        open_btn = Button(text="Open")
        cancel_btn = Button(text="Cancel")
        btn_layout.add_widget(open_btn)
        btn_layout.add_widget(cancel_btn)
        self.layout.add_widget(btn_layout)
        self.add_widget(self.layout)

        open_btn.bind(on_press=self.open_file)
        cancel_btn.bind(on_press=lambda _: setattr(self.manager, 'current', 'home'))

    def open_file(self, instance):
        selection = self.file_chooser.selection
        if selection:
            with open(selection[0], "r", encoding="utf-8") as f:
                content = f.read()
            # Switch to TranslatorScreen and show content
            self.manager.get_screen('translator').output_area.text = content
            self.manager.current = 'translator'


class TranslatorApp(App):
    def build(self):
        Window.size = (500, 700)  # optional for desktop
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(TranslatorScreen(name='translator'))
        sm.add_widget(SavedFilesScreen(name='saved_files'))
        return sm


if __name__ == "__main__":
    TranslatorApp().run()