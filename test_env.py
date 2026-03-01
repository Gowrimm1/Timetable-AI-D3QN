"""
test_env.py — Quick sanity check for TimetableEnv
"""

print("🔍 TEST: TimetableEnv")

from timetable_env import TimetableEnv

env = TimetableEnv()
state, _ = env.reset()

print(f"  Action space size : {env.action_space.n}")
print(f"  Observation shape : {env.observation_space.shape}")
print(f"  Number of subjects: {env.num_courses}")
print(f"  Number of rooms   : {env.num_rooms}")
print(f"  Initial state sum : {state.sum()} (should be 0)\n")

# ── Test 1: valid placement ───────────────────────────────────────────────────
# Subject 0 (CST302/CS6A, Theory) → Day=0, Period=0, Room=0 (B202, Theory, CS6A)
n_slots  = env.days if hasattr(env, 'days') else 5
DAYS, PERIODS, ROOMS = 5, 6, env.num_rooms

action_valid = 0 * (DAYS * PERIODS * ROOMS) + 0 * (PERIODS * ROOMS) + 0 * ROOMS + 0
state, reward, done, _, _ = env.step(action_valid)
print(f"Test 1 – Valid placement  | reward={reward:.1f} | placed={int((state>0).sum())} slot(s)")
assert reward > 0, "Expected positive reward for valid placement!"

# ── Test 2: clash — same slot ─────────────────────────────────────────────────
state, reward, done, _, _ = env.step(action_valid)
print(f"Test 2 – Clash (same slot)| reward={reward:.1f}")
assert reward < 0, "Expected negative reward for slot clash!"

# ── Test 3: wrong room type ───────────────────────────────────────────────────
# Subject 0 is Theory; room index 6 is Network_Lab_1 → mismatch
action_wrong_room = 0 * (DAYS * PERIODS * ROOMS) + 0 * (PERIODS * ROOMS) + 1 * ROOMS + 6
state, reward, done, _, _ = env.step(action_wrong_room)
print(f"Test 3 – Wrong room type  | reward={reward:.1f}")
assert reward < 0, "Expected negative reward for room type mismatch!"

print("\n✅ All basic tests passed.")