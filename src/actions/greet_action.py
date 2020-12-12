from actions.action import Action
import random


class GreetAction(Action):
    """
    Initial Action for greeting the user.
    """

    def __init__(self, greets=("hi", "hello", "good evening", "good afternoon",
                               "hi there", "good morning", "morning", "evening", "hey", "hey there")):
        self.greets = greets

    def applicable(self, state):
        if state["request"] in self.greets:
            return 1
        return None

    async def apply(self, io, state):
        if state.get("has_greeted", None):
            await io.reply(random.choice(self.greets) + " again")
        else:
            await io.reply(random.choice(self.greets))
        state["has_greeted"] = True

    def name(self):
        return "greet_action"
