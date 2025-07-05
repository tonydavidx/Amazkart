import datetime

new_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def last_run():
    try:
        with open("lastrun.txt", "r", encoding="utf-8") as f:
            last_run_data = f.readlines()

        last_run_data.insert(0, new_time + "\n")

        with open("lastrun.txt", "w", encoding="utf-8") as f:
            f.writelines(last_run_data)

        print(f"Last run time updated to {new_time}")
    except Exception as e:
        print(e)
