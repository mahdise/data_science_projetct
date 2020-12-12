from actions.action import Action
import random

human_readable_names = {
    "fallback_action": "I didn't really know what to say",
    "greet_action": "we said hello",
    "tfidf_discuss_action": "we talked about climate change",
    "embedding_discuss_action": "we discussed climate change",
    "lda_discuss_action": "we spoke about climate change",
    "static_question_action": "we smalltalked a bit",
    "regex_static_question_action": "we smalltalked a little",
    "recap_action": "we talked about what we talked about",
    "topic_suggestion_action": "I suggested a topic",
    "farewell_action": "we said goodbye"
}


class RecapAction(Action):
    """
    Action in which the chatbot provides the user with possible topics for a discussion
    """

    def applicable(self, state):
        if state["request"] in ("what did we talk about", "how did we get here", "i lost my thought"):
            return 1
        return None

    async def apply(self, io, state):
        if not state["path"]:
            await io.reply("We didn't do anything yet :D")
            return
        recap = ["Ooookay, first"]
        for p in state["path"][:-1]:
            recap.append(human_readable_names[p])
            recap.append(random.choice(("and then", "after that", "then")))
        recap.append(human_readable_names[state["path"][-1]])
        recap.append("and that's how we got here!")
        await io.reply(" ".join(recap))

    def name(self):
        return "recap_action"
