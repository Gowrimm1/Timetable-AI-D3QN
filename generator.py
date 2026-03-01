import random
import pandas as pd


def generate_all_timetables(all_subjects_df):

    # Ensure column names are lowercase (safety)
    all_subjects_df.columns = all_subjects_df.columns.str.strip().str.lower()

    days = ["MON", "TUE", "WED", "THU", "FRI"]
    periods = 6

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
            is_lab = str(row["is_lab"]).lower() == "yes"
            lab_cont = int(row["lab_hours"])
            teacher = row["teacher"]

            placed_hours = 0
            attempts = 0

            while placed_hours < total_hours and attempts < 300:
                attempts += 1
                day = random.choice(days)

                # THEORY SUBJECT
                if not is_lab:

                    # Max 2 theory classes per day
                    if timetable[day].count(subject) >= 2:
                        continue

                    period = random.randint(0, periods - 1)

                    if timetable[day][period] == "":

                        # Teacher clash check
                        if (
                            teacher in global_teacher_schedule
                            and (day, period) in global_teacher_schedule[teacher]
                        ):
                            continue

                        timetable[day][period] = subject
                        global_teacher_schedule.setdefault(
                            teacher, []
                        ).append((day, period))

                        placed_hours += 1

                # LAB SUBJECT
                else:

                    if lab_cont <= 0:
                        continue

                    start = random.randint(0, periods - lab_cont)

                    # Check continuous empty slots
                    if all(
                        timetable[day][start + i] == ""
                        for i in range(lab_cont)
                    ):

                        clash = False

                        for i in range(lab_cont):
                            if (
                                teacher in global_teacher_schedule
                                and (day, start + i)
                                in global_teacher_schedule[teacher]
                            ):
                                clash = True
                                break

                        if clash:
                            continue

                        # Place lab continuously
                        for i in range(lab_cont):
                            timetable[day][start + i] = subject + " (Lab)"
                            global_teacher_schedule.setdefault(
                                teacher, []
                            ).append((day, start + i))

                        placed_hours += lab_cont

        # Convert to DataFrame properly
        df = pd.DataFrame(timetable).T

        # Set day names
        df.index = days

        # Rename periods starting from 1
        df.columns = [f"Period {i+1}" for i in range(periods)]

        # Replace empty cells
        df.replace("", "-", inplace=True)

        all_timetables[str(semester)] = df

    return all_timetables