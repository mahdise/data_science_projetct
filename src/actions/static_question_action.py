from actions.action import Action
import random


class StaticQuestionAction(Action):
    """
    Action in which the user asks static questions, e.g. about the character.
    """

    def __init__(self):
        self.q_a_matches = {
            ("what are you", "who are you"):
                ("I am a chatbot developed in a data science project at the University of Bremen."
                 + "I am here to answer your questions about climate change."),
            ("thanks", "thank you", "thank you very much", "thank you so much"):
                ("You're welcome!", "No problemo!", "Most welcome!", "Sure thing!"),
            ("how is it going", "how are you doing", "are you doing ok"):
                ("Good", "Fine", "Okay", "Great", "Could be better, not so great, thanks."),
            "do you like people":
                "I love all the people who care for the climate and its health.",
            "what day is today":
                "Not quite sure, would you check your calendar, please?",
            ("who is your boss", "who is your master"):
                "In this free world, I don’t have any master. I have a lot of friends and you are surely one of them.",
            "have you heard the news":
                "What good news?",
            ("which languages do you speak", "do you speak english"):
                "At the moment, I speak only English",
            "how are you":
                ("I am doing well.", "I am doing well, how about you?", "Very well, thanks.",
                 "Fine, and what about you?")
        }
        self.cached_responses = None

    def applicable(self, state):
        for intent, responses in self.q_a_matches.items():
            if state["request"] in intent or state["request"] == intent:
                self.cached_responses = responses
                return 0.98
        return None

    async def apply(self, io, state):
        if isinstance(self.cached_responses, tuple):
            await io.reply(random.choice(self.cached_responses))
        else:
            await io.reply(self.cached_responses)

    def name(self):
        return "static_question_action"
