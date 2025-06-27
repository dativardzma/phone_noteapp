from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Ellipse, Color
from kivy.uix.stencilview import StencilView
import sqlite3
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView


conn = sqlite3.connect('sqlite.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT
    )
''')

conn.commit()
conn.close()

class GetStartedScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        btn = Button(
            text="Start",
            font_size=18,
            size_hint=(None, None),
            size=(150, 50),
            pos=(Window.width / 2 - 75, Window.height / 2 - 60)
        )
        txt = Label(
            text="press to get started", 
            size_hint=(None, None), 
            pos=(Window.width / 2 - 55, Window.height / 2 - 30), 
            color=(1, 1, 1, 1),
            font_size=40
        )
        btn.bind(on_press=self.go_to_second)
        layout.add_widget(txt)
        layout.add_widget(btn)
        self.add_widget(layout)

    def go_to_second(self, instance):
        self.manager.current = "login"

class CircularImage(StencilView):
    def __init__(self, source, size, pos, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            # Draw circle mask
            self.size = size
            self.pos = pos
            self.circle = Ellipse(pos=pos, size=size)
        
        # Add the image, same size and position as the circle
        self.image = Image(
            source=source,
            size=size,
            pos=pos,
            allow_stretch=True,
            keep_ratio=False
        )
        self.add_widget(self.image)

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        welcome_txt = Label(
            text="Welcome, dati",
            size_hint=(None, None),
            pos=(Window.width / 2 - 50, Window.height / 2 + 150),
            color=(1, 1, 1, 1),
            font_size=50
        )

        profile_picture = CircularImage(
            source='profile_picture.jpg',
            size=(150, 150),
            pos=(Window.width / 2 - 75, Window.height / 2 + 30)
        )

        self.input_field = TextInput(
            hint_text="Password...",
            size_hint=(None, None),
            size=(200, 40),
            pos=(Window.width / 2 - 100, Window.height / 2 - 30),
            multiline=False,
            password=True
        )

        # Rename the method you’re binding
        self.input_field.bind(on_text_validate=self.on_enter_pressed)

        layout.add_widget(welcome_txt)
        layout.add_widget(profile_picture)
        layout.add_widget(self.input_field)
        self.add_widget(layout)

    def on_enter_pressed(self, instance):
        print("You typed:", instance.text)
        password = 'dati123'
        if instance.text == password:
            print('correct')
            self.manager.current = "main"
        else:
            print('incorrect')
            self.manager.current = 'login'


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self.add_widget(self.layout)

        title_label = Label(
            text="Notes",
            size_hint=(None, None),
            pos=(20, Window.height - 60),
            font_size=32,
            color=(0, 1, 0, 1)
        )

        create_btn = Button(
            text="Create New Note",
            font_size=20,
            size_hint=(None, None),
            size=(200, 50),
            pos=(Window.width - 220, Window.height - 70)
        )
        create_btn.bind(on_press=self.go_to_create)

        scroll = ScrollView(
            size_hint=(None, None),
            size=(Window.width - 40, Window.height - 150),
            pos=(20, 50)
        )

        self.notes_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=0,
            spacing=10
        )
        self.notes_box.bind(minimum_height=self.notes_box.setter('height'))

        scroll.add_widget(self.notes_box)

        self.layout.add_widget(title_label)
        self.layout.add_widget(create_btn)
        self.layout.add_widget(scroll)

    def on_pre_enter(self):
        self.load_notes()

    def load_notes(self):
        self.notes_box.clear_widgets()
        conn = sqlite3.connect('sqlite.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description FROM notes")
        notes = cursor.fetchall()
        conn.close()

        for note_id, title, description in notes:
            note_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=100,
                padding=(10, 10),
                spacing=10
            )

            note_label = Label(
                text=f"[b]{title}[/b]\n{description}",
                markup=True,
                halign="left",
                valign="top"
            )
            note_label.bind(size=note_label.setter("text_size"))

            delete_btn = Button(
                text="❌",
                size_hint=(None, None),
                size=(40, 40),
                on_press=lambda btn, nid=note_id: self.delete_note(nid)
            )

            note_layout.add_widget(note_label)
            note_layout.add_widget(delete_btn)
            self.notes_box.add_widget(note_layout)

    def delete_note(self, note_id):
        conn = sqlite3.connect("sqlite.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id=?", (note_id,))
        conn.commit()
        conn.close()
        self.load_notes()

    def go_to_create(self, instance):
        self.manager.current = 'create'



class CreateNoteScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        self.title_input = TextInput(
            hint_text="Title", 
            size_hint=(None, None),
            size=(200, 45),
            pos=(Window.width / 2 - 100, Window.height / 2 + 250),
            font_size=32,
        )

        self.description_input = TextInput(
            hint_text="Description",
            size_hint=(None, None),
            size=(Window.width - 100, Window.height - 200),
            pos=(50, 100),  # Leaves 100px space on bottom and 100px on top
            font_size=20,
            multiline=True
        )

        save_btn = Button(
            text="Save",
            size_hint=(None, None),
            size=(150, 50),
            font_size=32,
            pos=(Window.width / 2 - 75, Window.height / 2 - 250)
        )

        save_btn.bind(on_press=self.note_creator)

        layout.add_widget(self.title_input)
        layout.add_widget(self.description_input)
        layout.add_widget(save_btn)
        self.add_widget(layout)

    def note_creator(self, instance):
        title = self.title_input.text
        description = self.description_input.text
        print("Title:", title)
        print("Description:", description)

        #ეს უკავშირდება ბაზას
        conn = sqlite3.connect('sqlite.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (title, description) VALUES (?, ?)", (title, description))
        conn.commit()
        #ეს კი კეტავს რომ არ გავიდეს ერრორზე
        conn.close()

        self.title_input.text = ''
        self.description_input.text = ''

        self.manager.current = 'main'

# App
class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(GetStartedScreen(name="start"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(CreateNoteScreen(name="create"))

        return sm

if __name__ == "__main__":
    MyApp().run()
