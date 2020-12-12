from actions.action import Action
import random
import json
import re


def whenToSuggest(path):
    """
    Define when to show the topic suggestion list
    """
    # Check if the length of the current path is bigger than 1
    return len(path) > 1 and not path[-1] in ['topic_suggestion_action', 'tfidf_discuss_action', 'embedding_discuss_action', 'lda_discuss_action']


class TopicSuggestionAction(Action):
    """
    Action in which the chatbot provides the user with possible topics for a discussion
    """

    def __init__(self, suggestions_path, limit, start_suggestion=("suggest","suggest me something", "what can we talk about", "can you suggest something")):
        # Define keywords for entering topic suggestion
        self.start_suggestion = start_suggestion
        # Load the suggestions.
        #TODO
        topic_suggestions = None
        with open(suggestions_path) as json_file:
            topic_suggestions = json.load(json_file)
        for topic in topic_suggestions:
            topic["regex"] = re.compile(topic["regex"])
        self.topic_suggestions = topic_suggestions
        self.suggestions_limit = limit

    def applicable(self, state):
        # Check if we should interact with the topic suggestion state
        if state["request"] in self.start_suggestion or state.get('has_suggested') or whenToSuggest(state['path']):
            return 0.95
        return None

    async def apply(self, io, state):
        # Check if the topic suggestion state has already been started
        if not state.get("has_suggested", False):
            # Start the topic suggestion state
            state["has_suggested"] = True

            # Initiating topic suggestions to engage the user in a conversation
            answer = "Here are a few topics we can discuss together:\n" + "\n".join([topic["name"] for topic in
                                         random.sample(self.topic_suggestions, min(self.suggestions_limit, len(self.topic_suggestions)))])

            # Output the full answer
            await io.reply(answer)

        else:
            # Check if the user won't enter topic suggestion state
            if state["request"] in ["none", "nothing", "nothing like that", "I don't care", "no", "no thanks", "no thank you", "nah", "none of the above", "neither"]:
                await io.reply("Ask me something you want to know.")
            else:
                suggestion_output = "Ehm, I don't think that was an option..."

                # Look for the right topic suggestion
                for topic in self.topic_suggestions:

                    # Check if the user input matches the topic suggestion
                    if topic["regex"].match(state["request"]):

                        # Return a random suggestion from the file
                        suggestion_output = random.choice(topic["suggestions"])

                        # Finish the topic suggestion state
                        state["has_suggested"] = False

                        # Break the loop when the suggestion has been reached
                        break

                # Return the suggestion
                await io.reply(suggestion_output)

    def name(self):
        return "topic_suggestion_action"
