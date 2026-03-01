from timetable_env import TimetableEnv

env = TimetableEnv()

state = env.reset()
print("Initial State:", state)

action = env.action_space.sample()
print("Sample Action:", action)

next_state, reward, terminated, truncated, info = env.step(action)

done = terminated or truncated

print("Next State:", next_state)
print("Reward:", reward)
print("Done:", done)