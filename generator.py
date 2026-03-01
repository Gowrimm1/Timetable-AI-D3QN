import random
import pandas as pd

def generate_all_timetables(all_subjects_df):

    days = ["MON", "TUE", "WED", "THU", "FRI"]
    periods = 6

    # MATCH YOUR CSV COLUMN NAMES
    semesters = all_subjects_df["semester"].unique()

    global_teacher_schedule = {}
    all_timetables = {}

    for semester in semesters:

        subjects_df = all_subjects_df[
            all_subjects_df["semester"] == semester
        ]

        timetable = {day: [""] * periods for day in days}

        for _, row in subjects_df.iterrows():

            subject = row["subject"]
            total_hours = int(row["weekly_hours"])
            is_lab = row["is_lab"] == "Yes"
            lab_cont = int(row["lab_hours"])
            teacher = row["teacher"]

            placed_hours = 0
            attempts = 0

            while placed_hours < total_hours and attempts < 300:
                attempts += 1
                day = random.choice(days)

                if not is_lab and timetable[day].count(subject) >= 2:
                    continue

                if is_lab and lab_cont > 0:

                    start = random.randint(0, periods - lab_cont)

                    if all(timetable[day][start+i] == "" for i in range(lab_cont)):

                        clash = False

                        for i in range(lab_cont):
                            if teacher in global_teacher_schedule and \
                               (day, start+i) in global_teacher_schedule[teacher]:
                                clash = True
                                break

                        if clash:
                            continue

                        for i in range(lab_cont):
                            timetable[day][start+i] = subject + " (Lab)"
                            global_teacher_schedule.setdefault(teacher, []).append((day, start+i))

                        placed_hours += lab_cont

                else:
                    period = random.randint(0, periods - 1)

                    if timetable[day][period] == "":

                        if teacher in global_teacher_schedule and \
                           (day, period) in global_teacher_schedule[teacher]:
                            continue

                        timetable[day][period] = subject
                        global_teacher_schedule.setdefault(teacher, []).append((day, period))

                        placed_hours += 1

        all_timetables[semester] = pd.DataFrame(timetable).T

    return all_timetables