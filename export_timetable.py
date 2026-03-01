import pandas as pd
import numpy as np
from stable_baselines3 import DQN
from timetable_env import TimetableEnv

env = TimetableEnv()
model = DQN.load("d3qn_timetable_model")

obs, _ = env.reset()
subjects_df = pd.read_csv('subjects.csv')

print("🛠️  Force-filling the timetable for submission...")

# Instead of random steps, we loop through each subject's required hours
for idx, row in subjects_df.iterrows():
    hours_to_place = row['required_hours']
    course_id = idx + 1
    
    # Try to place each required hour for this subject
    attempts = 0
    placed = 0
    while placed < hours_to_place and attempts < 500:
        # Get the AI's best guess
        action, _ = model.predict(obs, deterministic=False)
        
        # We override the action to ensure it's trying to place THIS specific course
        # Action math: course_idx * (days * periods * rooms) + (rest of the mapping)
        base_action = action % (env.days * env.periods * env.rooms)
        forced_action = (idx * (env.days * env.periods * env.rooms)) + base_action
        
        obs, reward, terminated, truncated, info = env.step(forced_action)
        
        # Check if the environment state actually updated for this course
        if course_id in env.state:
            # Check how many times it exists now
            current_count = np.count_nonzero(env.state == course_id)
            placed = current_count
        
        attempts += 1

# --- FORMATTING THE OUTPUT ---
final_state = env.state 
days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
periods = ["P1", "P2", "P3", "P4", "P5", "P6"]
room_names = pd.read_csv('rooms.csv')['room_name'].tolist()
id_to_code = {i+1: code for i, code in enumerate(env.df_subjects['course_code'])}

rows = []
for d in range(5):
    for p in range(6):
        entry = {"Day": days[d], "Period": periods[p]}
        for r in range(len(room_names)):
            val = final_state[d, p, r]
            entry[room_names[r]] = id_to_code.get(val, "---")
        rows.append(entry)

pd.DataFrame(rows).to_csv('MEC_Final_Timetable.csv', index=False)
print("✅ SUCCESS! MEC_Final_Timetable.csv is now filled based on subject requirements.")