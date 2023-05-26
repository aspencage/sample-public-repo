#!/usr/bin/python
# gui.py

from blackjack import *
import tkinter as tk
from tkinter import font as tkfont


def reset_deck():
    global deck 
    deck = Deck().shuffle()
    print("deck reset")


def hand_contains():
    return Interpreter(hand)


class App(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        spec_frames = (
            StartPage, ExplainSelfPage, ExplainGamePage, 
            ChoiceOrRandomPage, ChooseHandPage, 
            RandomHandPage, GamePage, ResultsPage
            )

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in spec_frames:
            page_name = F.__name__
            # initiates instance, anything that doesn't need to change each time 
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        # select function, anything that needs to reset when page is encountered
        try: 
            frame.select()
        except:
            pass # for static pages 



class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        str_="""🃏 Welcome to Blackjack Buddy! 🃏
        
        I'm a just-for-fun, work-in-progress program
        that exists to tell you whether you should 
        hit or stay in a simple Blackjack-inspired game."""
        label = tk.Label(self, text=str_)
        label.pack(side="top", fill="x", pady=10)
        button1 = tk.Button(self, text="Continue",
                           command=lambda: controller.show_frame("ChoiceOrRandomPage"))
        button1.pack()
        button2 = tk.Button(self, text="How do you work?",
                           command=lambda: controller.show_frame("ExplainSelfPage"))
        button2.pack()
        button3 = tk.Button(self, text="What's the game?",
                           command=lambda: controller.show_frame("ExplainGamePage"))
        button3.pack()
        tk.Label(self, text=" ").pack()



class ExplainSelfPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.controller = controller
        str_="""I'm a simulator! 👾 
        
        Starting from your drawn hand, I play twenty thousand
          games and average the results. From here, I can tell 
        you the odds and what I think you should do if you 
        want to optimize your chances of winning 🔮"""
        label = tk.Label(self, text=str_)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Back",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()



class ExplainGamePage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.controller = controller
        str_="""What exactly is the card game being played? 🤔
        
        It's a simplified and specific version of the card 
        game Blackjack. The game uses a single deck, so the
        house odds change notably based on the cards you draw. 
        Curiosity about this was the original motivation for
        the underlying code. 👩🏻‍💻 In this game, the house only
        ever draws two cards and the player sees neither."""
        label = tk.Label(self, text=str_)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Back",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()



class ChoiceOrRandomPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="""Do you want to choose your two cards 
        or draw two random cards?""")
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Choose my two cards",
                            command=lambda: controller.show_frame("ChooseHandPage"))
        button1.pack()
        button2 = tk.Button(self, text="Draw two random cards",
                            command=lambda: controller.show_frame("RandomHandPage"))
        button2.pack()
        button3 = tk.Button(self, text="Back",
                            command=lambda: controller.show_frame("StartPage"))
        button3.pack()

    # select for things that need to reset 
    def select(self):

        self.reset_deck()



class ChooseHandPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.controller = controller


    def select(self):

        for widget in self.winfo_children():
            widget.destroy()
        
        optionList = ([str(i+1) for i in range(1,10)]+["J","Q","K","A"])
        global v1
        v1 = tk.StringVar()
        v1.set("--")
        global v2
        v2 = tk.StringVar()
        v2.set("--")

        def msg(_): # command requires a positional argument with tkinter

            reset_deck()
            print("msg sent!")
            if ((v1.get() == "--") or (v2.get() == "--")):
                str_ = "Select both your card values."
            else: 
                drawn_hand = [c(v1.get()),c(v2.get())]
                global hand 
                hand = Hand(deck=deck,drawn_hand=drawn_hand)
                str_ = hand_contains().capitalize()

            label.configure(text=str_)

        c1_menu = tk.OptionMenu(self,v1,*optionList, command=msg) 
        c1_menu.pack()
        c2_menu = tk.OptionMenu(self,v2,*optionList, command=msg)
        c2_menu.pack()

        str_ = "Select both your card values."
        label = label = tk.Label(self, text=str_)
        label.pack(side="top", fill="x", pady=10)

        select = tk.Button(self, text="Select",
                           command=lambda: self.controller.show_frame("GamePage"))
        select.pack()
        back = tk.Button(self, text="Back",
                           command=lambda: self.controller.show_frame("ChoiceOrRandomPage"))
        back.pack()



class RandomHandPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.controller = controller


    def select(self):

        # erase old cards 
        for widget in self.winfo_children():
            widget.destroy()

        reset_deck()
        global hand
        hand = Hand(deck=deck,number_to_draw=2) 
        str_ = f"Your hand contains: \n{hand_contains()}." 
        label = tk.Label(self, text=str_)
        label.pack(side="top", fill="x", pady=10)

        continue_ = tk.Button(self, text="Continue",
                           command=lambda: self.controller.show_frame("GamePage"))
        continue_.pack()
        refresh = tk.Button(self, text="Refresh",
                           command=lambda: self.controller.show_frame("RandomHandPage"))
        refresh.pack()
        button = tk.Button(self, text="Back",
                           command=lambda: self.controller.show_frame("ChoiceOrRandomPage"))
        button.pack()



class GamePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller


    def select(self):

        for widget in self.winfo_children():
            widget.destroy()

        str_=f"""You hold {hand_contains()}.
        The House draws two cards, which you cannot see.
        Do you think you should hit or stay?
        (After guessing below, please allow 20 seconds 
        for the computer to play 20,000 games.)
        """
        label = tk.Label(self, text=str_)
        label.pack(side="top", fill="x", pady=10)

        def choose(str_):
            
            global chosen 
            chosen = str_

        hit = tk.Button(self, text="Hit",
                                command=lambda: [
                                    choose("hit"),
                                    self.controller.show_frame("ResultsPage")
                                    ])
        hit.pack()
        stay = tk.Button(self, text="Stay",
                                command=lambda: [
                                    choose("stay"),
                                    self.controller.show_frame("ResultsPage")
                                    ])
        stay.pack()
        just_results = tk.Button(self, text="Just show me the results",
                                command=lambda: [
                                    choose("results_only"),
                                    self.controller.show_frame("ResultsPage")
                                    ])
        just_results.pack()



class ResultsPage(tk.Frame):
    
    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        self.controller = controller 


    @ staticmethod
    def get_reco_text(hit_stay_d):

        stay_win_no_draws = calc_p_win_sans_draws(hit_stay_d["stay"])
        hit_win_no_draws = calc_p_win_sans_draws(hit_stay_d["hit"])

        str_ = ""
        str_+=f"If you hit, your estimated chance of winning is \
{round(hit_win_no_draws*100,1)}% (excluding draws).\n"
        str_+=f"If you stay, your estimated chance of winning is \
{round(stay_win_no_draws*100,1)}% (excluding draws). \n"

        if chosen != "results_only":
            str_ += f"You guessed that you should {chosen}. \n"
            if chosen == get_recommendation(hit_stay_d):
                str_ += "Blackjack Buddy agrees: "
            else:
                str_ += "Blackjack Buddy disagrees: the odds suggest that "
        else:
            str_ += "Blackjack Buddy's recommendation: "

        if stay_win_no_draws > hit_win_no_draws:
            str_+="you should stay."
        elif stay_win_no_draws < hit_win_no_draws:
            str_+="you should hit."
        else:
            str_+="you should follow your heart.\nThe odds are the same either way."

        return str_


    def select(self): 

        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text="""Testing your cards with 10,000 draws...
        Give me about 15 seconds!""")
        label.pack(side="top", fill="x", pady=10)

        restart = tk.Button(self, text="Restart",
                                command=lambda: self.controller.show_frame("ChoiceOrRandomPage"))
        restart.pack()

        hit_stay_d = get_hit_stay_probs(hand,deck)
        str_ = self.get_reco_text(hit_stay_d) 
        label.configure(text=f"You hold {hand_contains()}.\n{str_}")



app = App()
app.mainloop()  

