<<<<<<< Updated upstream
print("ENV FILE LOADED")
import gymnasium as gym
from gymnasium import spaces
import numpy as np
=======
"""
timetable_env.py — MEC D3QN Timetable Environment (v4)
Added:
✔ Teacher max 4 periods/day
✔ Lab = 3 consecutive periods
✔ Max 2 lab days with gap
✔ Avoid same subject overload in a day
✔ Better reward shaping (reduce blanks)
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd

DAYS     = 5
PERIODS  = 6

DIVISION_ROOM  = {"CS6A": 0, "CS6B": 1, "CS6C": 2}
HONOURS_ROOM   = 4

HONOURS_DAYS   = {1, 4}
HONOURS_PERIOD = 4
>>>>>>> Stashed changes


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
<<<<<<< Updated upstream
=======

        self._required = self.df_subjects["required_hours"].tolist()
        self.state   = None
        self._placed = None
        self.reset()
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
        return self.state, reward, terminated, False, {}
=======
        # ── Slot occupied ─────────────────────────────────────
        if self.state[day, period, room] != 0:
            return self.state.flatten(), -50.0, False, False, {}

        # ── Room type match ───────────────────────────────────
        if course["room_type_needed"] != rm["room_type"]:
            return self.state.flatten(), -50.0, False, False, {}

        # ── Honours rules ─────────────────────────────────────
        if is_hon:
            if day not in HONOURS_DAYS or period != HONOURS_PERIOD:
                return self.state.flatten(), -50.0, False, False, {}
            if room != HONOURS_ROOM:
                return self.state.flatten(), -50.0, False, False, {}

        # ── Theory division fixed room ────────────────────────
        if not is_hon and course["room_type_needed"] == "Theory":
            if division != "ALL":
                if room != DIVISION_ROOM.get(division, -1):
                    return self.state.flatten(), -50.0, False, False, {}

        # ── Avoid honours slot for normal subjects ────────────
        if not is_hon and day in HONOURS_DAYS and period == HONOURS_PERIOD:
            return self.state.flatten(), -30.0, False, False, {}

        # ── Teacher clash ─────────────────────────────────────
        if self._is_teacher_busy(course["teacher_code"], day, period):
            return self.state.flatten(), -100.0, False, False, {}

        # ── Teacher max 4 periods per day ─────────────────────
        teacher_count = 0
        for r in range(self.num_rooms):
            for p in range(PERIODS):
                cid = self.state[day, p, r]
                if cid != 0:
                    c = self.df_subjects.iloc[cid - 1]
                    if c["teacher_code"] == course["teacher_code"]:
                        teacher_count += 1

        if teacher_count >= 4:
            return self.state.flatten(), -100.0, False, False, {}

        # ── Lab constraints ───────────────────────────────────
        if course["room_type_needed"] == "Lab":

            # must fit 3 consecutive periods
            if period > PERIODS - 3:
                return self.state.flatten(), -100.0, False, False, {}

            for i in range(3):
                if self.state[day, period + i, room] != 0:
                    return self.state.flatten(), -100.0, False, False, {}

            # lab distribution check
            lab_days = set()
            for d in range(DAYS):
                for p in range(PERIODS):
                    for r in range(self.num_rooms):
                        cid = self.state[d, p, r]
                        if cid != 0:
                            c = self.df_subjects.iloc[cid - 1]
                            if c["division"] == division and c["room_type_needed"] == "Lab":
                                lab_days.add(d)

            if len(lab_days) >= 2 and day not in lab_days:
                return self.state.flatten(), -80.0, False, False, {}

            if any(abs(day - d) == 1 for d in lab_days):
                return self.state.flatten(), -80.0, False, False, {}

        # ── Avoid same subject too much in one day ─────────────
        same_course_today = 0
        for r in range(self.num_rooms):
            for p in range(PERIODS):
                if self.state[day, p, r] == course_idx + 1:
                    same_course_today += 1

        if same_course_today >= 2:
            return self.state.flatten(), -20.0, False, False, {}

        # ── Required hours check ──────────────────────────────
        if self._placed[course_idx] >= self._required[course_idx]:
            return self.state.flatten(), -10.0, False, False, {}

        # ── SUCCESS ───────────────────────────────────────────
        reward = 100.0

        if course["room_type_needed"] == "Lab":
            for i in range(3):
                self.state[day, period + i, room] = course_idx + 1
            self._placed[course_idx] += 3
        else:
            self.state[day, period, room] = course_idx + 1
            self._placed[course_idx] += 1

        if self._placed[course_idx] == self._required[course_idx]:
            reward += 50.0

        # small penalty to reduce empty slots
        reward -= 1.0

        terminated = all(
            self._placed[i] >= self._required[i]
            for i in range(self.num_courses)
        )

        if terminated:
            reward += 500.0

        return self.state.flatten(), reward, terminated, False, {}

    def _is_teacher_busy(self, teacher_code, day, period):
        for r in range(self.num_rooms):
            cid = self.state[day, period, r]
            if cid != 0:
                if self.df_subjects.iloc[cid - 1]["teacher_code"] == teacher_code:
                    return True
        return False

    def render(self):
        pass
>>>>>>> Stashed changes
