from dataclasses import dataclass, field
from datetime import time


@dataclass
class Task:
    title: str
    duration: int  # minutes
    start_time: time | None = None
    priority: int = 3  # 1 = highest, 5 = lowest

    def update_priority(self, priority: int) -> None:
        """Change this task's priority (1-5)."""
        pass

    def add_tasks(self) -> None:
        """Add a task."""
        pass

    def remove_task(self) -> None:
        """Remove a task."""
        pass


@dataclass
class Pet:
    name: str
    species: str
    needs: list[str] = field(default_factory=list)

    def retrieve_needs(self) -> list[str]:
        """Return this pet's needs."""
        pass

    def add_needs(self, need: str) -> None:
        """Add a need to this pet."""
        pass

    def remove_need(self, need: str) -> None:
        """Remove a need from this pet."""
        pass


@dataclass
class Owner:
    name: str
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, name: str, species: str) -> Pet:
        """Create a pet and add it to this owner's pets."""
        pass

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's pets."""
        pass


@dataclass
class Scheduler:
    daily_tasks: list[Task] = field(default_factory=list)
    available_times: list[time] = field(default_factory=list)

    def generate_schedule(self) -> list[Task]:
        """Build a daily schedule from tasks and available times."""
        pass

    def prioritize_tasks(self) -> list[Task]:
        """Rank tasks by priority (1 = highest, 5 = lowest)."""
        pass

    def reschedule_task(self, task: Task, new_time: time) -> None:
        """Move a task to a new start time."""
        pass
