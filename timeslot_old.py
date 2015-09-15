import Tkinter
import logging


class WeekLabel(Tkinter.Label):
    """
    Label for a week. Includes sum of time spent that week.
    Highlights red if count is not equal to 5.
    """
    def __init__(self, top_level_frame, column, date):
        self.parent = top_level_frame
        self.date = date

        self.text = Tkinter.StringVar()
        Tkinter.Label.__init__(self, top_level_frame, textvariable=self.text)
        self.update_to_value(0)

        self.grid(row=0, column=column)
        self.column = column

        self.weekly_sum = 0

    def update_times(self, task_dict):
        total = 0
        for task in task_dict.itervalues():
            total += task.get_value_in_week(self.column)

        self.update_to_value(total)

    def update_to_value(self, value):
        self.text.set(self.date + "\n" + str(value))


class TaskTime(Tkinter.Frame):
    """
    A set of entries for time spent on a particular task in one week.
    """
    def __init__(self, top_level_frame, row, column):
        logging.debug("Adding time frame to coordinate %d,%d" % (row, column))
        Tkinter.Frame.__init__(self, top_level_frame)
        self.parent = top_level_frame
        self.grid(row=row, column=column, sticky=Tkinter.N)

        self.subtask_times = {}
        self.subtask_times_counter = 0

        # Add one subtask time to track generic task time
        #   (i.e. not associated with any sub task)
        self.add_subtask_time()

    def add_subtask_time(self):
        row = self.subtask_times_counter
        self.subtask_times[row] = SubTaskTime(self, row)
        self.subtask_times_counter += 1

    def remove_subtask_time(self, row):
        self.subtask_times[row].destroy()

    def get_task_time_total(self):
        count = 0
        for row, sub_task_time in self.subtask_times.iteritems():
            count += sub_task_time.get_task_time()

        return count


class SubTaskTime(Tkinter.Entry):
    def __init__(self, task_time_frame, row):
        Tkinter.Entry.__init__(self, task_time_frame, width=5)
        self.parent = task_time_frame

        self.grid(row=row, pady=2)

    def get_task_time(self):

        try:
            return float(self.get())
        except:
            return 0