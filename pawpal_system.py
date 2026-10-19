from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, time, timedelta
from uuid import uuid4

# Frequency -> days until the next occurrence (None = one-off)
RECURRENCE_DAYS = {None: None, "daily": 1, "weekly": 7}


@dataclass
class Task:
    title: str
    duration: int  # minutes
    start_time: time | None = None
    priority: int = 3  # 1 = highest, 5 = lowest
    task_date: date = field(default_factory=date.today)
    recurrence: str | None = None  # frequency: None, "daily" or "weekly"
    description: str = ""
    completed: bool = False

    def __post_init__(self) -> None:
        """Validate duration, recurrence and priority when the task is created."""
        if self.duration <= 0:
            raise ValueError("duration must be a positive number of minutes")
        if self.recurrence not in RECURRENCE_DAYS:
            raise ValueError(f"recurrence must be one of {list(RECURRENCE_DAYS)}")
        self._validate_priority(self.priority)

    @staticmethod
    def _validate_priority(priority: int) -> None:
        """Raise ValueError unless priority is between 1 and 5."""
        if not 1 <= priority <= 5:
            raise ValueError("priority must be between 1 (highest) and 5 (lowest)")

    @property
    def start_sort_key(self) -> tuple[bool, time]:
        """Sort key that places unscheduled tasks (start_time None) after scheduled ones."""
        return (self.start_time is None, self.start_time or time.min)

    def update_priority(self, priority: int) -> None:
        """Change this task's priority (1-5)."""
        self._validate_priority(priority)
        self.priority = priority

    def occurs_on(self, day: date) -> bool:
        """True if this task falls on `day`, counting daily/weekly repeats after task_date."""
        if day < self.task_date:
            return False
        days = RECURRENCE_DAYS[self.recurrence]
        if days is None:
            return day == self.task_date
        return (day - self.task_date).days % days == 0

    def mark_complete(self) -> "Task | None":
        """Mark this task done. For a recurring task, return the next occurrence (else None)."""
        self.completed = True
        return self.next_occurrence()

    def next_occurrence(self) -> "Task | None":
        """Return a fresh, incomplete copy dated for the next recurrence, or None if one-off."""
        days = RECURRENCE_DAYS[self.recurrence]
        if days is None:
            return None
        return replace(
            self, task_date=self.task_date + timedelta(days=days), completed=False
        )

    def __str__(self) -> str:
        """Return a one-line summary of the task."""
        when = self.start_time.strftime("%H:%M") if self.start_time else "unscheduled"
        status = "done" if self.completed else "pending"
        return f"{self.title} ({self.duration} min, {when}, priority {self.priority}, {status})"


@dataclass
class Pet:
    name: str
    species: str
    needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    pet_id: str = field(default_factory=lambda: uuid4().hex)  # unique even if names collide

    def retrieve_needs(self) -> list[str]:
        """Return a copy of this pet's needs."""
        return list(self.needs)

    def add_needs(self, need: str) -> None:
        """Add a need to this pet (ignored if already present)."""
        need = need.strip().lower()
        if need and need not in self.needs:
            self.needs.append(need)

    def remove_need(self, need: str) -> None:
        """Remove a need from this pet; raises ValueError if it isn't listed."""
        self.needs.remove(need.strip().lower())

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's tasks (ignored if that exact task is already added)."""
        if not any(existing is task for existing in self.tasks):
            self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's tasks; raises ValueError if it isn't listed."""
        for index, existing in enumerate(self.tasks):
            if existing is task:
                del self.tasks[index]
                return
        raise ValueError(f"{task.title!r} is not one of {self.name}'s tasks")

    def pending_tasks(self) -> list[Task]:
        """Return this pet's tasks that are not yet completed."""
        return [task for task in self.tasks if not task.completed]

    def __str__(self) -> str:
        """Return a one-line summary of the pet and its pending tasks."""
        return f"{self.name} ({self.species}) - {len(self.pending_tasks())} pending task(s)"


@dataclass
class Owner:
    name: str
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pets (ignored if that pet is already added)."""
        if not any(existing.pet_id == pet.pet_id for existing in self.pets):
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's pets; raises ValueError if it isn't listed."""
        for index, existing in enumerate(self.pets):
            if existing.pet_id == pet.pet_id:
                del self.pets[index]
                return
        raise ValueError(f"{pet.name} is not one of {self.name}'s pets")

    def get_all_tasks(self) -> list[Task]:
        """Return every task from every pet, combined into one list."""
        return [task for pet in self.pets for task in pet.tasks]


def _minutes(t: time) -> int:
    """Minutes since midnight."""
    return t.hour * 60 + t.minute


def _to_time(minutes: int) -> time:
    return time(minutes // 60, minutes % 60)


@dataclass
class Scheduler:
    """The "brain": reads every pet's tasks through the Owner and plans one day."""

    owner: Owner
    available_times: list[tuple[time, time]] = field(default_factory=list)  # (start, end) windows
    schedule_date: date = field(default_factory=date.today)
    scheduled_tasks: list[Task] = field(default_factory=list)  # tasks placed by the last run
    unscheduled_tasks: list[Task] = field(default_factory=list)  # tasks that did not fit

    @property
    def daily_tasks(self) -> list[Task]:
        """Pending tasks across ALL of the owner's pets that occur on schedule_date."""
        return [
            task
            for task in self.owner.get_all_tasks()
            if not task.completed and task.occurs_on(self.schedule_date)
        ]

    def prioritize_tasks(self) -> list[Task]:
        """Return a new list of daily tasks ranked by priority (1 = highest, 5 = lowest)."""
        return sorted(self.daily_tasks, key=lambda task: (task.priority, task.start_sort_key))

    def generate_schedule(self) -> list[Task]:
        """Place ranked tasks from all pets into the windows without overlaps; leftovers are tracked."""
        self.scheduled_tasks = []
        self.unscheduled_tasks = []
        for task in self.prioritize_tasks():
            start = self._find_slot(task, self.scheduled_tasks)
            if start is None:
                self.unscheduled_tasks.append(task)
            else:
                task.start_time = start
                self.scheduled_tasks.append(task)
        self.scheduled_tasks.sort(key=lambda task: task.start_sort_key)
        return list(self.scheduled_tasks)

    def reschedule_task(self, task: Task, new_time: time) -> bool:
        """Move a task to new_time if it fits a window without overlap; return whether it moved."""
        others = [other for other in self.scheduled_tasks if other is not task]
        start = _minutes(new_time)
        if not self._fits(start, task.duration, others):
            return False
        task.start_time = new_time
        if task in self.unscheduled_tasks:
            self.unscheduled_tasks.remove(task)
        if not any(task is placed for placed in self.scheduled_tasks):
            self.scheduled_tasks.append(task)
        self.scheduled_tasks.sort(key=lambda t: t.start_sort_key)
        return True

    def explain_schedule(self) -> str:
        """Return a plain-language summary of the plan and anything left out."""
        lines = [f"Plan for {self.owner.name} on {self.schedule_date}:"]
        for task in self.scheduled_tasks:
            lines.append(f"  {task}")
        if not self.scheduled_tasks:
            lines.append("  (nothing scheduled)")
        for task in self.unscheduled_tasks:
            lines.append(f"  Could not fit: {task.title} ({task.duration} min, priority {task.priority})")
        return "\n".join(lines)

    # -- helpers ---------------------------------------------------------------------------

    def _windows(self) -> list[tuple[int, int]]:
        """Return the available windows as sorted (start, end) minutes since midnight."""
        return sorted((_minutes(start), _minutes(end)) for start, end in self.available_times)

    @staticmethod
    def _busy(placed: list[Task]) -> list[tuple[int, int]]:
        """Return the sorted (start, end) minutes already taken by placed tasks."""
        return sorted(
            (_minutes(t.start_time), _minutes(t.start_time) + t.duration)
            for t in placed
            if t.start_time is not None
        )

    def _fits(self, start: int, duration: int, placed: list[Task]) -> bool:
        """True if [start, start+duration) is inside one window and clear of placed tasks."""
        end = start + duration
        if not any(w_start <= start and end <= w_end for w_start, w_end in self._windows()):
            return False
        return all(end <= b_start or start >= b_end for b_start, b_end in self._busy(placed))

    def _find_slot(self, task: Task, placed: list[Task]) -> time | None:
        """Preferred start_time if it fits, else the earliest free slot, else None."""
        if task.start_time is not None and self._fits(_minutes(task.start_time), task.duration, placed):
            return task.start_time
        busy = self._busy(placed)
        for w_start, w_end in self._windows():
            cursor = w_start
            for b_start, b_end in busy:
                if b_end <= cursor:
                    continue
                if b_start - cursor >= task.duration:
                    break
                cursor = max(cursor, b_end)
            if cursor + task.duration <= w_end:
                return _to_time(cursor)
        return None
