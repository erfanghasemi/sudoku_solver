import heapq


class Variable:
    def __init__(self, position: tuple, degree: int, set_flag: bool, priority: float, table_size: int):
        self.position = position
        self.table_size = table_size
        self.degree = degree
        self.set_flag = set_flag
        self.priority = priority
        self.type = None

    def get_neighbours(self):
        pass

    # def __hash__(self):
    #     return hash((self.position, self.type))

    def __ge__(self, other):
        return self.priority >= other.priority

    def __lt__(self, other):
        return self.priority < other.priority

    def __str__(self):
        return "Position : " + str((self.position[0]+1, self.position[1]+1)) + " | Degree : " + str(self.degree) + " | Type : " + self.type + " | Set_Flag : " + str(self.set_flag)


class NumberVariable(Variable):
    def __init__(self, value: int, position: tuple, degree: int, set_flag: bool, priority: float, table_size: int, color_count: int):
        super().__init__(position, degree, set_flag, priority, table_size)
        self.value = value
        self.domain = list(range(1, table_size+1))
        self.domain_size = len(self.domain)
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

    def is_Empty(self):
        return self.domain_size == 0

    def calculate_priority(self):
        priority = max(self.table_size, self.color_count) - self.domain_size + (self.degree / (2 * self.table_size + 3))

    def __str__(self):
        prefix = super().__str__()
        return '{}  | Value {} | Domain {} | Domain_size {} | Priority {}'.format(prefix, self.value, self.domain, self.domain_size, self.priority)


class ColorVariable(Variable):
    def __init__(self, value: str, position: tuple, domain: dict, degree: int, set_flag: bool, priority: float, table_size: int, color_count: int):
        super().__init__(position, degree, set_flag, priority, table_size)
        self.value = value
        self.domain = domain
        self.domain_size = len(self.domain)
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

    def calculate_priority(self):
        priority = max(self.table_size, self.color_count) - self.domain_size + (self.degree / (2*self.table_size+3))
        return

    def is_Empty(self):
        return self.domain_size == 0

    def __str__(self):
        prefix = super().__str__()
        return '{}  | Value {} | Domain {} | Domain_size {} | Priority {}'.format(prefix, self.value, self.domain, self.domain_size, self.priority)


class State:
    def __init__(self, size_table: int, number_variables: list, color_variables: list):
        self.size_table = size_table
        self.number_variables = number_variables
        self.color_variables = color_variables
        self.complete_variables = 0
        self.priorities = []

    def complete_check(self):
        return self.complete_variables == 2 * self.size_table * self.size_table

    def set_value(self, position: tuple, type_variable: str, value):
        if type_variable == "NUMBER":
            self.number_variables[position[0]][position[1]] = value
        else:
            self.color_variables[position[0]][position[1]] = value

        self.complete_variables += 1

    def forward_checking(self, variable: Variable):
        pass

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

        representation += "====================================="
        return representation


class IO:
    def __init__(self):
        self.color_count = 0
        self.table_size = 0
        self.colors = {}
        self.number_variables = None
        self.color_variables = None

    def get_degree(self, position: tuple, type_variable: str):
        if type_variable == "NUMBER":
            return 2 * (self.table_size-1)
        else:
            if position[0] == 0 or position[1] == 0 or position[0] == self.table_size-1 or position[1] == self.table_size-1:
                if position == (0, 0) or position == (self.table_size-1, 0) or\
                        position == (0, self.table_size-1) or position == (self.table_size-1, self.table_size-1):
                    return 2
                return 3
            return 4

    def get_input(self):
        self.color_count, self.table_size = map(int, input().split())

        self.number_variables = [[None for i in range(self.table_size)] for j in range(self.table_size)]
        self.color_variables = [[None for i in range(self.table_size)] for j in range(self.table_size)]

        priority_color = self.color_count
        for color in input().split():
            self.colors[color] = priority_color
            priority_color -= 1

        for x in range(self.table_size):
            line = input().split()
            for y in range(self.table_size):

                degree = self.get_degree((x, y), "NUMBER")
                priority = max(self.table_size, self.color_count) - self.table_size + (degree / (2*self.table_size+3))

                if line[y][0].isdigit():
                    value = int(line[y][0])
                    new_variable = NumberVariable(value, (x, y), degree, True, priority, self.table_size, self.color_count)
                else:
                    new_variable = NumberVariable(None, (x, y), degree, False, priority, self.table_size, self.color_count)
                self.number_variables[x][y] = new_variable

                degree = self.get_degree((x, y), "COLOR")
                priority = max(self.table_size, self.color_count) - 4 + (degree / (2 * self.table_size + 3))

                if line[y][1].isalpha():
                    value = line[y][1]
                    new_variable = ColorVariable(value, (x, y), self.colors, degree, True, priority, self.table_size, self.color_count)
                else:
                    new_variable = ColorVariable("None", (x, y), self.colors, degree, False, priority, self.table_size, self.color_count)

                self.color_variables[x][y] = new_variable

        return self.color_count, self.table_size, self.number_variables, self.color_variables


if __name__ == "__main__":
    IO_parser = IO()
    color_count, table_size, number_variables, color_variables = IO_parser.get_input()
    init_state = State(table_size, number_variables, color_variables)



