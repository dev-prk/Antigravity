class Player:
    def __init__(self, name, goals=0):
        self.name = name
        self._goals = 0
        self.goals = goals

    @property
    def goals(self):
        return self._goals

    @goals.setter
    def goals(self, value):
        try:
            val = int(value)
            if val < 0:
                self._goals = 0
            else:
                self._goals = val
        except (ValueError, TypeError):
            self._goals = 0

def clean_input(value):
    return str(value.strip())

import sys

lines = sys.stdin.read().strip().split('\n')
name, goal = map(clean_input, lines[0].strip().split(","))
next_goal = lines[1] if len(lines) > 1 else ""

player = Player(name, goal)
print(name)
print(player.goals)
player.goals = next_goal
print(player.goals)
