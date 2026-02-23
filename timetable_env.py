print("ENV FILE LOADED")
import gymnasium as gym
from gymnasium import spaces
import numpy as np


class TimetableEnv(gym.Env):

    def __init__(self):
        super().__init__()

        self.slots = 5
        self.rooms = 3

        # timetable grid (state)
        self.state = np.zeros((self.slots, self.rooms), dtype=int)

        # action = course_id, slot, room
        self.action_space = spaces.MultiDiscrete([10, self.slots, self.rooms])

        # observation = timetable grid
        self.observation_space = spaces.Box(
            low=0, high=10, shape=(self.slots, self.rooms), dtype=int
        )

    def reset(self, seed=None, options=None):
        self.state = np.zeros((self.slots, self.rooms), dtype=int)
        return self.state, {}

    def step(self, action):
        course, slot, room = action

        reward = 0
        terminated = False

        # clash check
        if self.state[slot][room] != 0:
            reward = -10
        else:
            self.state[slot][room] = course
            reward = 5

        return self.state, reward, terminated, False, {}