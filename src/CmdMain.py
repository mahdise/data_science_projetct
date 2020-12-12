import asyncio
import IOAdapter
import ml
import uuid
import getpass

from Version import botVersion
from Agent import *

from actions.greet_action import GreetAction
from actions.tfidf_discuss_action import TFIDFDiscussAction
from actions.embedding_discuss_action import EmbeddingDiscussAction
from actions.static_question_action import StaticQuestionAction
from actions.regex_static_question_action import RegexStaticQuestionAction
from actions.recap_action import RecapAction
from actions.topic_suggestion_action import TopicSuggestionAction
from actions.fallback_action import FallbackAction
from actions.farewell_action import FarewellAction
from actions.lda_discuss_action import LdaDiscussAction


def main():
    conversation_id = str(uuid.uuid4())
    bot_id = botVersion()
    user_id = getpass.getuser()

    file_logger = IOAdapter.FileLogger("../data/output/log.jsonl")
    sql_logger = IOAdapter.SQLiteLogger("../data/output/log.db")
    io_adapter = sql_logger.makeIO(conversation_id, user_id, bot_id,
                                   file_logger.makeIO(conversation_id, user_id, bot_id,
                                                      IOAdapter.CommandLineIO()))

    agent = Agent(io_adapter,
                  [TFIDFDiscussAction(ml.load_tfidf_model_from_image("../models/vectoriser_img.pk")),
                   #EmbeddingDiscussAction(ml.load_embeddings_model_from_image("../data/qa_pairs_embedded.pk",
                   #                                                           "https://storage.googleapis.com/tfhub-modules/google/universal-sentence-encoder/4.tar.gz")),
                   # LdaDiscussAction("../models/lda_n20.pickle", "../models/tf_n20.pickle","../data/docs_preprocessed_topicDistribution_match_20.csv"),
                   FarewellAction(),
                   StaticQuestionAction(),
                   GreetAction(),
                   TopicSuggestionAction("../data/suggestions.json", 3),
                   FallbackAction(),
                   RecapAction(),
                   RegexStaticQuestionAction()
                   ])

    try:
        asyncio.run(agent.run())
    finally:
        sql_logger.close()
        file_logger.close()


if __name__ == "__main__":
    main()
