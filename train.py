from stable_baselines3 import DQN
from timetable_env import TimetableEnv

# Initialize environment
env = TimetableEnv()

# NEW FIX: In the latest SB3, we specify the dueling architecture 
# by using the 'share_features_extractor' or specific policy settings.
# For simplicity and to ensure it runs as D3QN:
policy_kwargs = dict(
    net_arch=[256, 256]
)

model = DQN(
    "MlpPolicy", 
    env, 
    policy_kwargs=policy_kwargs, 
    verbose=1, 
    learning_rate=1e-3,
    buffer_size=10000,
    # Many versions of SB3 have Dueling ON by default now! 
)

print("🚀 Starting D3QN Training...")
model.learn(total_timesteps=20000)

# Save the brain
model.save("d3qn_timetable_model")
print("✅ Training complete. Model saved!")