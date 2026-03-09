class fsm():
    def __init__(self, root):
        self.root = root

    # states is a dictionary of string to state objects
    def SetStates(self, states):
        self.__states = states
        self.__current_state_name: str = ""

    def Begin(self, initial_state_name):
        self.__current_state_name = initial_state_name
        state = self.GetCurrentState()
        state.OnEnter()
        
    def Update(self, dt):
        self.GetCurrentState().Update(dt)

    # Getters
    def GetCurrentState(self):
        return self.__states[self.__current_state_name]

    # Setters
    def SetState(self, new_state_name: str):
        if self.__current_state_name == "":
            return
        if not new_state_name in self.__states.keys():
            return
        
        # Call previous states exit method
        old_state = self.GetCurrentState()
        old_state.OnExit()

        self.__current_state_name = new_state_name
        new_state = self.GetCurrentState()
        new_state.OnEnter()

    
