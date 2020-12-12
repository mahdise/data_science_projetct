from actions.action import Action
import ml


class TFIDFDiscussAction(Action):
    """
    Action in which the user discusses about climate change with the chatbot.
    """

    def __init__(self, model):
        self.model = model
        self.cached_output = None

    def applicable(self, state):
        # Retrieve anwer from corpus.
        self.cached_output = ml.generate_tfidf_response(self.model, state["request"])
        if self.cached_output:
            return 0.9
        return None

    async def apply(self, io, state):
        await io.reply(self.cached_output)

    def name(self):
        return "tfidf_discuss_action"
