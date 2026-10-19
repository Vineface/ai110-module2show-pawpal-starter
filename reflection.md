# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
it should include a core action that adds pet tasks, another action for producing a daily schedule and allow editing of tasks.Perhaps another action could be to check time availability and priority of tasks.
- What classes did you include, and what responsibilities did you assign to each?
I included the Owner, Pet, Task and Schedule classes. The Owner class has the reponsibility of adding pets and removing pets from its list of pets. The Pet class has the responsibilities of retrieving pet needs, adding pet needs and removing pet needs. Task class has the responsibility of updating priorities of tasks, adding tasks and removing tasks. Schedule class has the responsibilities of generating a schedule, prioritizing tasks and rescheduling tasks.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
Yes, I removed add_task and remove_task from the Task class and moved them to the Pet class. This is because AI said that having them in Task class cannot work as a single task has no list to add itself to or remove itself from. It recommended moving them to Scheduler or to Pet. 
I also changed add_pet to accept the Pet object instead of just a pet name and its species. AI said that using available_times was ambiguous and that it was better to have a tuple of (start,end) times so that the scheduler can tell whether a 45 minute task can fit inside a window.
I added pet_id in the case of there being pets with the same names, so two pets can have the same name but have different ids which can be used for lookups and to remove a pet.
I added an unscheduled_task list for tasks that dont fit on a schedule instead of just dropping the tasks.
Task has a new propery called star_sort_key which returns unscheduled tasks last as without it, having start times being None would rais a TypeError.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
AI suggested a way to fix duplicate pet names by: 
```
Add owner: Owner | None = None to Pet. Owner.add_pet would set pet.owner = self. A pet could then be identified as (owner name, pet name).
Because Pet is defined before Owner, the hint needs a string annotation ("Owner | None") or from __future__ import annotations.
Dataclasses generate __repr__ and __eq__ from every field. A two-way link would make Owner print its pets, which print their owner, and so on forever. It would also make == recurse. To avoid that, declare the field as field(default=None, repr=False, compare=False).
```
It also suggested to skip the back-reference and give each pet a unique id. I went with the second option as it was something I understood better and it also shows that it would also be better for handling pets with the same name under the same owner. 
- How did you evaluate or verify what the AI suggested?
I evaluated what AI suggested by reading its explanations and pros and cons of each option. For example it said that Option 2 provides uniqeness while Option 1 is worth adding if you want to show "Rex(Jerome's dog) in the plan.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
