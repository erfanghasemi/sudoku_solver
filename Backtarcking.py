from collections import deque
from Model import *

if __name__ == "__main__":
    stack = deque()

    IO_parser = IO()
    init_state = IO_parser.get_input()

    stack.append(init_state)

    while len(stack) != 0:
        state = stack.pop()
        if state.complete_check():
            print("============ Answer ============ ")
            IO.give_output(state)
            exit(0)

        next_states = state.next_childes()

        for item in next_states:
            stack.append(item)

    print("We doesn't have any solution!")