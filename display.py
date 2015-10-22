import Tkinter
import logging
import time

ROW_OFFSET = 1
COLUMN_OFFSET = 2


def prompt_for_value(parent, function_to_call, title):
    def prompt():
        window = Tkinter.Toplevel(parent)
        window.wm_title(title)
        entry = Tkinter.Entry(window, width=20)
        entry.pack()
        entry.focus_set()

        def accept(_=None):
            logging.debug("New %s value: %s" % (title, entry.get()))
            function_to_call(entry.get())
            window.destroy()

        Tkinter.Button(window, text="Accept", command=accept).pack()
        window.bind('<Return>', accept)

    return prompt


class TrackerDisplay(Tkinter.Frame):
    def __init__(self, parent, _tracker):
        """
        :param Tkinter.Tk parent: Tkinter root.
        :return:
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
        self.task_displays[_task] = TaskDisplay(self, _task, task_index)

    def add_week_label(self, week_name, week_index):
        logging.debug("Adding week label at index %d, with name %s" % (week_index, week_name))
        self.week_labels.append(WeekLabel(self, week_name, week_index))

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
        self.archive_display = ArchiveDisplay(self)

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
        :return:
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
        :return:
        """
        # Gather the data entered in each entry and store it.
        for task_display in self.task_displays.itervalues():
            task_display.gather_input()

        # Trigger redrawing of entire UI
        self.tracker.update()


class TaskDisplay(Tkinter.Frame):
    def __init__(self, parent, _task, row_id):
        """

        :param TrackerDisplay parent: Tkinter Frame within which this frame resides.
        :param task.Task _task: Datastore that this class will draw.
        :return:
        """
        logging.debug("Creating display for task %s" % _task)

        self.task = _task

        if self.task.archived:
            logging.debug("Aborting display for task %s as it is archived." % _task)
            return

        self.parent = parent
        self.row_id = row_id
        Tkinter.Frame.__init__(self,
                               self.parent,
                               borderwidth=2,
                               relief=Tkinter.GROOVE)

        # Create a button with a variable text field so that we can update it later.
        # Click it to change the task name
        self._label_text = Tkinter.StringVar()
        self.label = Tkinter.Button(self,
                                    textvariable=self._label_text,
                                    command=prompt_for_value(self, self.set_name, "Enter new task name"))
        # Update the value displayed in the text field
        self.update_counter()

        # Create a button that prompts for a name, then creates a new subtask.
        self.add_new_subtask_button = Tkinter.Button(self,
                                                     text="+",
                                                     command=prompt_for_value(self.parent,
                                                                              self.add_subtask,
                                                                              "Enter subtask name"))

        self.archive_task_button = Tkinter.Button(self,
                                                  text="-",
                                                  command=self.archive_self)

        # Draw this task now so that the sub task labels go underneath the main label when added later
        self.draw()

        # Create a label for each subtask.
        self.subtask_labels = []
        for subtask in self.task.subtasks:
            self.add_subtask_label(subtask)

        # Create a set of entries (a week display) for each week this task exists for
        self.week_displays = []
        for _week in self.task.weeks:
            self.add_week(_week)

    def set_name(self, name):
        if self.parent.tracker.check_task_name_validity(name):
            self.task.task_name = name
            self.parent.update()
        else:
            logging.debug("Task name already exists, abandoning rename.")

    def add_subtask(self, name):
        """
        Intended to be called when the "new subtask" button is pressed.
        Creates a new subtask in the task.
        Also creates a label for the new subtask.
        :param str name: Subtask name.
        :return:
        """
        if self.task.check_subtask_name_validity(name):

            self.task.add_subtask(name)
            self.parent.update()

    def add_subtask_label(self, name):
        """
        Add a label to describe the subtask.
        :param str name: Subtask name
        :return:
        """
        self.subtask_labels.append(SubTaskLabel(self, name))

    def add_week(self, _week):
        self.week_displays.append(WeekDisplay(self.parent, _week, self.row_id, _week.index))

    def archive_self(self):
        self.task.archived = True
        self.parent.update()

    def draw(self):
        # Draw task details onto main grid in correct row based on defined task order.
        self.grid(row=self.row_id + ROW_OFFSET, sticky=Tkinter.W)
        # Draw task label in sub-grid that belongs to this task.
        self.label.grid(row=0, sticky=Tkinter.W)
        # Draw add subtask button next to label.
        self.add_new_subtask_button.grid(row=0, column=1, padx=20, sticky=Tkinter.W)
        # Draw archive button next to add subtask button
        self.archive_task_button.grid(row=0, column=1, sticky=Tkinter.E)

    def gather_input(self):
        if not self.task.archived:
            logging.debug("Gathering input from entries.")
            for week_display in self.week_displays:
                week_display.update_values()
        if self.task.archive_after_update:
            self.task.archived = False
            self.task.archive_after_update = False

    def update_counter(self):
        self._update_to_value(self.task.get_total_time())

    def _update_to_value(self, value):
        """
        Update the label to keep the same name, but with a new value.
        :param float value: Value to display.
        :return:
        """
        self._label_text.set("%s: %d" % (self.task.task_name, value))


class SubTaskLabel(Tkinter.Button):
    def __init__(self, parent_task_display, name):
        """
        :param TaskDisplay parent_task_display: Task display object that owns this subtask
        :param str name: subtask name
        :return:
        """
        self.parent = parent_task_display
        self.name = name

        # Create the label with a variable text field so we can change it later.
        self.text = Tkinter.StringVar()
        Tkinter.Button.__init__(self,
                                parent_task_display,
                                textvariable=self.text,
                                command=prompt_for_value(self, self.set_name, "Enter new subtask name"))

        # Initialise label with default value.
        self.update_counter()

        self.grid(sticky=Tkinter.W)

    def set_name(self, name):
        """
        Change the name of this subtask.
        :param str name: New name for this subtask.
        :return:
        """
        self.parent.task.rename_subtask(self.name, name)
        self.parent.parent.update()

    def update_counter(self):
        """
        Update the summation of time tracked against this task.
        :return:
        """
        logging.debug("Updating counter for subtask %s" % self.name)
        self._update_to_value(self.parent.task.get_time_for_subtask(self.name))

    def _update_to_value(self, value):
        """
        Update the label to keep the same name, but with a new value.
        :param float value: Value to display.
        :return:
        """
        self.text.set(self.name + ": " + str(value))


class WeekDisplay(Tkinter.Frame):
    def __init__(self, parent, _week, row_index, column_index):
        """
        Displays a single task/week grid space.
        Has an entry per subtask (and one for the general task).
        :param TrackerDisplay parent: Tkinter Frame within which this frame resides.
        :param weekslot.WeekSlot _week: Datastore that this class will draw.
        :return:
        """
        logging.debug("Creating display for week %s" % str(_week))

        self.parent = parent
        Tkinter.Frame.__init__(self,
                               self.parent)

        self.row_index = row_index
        self.column_index = column_index

        self.week = _week
        self.entries = []

        # Add a subtask text entry box for each value in the week.
        for time in self.week.time_tracked:
            self.add_subtask(time)

        # Only display if this week is not archived.
        if self.column_index >= self.parent.tracker.archived_week_index:
            self.draw()
        else:
            logging.debug("Not displaying week slot in column %d because it is archived." % self.column_index)

    def add_subtask(self, init_time):
        """
        Creates a new entry field for the new subtask.
        :param float init_time: Initial time for the entry to be filled with.
        :return:
        """
        new_entry = Tkinter.Entry(self, width=5)
        if init_time != 0:
            # insert the supplied value into the entry. Leave blank if value is 0
            new_entry.insert(0, str(init_time))
        self.entries.append(new_entry)

    def draw(self):
        """
        Draws this week display object in the correct grid slot of the TrackerDisplay object.
        Also draws the entries for each subtask within this week object.
        :return:
        """
        self.grid(row=self.row_index + ROW_OFFSET,
                  column=self.column_index + COLUMN_OFFSET,
                  sticky=Tkinter.N)

        for index, entry in enumerate(self.entries):
            entry.grid(row=index)

    def update_values(self):
        """
        Gather the values from the displayed entries and put into the week object.
        :return:
        """
        logging.debug("Updating values for week slot in row %d, column %d" % (self.row_index, self.column_index))
        values = []
        for entry in self.entries:
            # Try convert the string value stored in the entry to a float. If this fails, assume it is 0.
            # Specifically this covers the case where the field is an empty string which signifies 0.
            try:
                float_value = float(entry.get())
            except ValueError:
                float_value = 0.0
            values.append(float_value)
        self.week.update_values(values)


class WeekLabel(Tkinter.Label):
    def __init__(self, parent, date_string, column_index):
        """

        :param TrackerDisplay parent: Tkinter Frame within which this frame resides.
        :param str date_string: Date in string format
        :param int column_index: Grid index to draw this label.
        :return:
        """
        logging.debug("Creating Label for week %s" % str(date_string))

        # Create the label with a variable text field so we can change it later.
        self.text = Tkinter.StringVar()
        Tkinter.Label.__init__(self, parent, textvariable=self.text)

        self.date_string = date_string
        self.column_index = column_index

        # Only display if this week is not archived.
        if self.column_index >= parent.tracker.archived_week_index:
            self.draw()
        else:
            logging.debug("Not displaying week label in column %d because it is archived." % self.column_index)

    def update_to_value(self, value):
        """
        Update the label to keep the same name, but with a new value.
        :param float value: Value to display.
        :return:
        """
        logging.debug("Updating week label %s to value %d" % (self.date_string, value))
        self.text.set("%s\n%d" % (self.date_string, value))

    def draw(self):
        """
        Draws this week label in the first row of the correct column of the TrackerDisplay grid.
        :return:
        """
        self.grid(row=0, column=self.column_index + COLUMN_OFFSET)


class ArchiveDisplay(Tkinter.Toplevel):
    def __init__(self, parent):
        """
        :param TrackerDisplay parent:
        """
        Tkinter.Toplevel.__init__(self, parent)
        self.wm_title("Click tasks to restore them")

        self.parent = parent

        self.hide_self_button = Tkinter.Button(self,
                                               text="Close",
                                               command=self.parent.hide_archive)

        self.description_label = Tkinter.Label(self, text="Click tasks to restore them.")

        self.archived_task_list = self.parent.tracker.get_archived_task_list()

        self.restore_task_buttons = {}

        for _task in self.archived_task_list:
            self.restore_task_buttons[_task] = Tkinter.Button(self,
                                                              text=str(_task),
                                                              command=self.unarchive_task(_task))

        self.draw()

    def unarchive_task(self, _task):
        """
        Trigger this task to become unarchived on the next update of the display.
        :param task.Task _task: Task to un-archive.
        """
        def do_the_work():
            # Set just unarchived so that we don't try and read the entry values from this task before we redraw.
            _task.archive_after_update = True
            self.restore_task_buttons[_task].destroy()
            self.parent.update()
        return do_the_work

    def draw(self):
        self.description_label.pack()
        for button in self.restore_task_buttons.itervalues():
            button.pack()
        self.hide_self_button.pack()


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


