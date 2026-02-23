print("TEST RUNNING")

from timetable_env import TimetableEnv

env = TimetableEnv()

state, _ = env.reset()
print("Initial state:")
print(state)

#clash experiment
state, reward, done, _, _ = env.step([1,1,1])
print("\nAfter first action:")
print(state)
print("Reward:", reward)

state, reward, done, _, _ = env.step([2,1,1])
print("\nAfter second action (same slot):")
print(state)
print("Reward:", reward)