class Action:
    # Called to determine whether the action is runnable,
    # return None if not otherwise return priority (higher priority wins).
    def __init__(self):
        pass

    def applicable(self, state):
        raise NotImplementedError("Can't check if Action is applicable.")

    # Called when running the action.
    async def apply(self, io, state):
        raise NotImplementedError("Can't apply Action.")

    # The name of the state used for history logging
    def name(self):
        raise NotImplementedError("Can't get name of Action.")
