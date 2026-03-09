from static.states.state import State


class intermission(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("IntermissionState entered")

    def Update(self, dt):
        pass

    def OnExit(self):
        print("IntermissionState exited")


class round_start(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("RoundStartState entered")

    def Update(self, dt):
        pass

    def OnExit(self):
        print("RoundStartState exited")


class players_turn(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("PlayersTurnState entered")

    def Update(self, dt):
        pass

    def OnExit(self):
        print("PlayersTurnState exited")


class dealer_turn(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("DealerTurnState entered")

    def Update(self, dt):
        pass

    def OnExit(self):
        print("DealerTurnState exited")


class score(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("ScoreState entered")

    def Update(self, dt):
        pass

    def OnExit(self):
        print("ScoreState exited")


class cleanup(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("CleanupState entered")

    def Update(self, dt):
        pass

    def OnExit(self):
        print("CleanupState exited")