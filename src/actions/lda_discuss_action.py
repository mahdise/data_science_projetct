from actions.action import Action
import ml


class LdaDiscussAction(Action):
    """
    Action in which the user discusses about climate change with the chatbot.
    """

    def __init__(self, lda_model_path, count_vectorizer_path, corpus_path):
        # Load models
        self.lda_model, self.count_vectorizer, self.docs_preprocessed_topics_match = ml.load_lda_model(lda_model_path, count_vectorizer_path, corpus_path)
        self.cached_output = None

    def applicable(self, state):
        # Retrieve answer from corpus.
        score, self.cached_output = ml.generate_lda_response(self.lda_model, self.count_vectorizer, self.docs_preprocessed_topics_match, state["request"])

        if self.cached_output:
            return 0.9
        return None

    async def apply(self, io, state):
        await io.reply(self.cached_output)

    def name(self):
        return "lda_discuss_action"
