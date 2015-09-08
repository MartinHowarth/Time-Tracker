import Tkinter
import task
import timeslot
import logging

logging.basicConfig(level=logging.DEBUG)


class Tracker(Tkinter.Frame):
    def __init__(self, tkinter_root):
        Tkinter.Frame.__init__(self, tkinter_root)
        self.grid(row=1, column=0)

        self.tasks = {}
        self.weeks = {}
        self.week_index_counter = 2

        self.add_task_button = Tkinter.Button(self,
                                              text="+Task",
                                              command=self.add_task)
        self.add_task_button.grid(row=0, column=0, sticky=Tkinter.W)

        self.add_week_button = Tkinter.Button(self,
                                              text="+Week",
                                              command=self.add_week)
        self.add_week_button.grid(row=0, column=1, sticky=Tkinter.W)

        tkinter_root.bind('<Return>', self.update_time_totals)

    def add_task(self, name=None):
        if name is None:
            window = Tkinter.Toplevel(self)
            window.wm_title("Enter task name")
            entry = Tkinter.Entry(window, width=20)
            entry.pack()

            def accept():
                new_task = task.Task(self, entry.get())
                self.tasks[new_task.task_id] = new_task
                window.destroy()

            Tkinter.Button(window, text="Accept", command=accept).pack()

        else:
            new_task = task.Task(self, name)
            self.tasks[new_task.task_id] = new_task

    def add_week(self):
        logging.debug("Adding week globally.")
        date = "test date"
        self.weeks[self.week_index_counter] = \
            timeslot.WeekLabel(self, self.week_index_counter, date)

        for _task in self.tasks.itervalues():
            _task.add_week(self.week_index_counter)

        self.week_index_counter += 1

    def update_time_totals(self, _):
        logging.debug("Updating time totals.")
        for task in self.tasks.itervalues():
            task.update_times()

        for week in self.weeks.itervalues():
            week.update_times(self.tasks)

    def __str__(self):
        return "top level frame"


if __name__ == "__main__":
    root = Tkinter.Tk()
    root.wm_title("Time Tracker")
    root.resizable()
    tracker = Tracker(root)

    to_draw = []

    tracker.add_task("Task 1")
    tracker.tasks[1].add_subtask("Sub task 1")
    # task1 = task.Task(tracker, "Task 1")
    # task2 = task.Task(tracker, "Task 2")
    # task3 = task.Task(tracker, "Task 3")
    # subtask1 = task.SubTask(task1, "Sub Task 1")

    root.mainloop()