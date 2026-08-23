from static.states.state import State

class intermission(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("IntermissionState entered")
        self.elapsed = 0
        for player in self.fsm.root.players:
            player.SetState('lobby')

    def Update(self, dt):
        self.elapsed += dt

        if self.elapsed >= 2:
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

    def Update(self, dt):
        if self.fsm.root.current_round and self.fsm.root.current_round.AreAllPlayersFinished():
            self.fsm.SetState("dealer_turn")

    def OnExit(self):
        print("PlayersTurnState exited")


class dealer_turn(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("DealerTurnState entered")
        self.elapsed = 0

    def Update(self, dt):
        self.elapsed += dt
        if self.elapsed >= 1:
            self.elapsed = 0

            if self.fsm.root.dealer.ShouldIDraw():
                self.fsm.root.dealer.DealToSelf()
            else:
                self.fsm.SetState("score")

    def OnExit(self):
        print("DealerTurnState exited")


class score(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("ScoreState entered")
        self.elapsed = 0
        self.fsm.root.EvaluateRound()

    def Update(self, dt):
        self.elapsed += dt
        if self.elapsed >= 1:
            self.fsm.SetState('cleanup')

    def OnExit(self):
        print("ScoreState exited")


class cleanup(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("CleanupState entered")
        self.elapsed = 0
        self.fsm.root.CleanupRound()

    def Update(self, dt):
        self.elapsed += dt
        if self.elapsed >= 1:
            self.fsm.SetState('evaluate_game')

    def OnExit(self):
        print("CleanupState exited")

        
class evaluate_game(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("EvaluateGameState entered")
        self.elapsed = 0
        self.fsm.root.EvaluateGame()

    def Update(self, dt):
        self.elapsed += dt
        if self.elapsed >= 1:
            self.fsm.SetState('intermission')

    def OnExit(self):
        print("EvaluateGameState exited")