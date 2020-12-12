import string
import random

class Agent:

    def __init__(self, io_subsystem, actions):
        self.io = io_subsystem
        self.actions = actions
        self.state = {"running": True,
                      "path": []}

    async def run(self):
        while self.state["running"]:
            request = await self.io.request()
            self.state["raw_request"] = request
            self.state["request"] = request.lower().translate(str.maketrans('', '', string.punctuation))
            actions = sorted(filter(lambda p: p[0] is not None, [[a.applicable(self.state), a] for a in self.actions]),
                             key=lambda p: p[0],
                             reverse=True)
            max_applicability = max(actions, key=lambda a: a[0])[0]
            action = random.choice(list(filter(lambda x: x[0] == max_applicability, actions)))[1]
            await action.apply(self.io, self.state)
            self.state["path"].append(action.name())
