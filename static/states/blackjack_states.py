from static.states.state import State


class intermission(State):
    def __init__(self, fsm):
        super().__init__(fsm)
        self.elapsed = 0

    def OnEnter(self):
        print("IntermissionState entered")
        self.elapsed = 0

    def Update(self, dt):
        self.elapsed += dt

        if self.elapsed >= 3:
            self.fsm.SetState("round_start")

    def OnExit(self):
        print("IntermissionState exited")


class round_start(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("RoundStartState entered")
        for player in self.fsm.root.players:
            for i in range(1,55):
                print(i)
                player.HitMe()

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