from actions.action import Action
import random


class FallbackAction(Action):
    """
    Action for when no other answer is suitable.
    """

    def applicable(self, state):
        return 0

    # Called when running the action.
    async def apply(self, io, state):
        await io.reply(random.choice(("Sorry, I don't understand.", "Say again?", "Uhhhh...", "Could you rephrase that :/?")))

    # The name of the action used for history logging.
    def name(self):
        return "fallback_action"
