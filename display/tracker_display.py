import Tkinter
import logging
from misc_display_functions import prompt_for_value
import task_display
import week_display
import archive_display


class TrackerDisplay(Tkinter.Frame):
    def __init__(self, parent, _tracker):
        """
        :param Tkinter.Tk parent: Tkinter root.
        """
        self.tracker = _tracker

        self.parent = parent
        Tkinter.Frame.__init__(self, self.parent)

        # Create a frame that will house all of the buttons so that they fit nicely into one grid slot.
        self.button_frame = Tkinter.Frame(self)

        self.add_task_button = Tkinter.Button(self.button_frame,
                                              text="+Task",
                                              command=prompt_for_value(self,
                                                                       self.add_task,
                                                                       "Enter task name"))

        self.add_week_button = Tkinter.Button(self.button_frame,
                                              text="+Week",
                                              command=self.add_week)

        self.increment_week_archive_button = Tkinter.Button(self.button_frame,
                                                            text=">",
                                                            command=self.increment_week_archive)
        self.decrement_week_archive_button = Tkinter.Button(self.button_frame,
                                                            text="<",
                                                            command=self.decrement_week_archive)

        self.archive_button = Tkinter.Button(self.button_frame,
                                             text="Archive",
                                             command=self.show_archive)

        self.save_button = Tkinter.Button(self.button_frame,
                                          text="Save",
                                          command=self._save)

        self.load_button = Tkinter.Button(self.button_frame,
                                          text="Load",
                                          command=self._load)

        self.archive_display = None

        self.parent.bind('<Return>', self.update)

        self.task_displays = {}
        self.week_labels = []

        for task_name in self.tracker.task_order:
            self.add_task_display(task_name)

        for week_index in range(self.tracker.week_index):
            self.add_week_label(self.tracker.get_week_name(week_index), week_index)

        for week_index, week_label in enumerate(self.week_labels):
            counter = 0
            for _task_display in self.task_displays.itervalues():
                counter += _task_display.task.get_time_for_week(week_index)

            week_label.update_to_value(counter)

        self.draw()

    def add_task(self, name):
        logging.debug("Add task button pressed with name: %s" % name)
        self.tracker.create_new_task(name)
        self.update()

    def add_week(self):
        logging.debug("Add week button pressed.")
        self.tracker.add_week()
        self.update()

    def add_task_display(self, task_name):
        logging.debug("Adding task display with name %s" % task_name)
        _task, task_index = self.tracker.get_task_and_index(task_name)
        self.task_displays[_task] = task_display.TaskDisplay(self, _task, task_index)

    def add_week_label(self, week_name, week_index):
        logging.debug("Adding week label at index %d, with name %s" % (week_index, week_name))
        self.week_labels.append(week_display.WeekLabel(self, week_name, week_index))

    def add_week_slot(self, _task, week):
        logging.debug("Adding week slot to task %s for week %s" % (_task, week))
        self.task_displays[_task].add_week(week)

    def increment_week_archive(self):
        """
        Shows one less week.
        :return:
        """
        self.tracker.archived_week_index += 1
        self.update()

    def decrement_week_archive(self):
        """
        Shows one more week.
        :return:
        """
        self.tracker.archived_week_index -= 1
        self.update()

    def show_archive(self):
        """
        Displays a new window with a list of archived tasks. Allows user to un-archive tasks.
        """
        self.archive_display = archive_display.ArchiveDisplay(self)

    def hide_archive(self):
        """
        Hides the archive window. Opposite of self.show_archive
        """
        self.archive_display.destroy()

    def _save(self):
        """
        Called when the save button is pressed. Triggers Tracker object to save.
        """
        self.tracker.save()

    def _load(self):
        """
        Called when the load button is pressed. Triggers Tracker object to load.
        """
        self.tracker.load()
        self.tracker.update()

    def draw(self):
        """
        Draws this TrackerDisplay onto the Tkinter root.
        Also draws all of the management buttons in the 0,0 grid slot of this object.
        """
        self.grid(row=0, column=0)

        self.save_button.pack(side=Tkinter.LEFT)
        self.load_button.pack(side=Tkinter.LEFT)
        self.archive_button.pack(side=Tkinter.LEFT)
        self.add_task_button.pack(side=Tkinter.LEFT, padx=10)
        self.add_week_button.pack(side=Tkinter.RIGHT, padx=10)
        self.increment_week_archive_button.pack(side=Tkinter.RIGHT)
        self.decrement_week_archive_button.pack(side=Tkinter.RIGHT)

        self.button_frame.grid(row=0, column=0, sticky=Tkinter.W)

    def update(self, _=None):
        """
        Trigger re-draw of the entire UI.
        Also gathers the input in all of the entries and stores it.
        :param _: Dummy parameter. Tkinter passes in the event object that we don't care about.
        """
        # Gather the data entered in each entry and store it.
        for _task_display in self.task_displays.itervalues():
            _task_display.gather_input()

        # Trigger redrawing of entire UI
        self.tracker.update()

