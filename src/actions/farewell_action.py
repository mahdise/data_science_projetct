from actions.action import Action
import random


class FarewellAction(Action):
    """
    Action in which the chatbot says goodbye to the user.
    """

    def applicable(self, state):
        if state["request"] in ("bye", "goodbye", "see ya", "see you", "cheers"):
            return 1
        return None

    async def apply(self, io, state):
        await io.reply(random.choice(("Goodbye and thanks for your interest in climate change! 🌱",
                                "Cheers, mate!", "Have a nice day, I hope you had a pleasant conversation. :)")))
        state["running"] = False

    def name(self):
        return "farewell_action"
