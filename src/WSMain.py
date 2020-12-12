import uuid

import asyncio
import websockets
import IOAdapter
import ml

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

PORT = 8765

def main():
    print("Starting server on port:" + str(PORT))
    
    file_logger = IOAdapter.FileLogger("../data/output/log.jsonl")
    sql_logger = IOAdapter.SQLiteLogger("../data/output/log.db")
    
    bot_id = botVersion()
    
    async def connect(websocket, path):
        conversation_id = str(uuid.uuid4())
        remote_ip, remote_port = websocket.remote_address
        user_id = remote_ip + ":" + str(remote_port)
        
        io_adapter = sql_logger.makeIO(conversation_id, user_id, bot_id,
                        file_logger.makeIO(conversation_id, user_id, bot_id,
                            IOAdapter.WSIO(websocket)))
        
        agent = Agent(io_adapter,
                   [  TFIDFDiscussAction(ml.load_tfidf_model_from_image("../models/vectoriser_img.pk")),
                      # EmbeddingDiscussAction(ml.load_embeddings_model_from_image("../data/qa_pairs_embedded.pk",
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
            await agent.run()
        except websockets.exceptions.ConnectionClosed:
            pass

    start_server = websockets.serve(connect, "localhost", PORT)

    try:
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    except:
        pass
    finally:
        file_logger.close()
        sql_logger.close()
        print("Server and logging stopped.")

if __name__ == "__main__":
    main()
