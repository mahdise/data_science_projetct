# GloBot - A command-line based chatbot about climate change

GloBot is a retrieval-based conversational agent, focussing on the topic of climate change. The underlying corpus is based on discussions from [Quora](https://en.quora.com/), [SkepticalScience](https://skepticalscience.com/), [StackExchange](https://stackexchange.com/), [TedTalk](https://www.ted.com/talks), [Climate-Debate](https://www.climate-debate.com/), [NASA](https://climate.nasa.gov/faq/) and [Twitter](https://twitter.com/).

## Requirements

The following missing files need to be downloaded from seafile and inserted into the respective structure:
```asciiarmor
.
├── data
│   ├── qa_pairs.json
│   ├── docs_preprocessed_topicDistribution_match.csv
│   ├── suggestions.json
|   ├── list_of_static_question.json
├── models
│   ├── vectoriser_img.pk
│   ├── lda_n20.pickle
│   ├── tf_n20.pickle
```

## Usage

Run the file `CmdMain.py`. Then proceed to chat in the console.  
Alternatively: Open the file `bot.html` in your browser and run `WSMain.py`. Then proceed to chat on the website. 

The conversation history is logged and can be found in `conversation.jsonl` (see [jsonlines](http://jsonlines.org/) for the format used).

## Extendability

The chatbot's capabilities are contained in the different `Actions`, defined in the respectively named files. Each of these specify

1. their own applicability, i.e. under what conditions the chatbot should perform this action, which might depend on the user input alone or take the hitherto state history into account. It is expected to return either a reasonable number or None.
2. their own functionality, i.e. the chatbot printing some output by calling the `IOAdapter`'s `reply` method.

Thus, instead of classic intention detection or the use of a state machine, here, the actions "compete" with one another for applicability with each user input.

For easier testing of specific action functionalities, you can call the Agent's constructor with the desired subset of instantiated `Actions` as arguments.

