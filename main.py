import csv
import json
import tkinter as tk
from datetime import datetime, date, time
from tkinter import messagebox


class WorkTimeSaverApp:
    def __init__(self, root, times_file_path, total_time_file_path):
        self.root = root
        self.root.title("Work Time Saver")

        # Create and place labels and entry widgets
        tk.Label(root, text="Start Time (00:00)").grid(row=0)
        tk.Label(root, text="End Time (00:00)").grid(row=1)
        tk.Label(root, text="Title").grid(row=2)
        tk.Label(root, text="Description").grid(row=3)

        self.entry_start_time = tk.Entry(root)
        self.entry_end_time = tk.Entry(root)
        self.entry_title = tk.Entry(root)
        self.entry_description = tk.Entry(root)

        self.entry_description.config(justify='right')

        self.entry_start_time.grid(row=0, column=1)
        self.entry_end_time.grid(row=1, column=1)
        self.entry_title.grid(row=2, column=1)
        self.entry_description.grid(row=3, column=1)

        # Create and place the print button
        button_submit = tk.Button(root, text="submit", command=self.save_data)
        button_submit.grid(row=4, column=1)
        start_time_now_button = tk.Button(root, text="now", command="")
        start_time_now_button.grid(row=0, column=2)
        end_time_now_button = tk.Button(root, text="now", command="")
        end_time_now_button.grid(row=1, column=2)

        start_time_now_button = tk.Button(root, text="now", command=self.set_start_time_now)
        start_time_now_button.grid(row=0, column=2)

        end_time_now_button = tk.Button(root, text="now", command=self.set_end_time_now)
        end_time_now_button.grid(row=1, column=2)

        button_calculate = tk.Button(root, text="calculate", command=self.calculate_data, bg='#111111', fg='#ffffff')
        button_calculate.grid(row=5, column=1)

        self.times_file_path = times_file_path
        self.total_time_file_path = total_time_file_path

        self.prefill_fields()

    def prefill_fields(self):
        with open(self.times_file_path, 'r', encoding='utf-8', newline='') as file:
            reader = csv.reader(file)
            rows = list(reader)

            if rows:
                last_row = rows[-1]
                if last_row[2] == 'null':
                    self.entry_start_time.insert(0, last_row[1])
                    self.entry_title.insert(0, last_row[0])
                    self.entry_end_time.insert(0, "")
                    self.entry_description.insert(0, last_row[3])

    def set_start_time_now(self):
        current_time = datetime.now().strftime("%H:%M")
        self.entry_start_time.delete(0, tk.END)  # Clear the entry first
        self.entry_start_time.insert(0, current_time)  # Insert the current time

    def set_end_time_now(self):
        current_time = datetime.now().strftime("%H:%M")
        self.entry_end_time.delete(0, tk.END)  # Clear the entry first
        self.entry_end_time.insert(0, current_time)  # Insert the current time

    def get_data(self):
        start_time = self.entry_start_time.get()
        end_time = self.entry_end_time.get()
        title = self.entry_title.get()
        description = self.entry_description.get()

        start_time = start_time if start_time != "" else None
        end_time = end_time if end_time != "" else None
        title = title if title != "" else None
        description = description if description != "" else None

        if not start_time or not title or not description:
            messagebox.showinfo("Error",
                                f"enter {'start_time' if not start_time else 'title' if not title else 'description'}")

        return start_time, end_time, title, description

    def save_data(self):
        start_time, end_time, title, description = self.get_data()

        if not start_time or not title or not description:
            return

        data = [title, start_time, end_time if end_time else 'null', description]

        with open(self.times_file_path, 'r', encoding='utf-8', newline='') as file:
            reader = csv.reader(file)
            rows = list(reader)

            if rows and rows[-1][2] == 'null':
                # Replace the last row with the new data
                rows[-1] = data
            else:
                # Append the new data as a new row
                rows.append(data)

        with open(self.times_file_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        # Close window
        self.root.destroy()

    def calculate_data(self):
        with open(self.times_file_path, 'r', encoding='utf-8', newline='') as file:
            reader = csv.reader(file)
            rows = list(reader)

            if rows and rows[-1][2] == 'null':
                messagebox.showinfo("Error", "there is a null value")

            times = {}

            for row in rows:
                start_time = row[1]
                end_time = row[2]

                datetime_start_time = datetime.combine(date.today(), time.fromisoformat(start_time))	
                datetime_end_time = datetime.combine(date.today(), time.fromisoformat(end_time))

                time_taken = datetime_end_time - datetime_start_time

                time_taken = time_taken.total_seconds() / 60

                if times.get(row[0]):
                    times[row[0]]['total_time'] += time_taken
                    if row[3] not in times[row[0]]['description']:
                        times[row[0]]['description'].append(row[3])
                else:

                    times[row[0]] = {'total_time': time_taken, 'description': [row[3]]}

        for title in times.values():
            title['description'] = ', '.join(title['description'])

        with open(self.total_time_file_path, 'w') as final:
            json.dump(times, final, ensure_ascii=False)

        self.clear_data()

        self.show_results()

    def clear_data(self):
        with open(self.times_file_path, 'w', encoding='utf-8', newline='') as file:
            # Opening in 'w' mode truncates the file, so no need to write anything
            pass

    def show_results(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title("Calculation Results")
        self.root.geometry("400x300")

        text_results = tk.Text(self.root, height=20, width=50)
        text_results.pack()

        with open(self.total_time_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

            for task, info in data.items():
                text_results.insert(tk.END, f"Task: {task}\n")
                text_results.insert(tk.END, f"Total Time: {info['total_time']} minutes\n")
                text_results.insert(tk.END, f"Description: {info['description']}\n\n")


# Set up the main window
root = tk.Tk()
app = WorkTimeSaverApp(root, 'times.csv', 'total_time.json')

# Run the Tkinter event loop
root.mainloop()
