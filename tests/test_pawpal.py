from pawpal_system import Pet, Task


def test_mark_complete_changes_task_status():
    task = Task(title="Morning walk", duration=30)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Rex", species="dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task(title="Feeding", duration=15))

    assert len(pet.tasks) == 1
