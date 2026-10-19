from datetime import time

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(name="Jerome", preferences=["walks before dinner"])

    rex = Pet(name="Rex", species="dog")
    tom = Pet(name="Tom", species="cat")
    owner.add_pet(rex)
    owner.add_pet(tom)

    rex.add_task(Task("Morning walk", duration=30, priority=2))
    rex.add_task(Task("Medication", duration=10, start_time=time(8, 0), priority=1, recurrence="daily"))
    tom.add_task(Task("Feeding", duration=15, priority=1))
    tom.add_task(Task("Grooming", duration=60, priority=5))

    scheduler = Scheduler(
        owner=owner,
        available_times=[(time(8, 0), time(9, 0)), (time(18, 0), time(18, 45))],
    )
    scheduler.generate_schedule()

    print(scheduler.explain_schedule())


if __name__ == "__main__":
    main()
