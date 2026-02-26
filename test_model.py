import numpy as np
from stable_baselines3 import DQN
from timetable_env import TimetableEnv

# 1. Load the Environment and the Trained Brain
env = TimetableEnv()
model = DQN.load("d3qn_timetable_model")

# 2. Let the AI solve one final timetable
obs, _ = env.reset()
for _ in range(10):
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated:
        break

# 3. Print the result in a nice grid
print("\n--- AI GENERATED TIMETABLE ---")
print("Rows = Slots (1-5), Columns = Rooms (101-103)")
# Reshape the flat observation back into our 5x3 grid
grid = obs.reshape((5, 3))
print(grid)
print("------------------------------")