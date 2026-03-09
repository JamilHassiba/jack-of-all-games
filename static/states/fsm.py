class fsm():
    # states is a dictionary of string to state objects
    def __init__(self, root, states, initial_state: str):
        self.__root = root
        self.__current_state_name: str = initial_state
        self.__states = states

    def Update(self, dt):
        self.GetCurrentState().Update(dt)

    # Getters
    def GetCurrentState(self):
        return self.__states[self.__current_state_name]

    # Setters
    def SetState(self, new_state_name: str):
        if not new_state_name in self.states.keys:
            return
        
        # Call previous states exit method
        old_state = self.GetCurrentState()
        old_state.OnExit()

        self.__current_state_name = new_state_name
        new_state = self.GetCurrentState()
        new_state.OnEnter()

    
