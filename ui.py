import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import threading

from test2 import QUESTION_PROMPT, RECOMENDATION_PROMPT, SANDWICH_LIST

# Use CustomTkinter's modern theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class SandwichRecommenderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Rodilla Sandwich Recommender 🥪")
        self.geometry("800x600")
        self.configure(fg_color="#FFFFFF")  # Rodilla white background

        # Colors (Rodilla-inspired)
        self.colors = {
            "primary": "#D4202C",  # Rodilla red
            "secondary": "#F7D117",  # Rodilla yellow
            "text": "#333333",
            "background": "#FFFFFF"
        }

        # Initialize chat components
        self.llm = ChatGroq(
            temperature=0.7,
            model_name="mixtral-8x7b-32768"
        )
        self.answers = []
        self.current_question = 0

        self.create_widgets()

    def create_widgets(self):
        # Header Frame
        self.header_frame = ctk.CTkFrame(self, fg_color=self.colors["primary"], height=100)
        self.header_frame.pack(fill="x", padx=0, pady=0)

        # Logo/Title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Sandwich Recommender",
            font=("Helvetica", 24, "bold"),
            text_color="white"
        )
        self.title_label.pack(pady=30)

        # Main Content Frame
        self.content_frame = ctk.CTkFrame(self, fg_color=self.colors["background"])
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Welcome Message
        self.welcome_label = ctk.CTkLabel(
            self.content_frame,
            text="¡Bienvenido a tu recomendador personal de sándwiches!\nDescubramos tu sándwich perfecto.",
            font=("Helvetica", 16),
            text_color=self.colors["text"]
        )
        self.welcome_label.pack(pady=20)

        # Question Display
        self.question_label = ctk.CTkLabel(
            self.content_frame,
            text="",
            font=("Helvetica", 14),
            text_color=self.colors["text"],
            wraplength=600
        )
        self.question_label.pack(pady=20)

        # Answer Input
        self.answer_entry = ctk.CTkEntry(
            self.content_frame,
            width=400,
            height=40,
            placeholder_text="Escribe tu respuesta aquí..."
        )
        self.answer_entry.pack(pady=20)

        # Next Button
        self.next_button = ctk.CTkButton(
            self.content_frame,
            text="Siguiente",
            command=self.handle_answer,
            fg_color=self.colors["primary"],
            hover_color=self.colors["secondary"],
            height=40
        )
        self.next_button.pack(pady=20)

        # Result Display
        self.result_text = ctk.CTkTextbox(
            self.content_frame,
            width=600,
            height=200,
            font=("Helvetica", 12),
            fg_color="#F5F5F5",
            text_color=self.colors["text"]
        )
        self.result_text.pack(pady=20)
        self.result_text.pack_forget()  # Hidden initially

        # Progress Indicator
        self.progress_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.progress_frame.pack(pady=10)
        
        self.progress_dots = []
        for i in range(3):
            dot = ctk.CTkLabel(
                self.progress_frame,
                text="○",
                font=("Helvetica", 20),
                text_color=self.colors["primary"]
            )
            dot.pack(side="left", padx=5)
            self.progress_dots.append(dot)

        # Start the first question
        self.ask_next_question()

    def ask_next_question(self):
        def get_question():
            chain = QUESTION_PROMPT | self.llm
            response = chain.invoke({
                "previous_answers": "\n".join(self.answers)
            })
            self.question_label.configure(text=response.content)
            self.next_button.configure(state="normal")

        self.next_button.configure(state="disabled")
        threading.Thread(target=get_question).start()
        
        # Update progress dots
        for i in range(3):
            self.progress_dots[i].configure(
                text="●" if i < self.current_question else "○"
            )

    def handle_answer(self):
        answer = self.answer_entry.get()
        if answer.strip():
            self.answers.append(f"Q{self.current_question + 1}: {self.question_label.cget('text')}\nA{self.current_question + 1}: {answer}")
            self.answer_entry.delete(0, 'end')
            
            self.current_question += 1
            
            if self.current_question < 3:
                self.ask_next_question()
            else:
                self.show_recommendation()

    def show_recommendation(self):
        def get_recommendation():
            sandwich_info = "\n".join([
                f"- {s['name']}: {', '.join(s['attributes'])} | Ingredients: {', '.join(s['ingredients'])}"
                for s in SANDWICH_LIST
            ])
            
            chain = RECOMENDATION_PROMPT | self.llm
            recommendation = chain.invoke({
                "sandwich_list": sandwich_info,
                "all_answers": "\n".join(self.answers)
            })
            
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", recommendation.content)
            self.result_text.pack(pady=20)
            self.next_button.pack_forget()
            self.answer_entry.pack_forget()
            self.question_label.configure(text="¡Tu sándwich perfecto está listo!")

        self.next_button.configure(state="disabled")
        threading.Thread(target=get_recommendation).start()

if __name__ == "__main__":
    app = SandwichRecommenderApp()
    app.mainloop()
