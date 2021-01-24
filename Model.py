from copy import deepcopy


class Variable:
    def __init__(self, position: tuple, value, degree: int, set_flag: bool, priority: float, table_size: int, domain):
        self.position = position
        self.table_size = table_size
        self.degree = degree
        self.set_flag = set_flag
        self.priority = priority
        self.value = value
        self.domain = domain
        self.domain_size = len(self.domain)
        self.type = None

    @staticmethod
    def count_adjacent(position: tuple, table_size: int):
        x, y = position
        if x == 0 or y == 0 or x == table_size - 1 or y == table_size - 1:
            if (x, y) == (0, 0) or (x, y) == (table_size - 1, 0) or (x, y) == (0, table_size - 1) or (x, y) == (table_size - 1, table_size - 1):
                return 2
            return 3
        return 4

    def set_value(self, value):
        self.value = value
        self.set_flag = True

    def is_Empty(self):
        return self.domain_size == 0

    def __ge__(self, other):
        return self.priority >= other.priority

    def __lt__(self, other):
        return self.priority < other.priority

    def __str__(self):
        return "Position : " + str((self.position[0]+1, self.position[1]+1)) + " | Degree : " + str(self.degree) + " | Type : " + self.type + " | Set_Flag : " + str(self.set_flag)


class NumberVariable(Variable):
    def __init__(self,  value: int, position: tuple, degree: int, set_flag: bool, priority: float, table_size: int, color_count: int, domain: set):
        super().__init__(position, value, degree, set_flag, priority, table_size, domain)
        self.type = "NUMBER"
        self.color_count = color_count

    def get_neighbours(self):
        neighbours = []
        for i in range(self.table_size):
            if i != self.position[0]:
                neighbours.append((i, self.position[1]))
            if i != self.position[1]:
                neighbours.append((self.position[0], i))
        return neighbours

    def update_priority(self):
        self.priority = max(self.table_size, self.color_count) - self.domain_size + (self.degree / (2 * self.table_size + 3))

    def modify_domain(self, value):
        self.domain.remove(value)

    def __str__(self):
        prefix = super().__str__()
        return '{}  | Value {} | Domain {} | Domain_size {} | Priority {}'.format(prefix, self.value, self.domain, self.domain_size, self.priority)


class ColorVariable(Variable):
    def __init__(self, value: str, position: tuple, domain: dict, degree: int, set_flag: bool, priority: float, table_size: int, color_count: int):
        super().__init__(position, value, degree, set_flag, priority, table_size, domain)
        self.type = "COLOR"
        self.color_count = color_count

    def get_neighbours(self):
        neighbours = []
        if self.position[0]-1 > -1:
            neighbours.append((self.position[0]-1, self.position[1]))

        if self.position[0]+1 < self.table_size:
            neighbours.append((self.position[0]+1, self.position[1]))

        if self.position[1]-1 > -1:
            neighbours.append((self.position[0], self.position[1]-1))

        if self.position[1]+1 < self.table_size:
            neighbours.append((self.position[0], self.position[1]+1))

        return neighbours

    def update_priority(self):
        self.priority = max(self.table_size, self.color_count) - self.domain_size + (self.degree / (2*self.table_size+3))

    def modify_domain(self, value):
        self.domain.pop(value, None)

    def __str__(self):
        prefix = super().__str__()
        return '{}  | Value {} | Domain {} | Domain_size {} | Priority {}'.format(prefix, self.value, self.domain, self.domain_size, self.priority)


class State:
    def __init__(self, size_table: int, number_variables: list, color_variables: list, complete_variables: int, priorities: list):
        self.size_table = size_table
        self.number_variables = number_variables
        self.color_variables = color_variables
        self.complete_variables = complete_variables
        self.priorities = priorities
        self.status = "active"

    def deactivate_state(self):
        self.status = "disable"

    def complete_check(self):
        return self.complete_variables == 2 * self.size_table * self.size_table

    def set_value(self, position: tuple, type_variable: str, value):
        if type_variable == "NUMBER":
            self.number_variables[position[0]][position[1]].set_value(value)
        else:
            self.color_variables[position[0]][position[1]].set_value(value)

        self.complete_variables += 1

    def forward_checking(self, variable):
        if type(variable) == NumberVariable:
            neighbours = variable.get_neighbours()
            for position in neighbours:
                x, y = position
                if self.number_variables[x][y].set_flag is False:
                    if variable.value in self.number_variables[x][y].domain:
                        self.number_variables[x][y].modify_domain(variable.value)

                    self.number_variables[x][y].domain_size -= 1
                    if self.number_variables[x][y].is_Empty():
                        return -1
                    self.number_variables[x][y].degree -= 1

        if type(variable) == ColorVariable:
            neighbours = variable.get_neighbours()
            for position in neighbours:
                x, y = position

                if self.color_variables[x][y].set_flag is False:
                    if variable.value in self.color_variables[x][y].domain:
                        self.color_variables[x][y].modify_domain(variable.value)
                    self.color_variables[x][y].domain_size -= 1
                    if self.color_variables[x][y].is_Empty():
                        return -1
                    self.color_variables[x][y].degree -= 1

    def MRV_degree(self):
        self.priorities.sort()
        selected_variable = self.priorities.pop(0)
        return selected_variable

    def next_childes(self):
        pass

    def __str__(self):
        representation = ""
        representation += "\n----------Number Variable----------\n"
        for line in self.number_variables:
            for n_variable in line:
                representation += n_variable.__str__() + "\n"

        representation += "\n----------Color Variable----------\n"
        for line in self.color_variables:
            for c_variable in line:
                representation += c_variable.__str__() + "\n"

        representation += "============Information===========\n"
        representation += "Complete Variables : " + str(self.complete_variables) + "\n"
        representation += "Status : " + self.status + "\n"
        representation += "Table size : " + str(self.size_table)
        return representation


class IO:
    def __init__(self):
        self.color_count = 0
        self.table_size = 0
        self.colors = {}
        self.number_variables = None
        self.color_variables = None
        self.complete_variables = 0
        self.priorities = []

    def get_input(self):
        self.color_count, self.table_size = map(int, input().split())

        self.number_variables = [[None for i in range(self.table_size)] for j in range(self.table_size)]
        self.color_variables = [[None for i in range(self.table_size)] for j in range(self.table_size)]

        priority_color = self.color_count
        for color in input().split():
            self.colors[color] = priority_color
            priority_color -= 1

        init_number_assignment = []
        init_color_assignment = []

        for x in range(self.table_size):
            line = input().split()
            for y in range(self.table_size):

                degree = 2 * self.table_size - 2 + Variable.count_adjacent((x, y), self.table_size)
                priority = max(self.table_size, self.color_count) - self.table_size + (degree / (2*self.table_size+3))
                domain = set(range(1, self.table_size+1))

                if line[y][0].isdigit():
                    value = int(line[y][0])
                    init_number_assignment.append((x, y, value))

                new_variable = NumberVariable(None, (x, y), degree, False, priority, self.table_size, self.color_count, domain)

                self.priorities.append(new_variable)
                self.number_variables[x][y] = new_variable

                degree = 2 * Variable.count_adjacent((x, y), self.table_size)
                priority = max(self.table_size, self.color_count) - 4 + (degree / (2 * self.table_size + 3))

                if line[y][1].isalpha():
                    value = line[y][1]
                    init_color_assignment.append((x, y, value))

                new_variable = ColorVariable("None", (x, y), deepcopy(self.colors), degree, False, priority, self.table_size, self.color_count)

                self.priorities.append(new_variable)
                self.color_variables[x][y] = new_variable

        return self.color_count, self.table_size, self.number_variables, self.color_variables, self.complete_variables,\
               self.priorities, init_number_assignment, init_color_assignment


if __name__ == "__main__":
    IO_parser = IO()
    color_count, table_size, number_variables, color_variables, complete_variables, priorities , init_number_assignment, init_color_assignment = IO_parser.get_input()
    init_state = State(table_size, number_variables, color_variables, complete_variables, priorities)

    print(init_state)
    for item in init_number_assignment:
        init_state.set_value((item[0], item[1]), "NUMBER", item[2])
        init_state.forward_checking(number_variables[item[0]][item[1]])

    for item in init_color_assignment:
        init_state.set_value((item[0], item[1]), "COLOR", item[2])
        init_state.forward_checking(color_variables[item[0]][item[1]])
        print(init_state)




