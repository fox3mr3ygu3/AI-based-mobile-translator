# Arabic AI Translator App

A mobile-friendly AI-powered translator app for **Arabic texts** (Qur’an, nasheed, poetry).  
The app provides verse-by-verse translation, correct phonetic transcription, and full meaning in the target language. It also supports word-by-word translation for learning purposes.

---

## Features

- Translate Arabic text into your chosen language with **correct transcription**.  
- **Verse-by-verse translation** ensures clarity and accuracy.  
- **Word-by-word translation** mode for learning individual word meanings.  
- **Multi-line input** for long texts, nasheeds, or poetry.  
- **Save translations** locally with custom filenames.  
- **View saved translations** from within the app.  
- **Clear input/output** with a single button.  
- **Back and navigation buttons** for easy switching between screens.  
- Automatic **Arabic text reshaping** for proper display.  
- **Offline warning** if internet is not available.

---

## Screens

1. **Home Screen**
   - Buttons: `Translate` | `Saved Files`  

2. **Translator Screen**
   - Input field (multi-line)
   - Output area (translated text)
   - Buttons: `Back` | `Translate` | `Clear` | `Save`

3. **Saved Files Screen**
   - File list of saved translations
   - Buttons: `Open` | `Cancel`  

---

## Installation

### Requirements
- Python 3.10+  
- [Kivy](https://kivy.org/#home)  
- [OpenAI Python SDK](https://pypi.org/project/openai/)  
- [Arabic Reshaper](https://pypi.org/project/arabic-reshaper/)  
- [python-bidi](https://pypi.org/project/python-bidi/)  
- `dotenv` for managing API keys
- OPENAI API key   

```bash
pip install -r requirements.txt
