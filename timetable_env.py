import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd

class TimetableEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.df_subjects = pd.read_csv('subjects.csv')
        self.df_rooms = pd.read_csv('rooms.csv')
        self.num_courses = len(self.df_subjects)
        
        self.days, self.periods, self.rooms = 5, 6, 7
        self.total_actions = self.num_courses * self.days * self.periods * self.rooms
        self.action_space = spaces.Discrete(self.total_actions)
        
        # 210 slots (5*6*7)
        self.observation_space = spaces.Box(low=0, high=self.num_courses, shape=(210,), dtype=np.int32)
        self.state = np.zeros((self.days, self.periods, self.rooms), dtype=int)
        self.placed_count = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.zeros((self.days, self.periods, self.rooms), dtype=int)
        self.placed_count = 0
        return self.state.flatten().astype(np.int32), {}

    def step(self, action):
        course_idx = action // (self.days * self.periods * self.rooms)
        day = (action // (self.periods * self.rooms)) % self.days
        period = (action // self.rooms) % self.periods
        room = action % self.rooms

        reward = -0.1 # Very small penalty to keep the agent moving
        terminated = False
        
        course_info = self.df_subjects.iloc[course_idx]
        room_info = self.df_rooms.iloc[room]
        
        # 1. Hard Conflict: Slot already taken
        if self.state[day, period, room] != 0:
            reward -= 10 
        # 2. Room Type Match (e.g., Theory in Lab)
        elif course_info['room_type_needed'] != room_info['room_type']:
            reward -= 10
        # 3. Teacher Busy Check
        elif self.is_teacher_busy(course_info['teacher_code'], day, period):
            # Special case for Honours Period
            if course_info['is_honours'] and period == 3:
                reward += 50 
                self.state[day, period, room] = course_idx + 1
                self.placed_count += 1
            else:
                reward -= 20
        else:
            # SUCCESS: Place the course
            self.state[day, period, room] = course_idx + 1
            self.placed_count += 1
            reward += 100 # BIG reward for placing a class

        # Stop when all courses are placed
        if self.placed_count >= self.num_courses:
            terminated = True
            reward += 300 

        return self.state.flatten().astype(np.int32), reward, terminated, False, {}

    def is_teacher_busy(self, teacher_code, day, period):
        for r in range(self.rooms):
            cid = self.state[day, period, r]
            if cid != 0:
                if self.df_subjects.iloc[cid-1]['teacher_code'] == teacher_code:
                    return True
        return False