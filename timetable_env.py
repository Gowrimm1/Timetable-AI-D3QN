import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd

class TimetableEnv(gym.Env):
    def __init__(self):
        super().__init__()
        
        # 1. Define Dimensions
        self.num_courses = 10
        self.slots = 5
        self.rooms = 3
        
        # 2. Action Space: One single number representing a combination
        self.total_actions = self.num_courses * self.slots * self.rooms
        self.action_space = spaces.Discrete(self.total_actions)
        
        # 3. Observation Space: Flattened grid (15 values)
        self.observation_space = spaces.Box(
            low=0, 
            high=self.num_courses, 
            shape=(self.slots * self.rooms,), 
            dtype=np.int32
        )
        
        self.state = np.zeros((self.slots, self.rooms), dtype=int)
        self.placed_count = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.zeros((self.slots, self.rooms), dtype=int)
        self.placed_count = 0
        return self.state.flatten().astype(np.int32), {}

    def step(self, action):
        # --- THE DECODER MATH ---
        # This converts action (0-149) into Course, Slot, and Room
        course = (action // (self.slots * self.rooms)) + 1 
        slot = (action // self.rooms) % self.slots
        room = action % self.rooms
        # ------------------------

        reward = 0
        terminated = False

        # RULE: Don't overlap classes
        if self.state[slot][room] != 0:
            reward = -10  # Penalty for clashing
        else:
            # SUCCESS: Place the course
            self.state[slot][room] = course
            self.placed_count += 1
            reward = 10 

        # FINISH: Stop when all courses are placed
        if self.placed_count >= self.num_courses:
            terminated = True
            reward += 50 

        return self.state.flatten().astype(np.int32), reward, terminated, False, {}