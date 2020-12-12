from actions.action import Action
import ml


class EmbeddingDiscussAction(Action):
    """
    Action in which the user discusses about climate change with the chatbot.
    """

    def __init__(self, model):
        self.model = model
        self.cached_output = None

    def applicable(self, state):
        # Retrieve anwer from corpus.
        score, output = ml.generate_embeddings_response(self.model, state["request"])
        if score >= 0.3:
            self.cached_output = output
            return score
        return None

    async def apply(self, io, state):
        await io.reply(self.cached_output)

    def name(self):
        return "embedding_discuss_action"
