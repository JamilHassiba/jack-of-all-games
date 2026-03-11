from static.states.state import State

class intermission(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("IntermissionState entered")
        self.elapsed = 0

    def Update(self, dt):
        self.elapsed += dt

        if self.elapsed >= 10:
            self.fsm.SetState("round_start")

    def OnExit(self):
        print("IntermissionState exited")


class round_start(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("RoundStartState entered")
        self.fsm.root.NewRound()
        self.elapsed = 0

    def Update(self, dt):
        self.elapsed += dt

        if self.elapsed >= 1:
            self.fsm.SetState("players_turn")

    def OnExit(self):
        print("RoundStartState exited")


class players_turn(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("PlayersTurnState entered")
        self.elapsed = 0

    def Update(self, dt):
        self.elapsed += dt
        if self.fsm.root.current_round.AllPlayersFinished() or self.elapsed > 5:
            self.fsm.SetState("dealer_turn")

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