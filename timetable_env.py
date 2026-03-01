"""
timetable_env.py — MEC D3QN Timetable Environment (v3)
Fixes: Honours uses Room_309 (neutral shared room), not a division room.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd

DAYS     = 5
PERIODS  = 6

# Theory room index per division (matches rooms.csv order)
# 0=B202(CS6A), 1=B302(CS6B), 2=B303(CS6C), 3=Room_309, 4=Room_310, 5=Room_201
DIVISION_ROOM  = {"CS6A": 0, "CS6B": 1, "CS6C": 2}
HONOURS_ROOM   = 4          # Room_310 — neutral room for all-division Honours class

HONOURS_DAYS   = {1, 4}     # Tuesday=1, Friday=4
HONOURS_PERIOD = 4          # Period 5 (0-indexed)


class TimetableEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self):
        super().__init__()
        self.df_subjects = pd.read_csv("subjects.csv")
        self.df_rooms    = pd.read_csv("rooms.csv")
        self.num_courses = len(self.df_subjects)
        self.num_rooms   = len(self.df_rooms)
        self.n_slots     = DAYS * PERIODS * self.num_rooms

        self.action_space = spaces.Discrete(self.num_courses * self.n_slots)
        self.observation_space = spaces.Box(
            low=0, high=self.num_courses,
            shape=(self.n_slots,), dtype=np.int32
        )
        self._required = self.df_subjects["required_hours"].tolist()
        self.state   = None
        self._placed = None
        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state   = np.zeros((DAYS, PERIODS, self.num_rooms), dtype=np.int32)
        self._placed = [0] * self.num_courses
        return self.state.flatten(), {}

    def step(self, action):
        course_idx = int(action) // self.n_slots
        remainder  = int(action) % self.n_slots
        day        = remainder  // (PERIODS * self.num_rooms)
        period     = (remainder // self.num_rooms) % PERIODS
        room       = remainder  % self.num_rooms

        if course_idx >= self.num_courses or room >= self.num_rooms:
            return self.state.flatten(), -1.0, False, False, {}

        course   = self.df_subjects.iloc[course_idx]
        rm       = self.df_rooms.iloc[room]
        division = course["division"]
        is_hon   = bool(course["is_honours"])

        # ── Hard constraint: slot occupied ────────────────────────────────────
        if self.state[day, period, room] != 0:
            return self.state.flatten(), -50.0, False, False, {}

        # ── Hard constraint: room type must match ─────────────────────────────
        if course["room_type_needed"] != rm["room_type"]:
            return self.state.flatten(), -50.0, False, False, {}

        # ── Honours: must go in HONOURS_ROOM on Tue/Fri P5 ───────────────────
        if is_hon:
            if day not in HONOURS_DAYS or period != HONOURS_PERIOD:
                return self.state.flatten(), -50.0, False, False, {}
            if room != HONOURS_ROOM:
                return self.state.flatten(), -50.0, False, False, {}

        # ── Theory division stickiness (non-honours) ──────────────────────────
        if not is_hon and course["room_type_needed"] == "Theory":
            if division != "ALL":
                if room != DIVISION_ROOM.get(division, -1):
                    return self.state.flatten(), -50.0, False, False, {}

        # ── Non-honours must not occupy the Honours slot ──────────────────────
        if not is_hon and day in HONOURS_DAYS and period == HONOURS_PERIOD:
            return self.state.flatten(), -30.0, False, False, {}

        # ── Teacher clash ─────────────────────────────────────────────────────
        if self._is_teacher_busy(course["teacher_code"], day, period):
            return self.state.flatten(), -100.0, False, False, {}

        # ── Already fulfilled required hours ──────────────────────────────────
        if self._placed[course_idx] >= self._required[course_idx]:
            return self.state.flatten(), -10.0, False, False, {}

        # ── SUCCESS ───────────────────────────────────────────────────────────
        self.state[day, period, room]  = course_idx + 1
        self._placed[course_idx]      += 1
        reward = 100.0
        if self._placed[course_idx] == self._required[course_idx]:
            reward += 50.0

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

    def get_valid_actions(self, course_idx):
        """Return all currently valid action ints for a given course index."""
        valid    = []
        course   = self.df_subjects.iloc[course_idx]
        division = course["division"]
        is_hon   = bool(course["is_honours"])

        if self._placed[course_idx] >= self._required[course_idx]:
            return valid

        for d in range(DAYS):
            for p in range(PERIODS):
                # Honours: only Tue/Fri P5
                if is_hon:
                    if d not in HONOURS_DAYS or p != HONOURS_PERIOD:
                        continue
                else:
                    # Non-honours: skip the reserved Honours slot
                    if d in HONOURS_DAYS and p == HONOURS_PERIOD:
                        continue

                # Teacher busy at this (day, period)?
                if self._is_teacher_busy(course["teacher_code"], d, p):
                    continue

                for r in range(self.num_rooms):
                    rm = self.df_rooms.iloc[r]

                    # Room type match
                    if course["room_type_needed"] != rm["room_type"]:
                        continue

                    # Honours must use HONOURS_ROOM
                    if is_hon and r != HONOURS_ROOM:
                        continue

                    # Theory division stickiness
                    if not is_hon and course["room_type_needed"] == "Theory":
                        if division != "ALL":
                            if r != DIVISION_ROOM.get(division, -1):
                                continue

                    # Slot must be free
                    if self.state[d, p, r] != 0:
                        continue

                    slot   = d * (PERIODS * self.num_rooms) + p * self.num_rooms + r
                    action = course_idx * self.n_slots + slot
                    valid.append(action)

        return valid

    def render(self):
        pass