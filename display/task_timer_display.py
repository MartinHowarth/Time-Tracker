import Tkinter
import logging
import time


class TaskTimer(Tkinter.Toplevel):
    """
    Window that contains a timer to actively track time against a task.
    """
    def __init__(self, parent, _task):
        """
        :param TrackerDisplay parent: Parent Tkinter object.
        :param task.Task _task: Task to actively track time for.
        """
        self.parent = parent
        self.task = _task
        self.last_unpause_time = 0
        self.total_time_tracked = 0
        self.paused = False

        Tkinter.Toplevel.__init__(self, parent)
        self.wm_title(str(_task))

        self.pause_timer_button = Tkinter.Button(self,
                                                 text="Pause",
                                                 command=self.pause_timer)

        self.start_timer_button = Tkinter.Button(self,
                                                 text="Start",
                                                 command=self.start_timer)

        self.rounded_timer_entry = Tkinter.Entry(self, width=5)

        self.timer_text = Tkinter.StringVar()
        self.timer_label = Tkinter.Label(self, textvariable=self.timer_text)

    def pause_timer(self):
        self.total_time_tracked += time.time() - self.last_unpause_time
        self.update_timer_label()

    def start_timer(self):
        self.last_unpause_time = time.time()

    def update_timer_label(self):
        """
        Updates the label that displays the current length that the timer has been running.
        """
        temp_total_time = self.total_time_tracked
        if not self.paused:
            temp_total_time += time.time() - self.last_unpause_time

        temp_total_time_str = time.strftime("%Hhr %Mmin", time.localtime(temp_total_time))
        self.timer_text.set(temp_total_time_str)
