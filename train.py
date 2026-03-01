from stable_baselines3 import DQN
from timetable_env import TimetableEnv

env = TimetableEnv()
# Enable Dueling DQN architecture
policy_kwargs = dict(net_arch=[256, 256])

model = DQN(
    "MlpPolicy", 
    env, 
    policy_kwargs=policy_kwargs, 
    verbose=1,
    learning_rate=1e-4, # Slower learning rate for stability
    exploration_fraction=0.7, # AI will try random things for 70% of training
    exploration_final_eps=0.02,
    buffer_size=100000
)

print("🚀 Training 150,000 steps for MEC Timetable...")
model.learn(total_timesteps=150000)
model.save("d3qn_timetable_model")
print("✅ Training Complete!")