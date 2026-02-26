import pandas as pd

# 1. Create Subjects (Course Code, Name, Weekly Hours)
subjects = pd.DataFrame({
    'course_id': range(1, 11),
    'course_name': ['DBMS', 'DAA', 'OS', 'CN', 'Maths', 'AI', 'Java', 'Python', 'Graphics', 'Economics']
})
subjects.to_csv('subjects.csv', index=False)

# 2. Create Rooms
rooms = pd.DataFrame({
    'room_id': [101, 102, 103],
    'room_type': ['Theory', 'Theory', 'Lab']
})
rooms.to_csv('rooms.csv', index=False)

print("✅ CSV Files Created: subjects.csv, rooms.csv")