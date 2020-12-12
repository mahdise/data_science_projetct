from actions.action import Action
from nltk.corpus import wordnet as wn
import re
import random
import json


class RegexStaticQuestionAction(Action):
    """
    Action in which the user asks static questions, e.g. about the character.
    """

    def __init__(self):
        self.patterns = {}
        self.cached_intent = None
        self.intent_question_match = []
        # Words for frequent intents, that can be detected via regexes containing respective synonyms.
        list_words = ['hello', 'describe', 'thank']
        dict_syn = {}

        # Read the file, containing intents matched with possible chatbot answers.
        with open('../data/list_of_static_question.json') as f:
            self.intent_question_match = json.load(f)

        for word in list_words:
            synonyms = []
            for syn in wn.synsets(word):
                for lem in syn.lemmas():
                    synonyms.append(lem.name())

            dict_syn[word] = set(synonyms)

        keywords = {'appreciation': ['.*you are cute|beautiful|handsome|smart|intelligent'],
                    'thanks': [],
                    'identity': ['.*who are you.*'],
                    'goodbye': ['.*goodbye.*|.*bye.*'],
                    'weather': ['.*what.*weather.*|.*about.*weather'],
                    'location': ['.*where.*live.*|.*your location'],
                    'bot_age': ['.*how old.*|.*your age'],
                    'bot_gender': ['.*what.* sex|are you.*boy or.*girl|are you a boy|are you a girl'],
                    'bot_language': ['.*what .*built| .*written in'],
                    'bot_story': ['.*your story.*| what story do you have?'],
                    'bot_offering': ['what do you offer|.*your offering'],
                    'bot_outlook': ['how do you look'],
                    'datetime': ['.*what time is it'],
                    'asking_help': ['.*how can you help me'],
                    'human': ['.*are you human'],
                    'love': ['.*do you love me'],
                    'real': ['.*are you real'],
                    'bot_friend': ['.*do you have friend.*'],
                    'bot_speciality': ['.*why are you special|.*your speciallity'],
                    'user_data': ['.*what.*my data|.*use my data'],
                    'bot_purpose': ['.*what.*you do|why would.*chat with you'],
                    'borrow': ['.*can i borrow.*'],
                    'color': ['.*what.*favorite color'],
                    'joke': ['.*tell me.*joke|.*know.*joke'],
                    'funny_phrases': ['.*will you marry me|.*are you single'],
                    'impatience': ['.*want.*answer now|where is my answer|you are lazy'],
                    'unsatisfied': ['you are annoying|suck|boring|bad|crazy'],
                    'asking_live_conv': ['.*want to speak .* human|live agent|customer service'],
                    'not_happy': ['.*you are not making .*sense'],
                    'bot_gratitude': ['.*nice to meet you|.*pleasure to meet you'],
                    'bot_creator': ['.*who created you|.*who made you|who is your boss'],
                    'ask_ques': ['.*can i ask.*question|.*anything'],
                    'whatsup': ['what.*up|how is going|how going']
                    }

        for synonym in list(dict_syn['thank']):
            keywords['thanks'].append('.*thank|thx|tnx|thanks a lot\\b' + synonym + '\\b.*')

        for intent, keys in keywords.items():
            self.patterns[intent] = re.compile('|'.join(keys))

    def applicable(self, state):
        for intent, pattern in self.patterns.items():
            if re.search(pattern, state["request"]):
                self.cached_intent = intent
                return 0.98
        return None

    async def apply(self, io, state):
        await io.reply(random.choice(self.intent_question_match[self.cached_intent]))

        # Stop the chatbot when user said goodbye.
        if self.cached_intent == "goodbye":
            state["running"] = False

    def name(self):
        return "regex_static_question_action"
