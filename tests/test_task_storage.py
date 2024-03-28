import unittest
from pathlib import Path

from simRT.core.task import PeriodicTask, TaskInfo
from simRT.generator.task_generator import Taskset
from simRT.utils.task_storage import TaskStorage


class TestTaskStorage(unittest.TestCase):
    def setUp(self) -> None:
        self.task_db = TaskStorage(Path("./data/test.sqlite"))

    def tearDown(self) -> None:
        self.task_db.commit()
        self.task_db.close()
        Path("./data/test.sqlite").unlink()

    def test_insert_task(self):
        self.task_db.clear()
        task1 = TaskInfo(id=2, type=PeriodicTask, wcet=3, deadline=4, period=4)
        task2 = TaskInfo(id=1, type=PeriodicTask, wcet=5, deadline=6, period=7)
        task3 = TaskInfo(id=3, type=PeriodicTask, wcet=8, deadline=9, period=9)
        self.task_db.insert_task(task1)
        self.task_db.insert_task(task2)
        self.task_db.insert_task(task3)

    def test_insert_taskset(self):
        self.task_db.clear()
        task2 = TaskInfo(id=2, type=PeriodicTask, wcet=3, deadline=4, period=4)
        task1 = TaskInfo(id=1, type=PeriodicTask, wcet=5, deadline=6, period=7)
        task3 = TaskInfo(id=3, type=PeriodicTask, wcet=8, deadline=9, period=9)
        task4 = TaskInfo(id=4, type=PeriodicTask, wcet=8, deadline=9, period=9)
        self.task_db.insert_task(task1)
        self.task_db.insert_task(task2)
        self.task_db.insert_task(task3)
        self.task_db.insert_task(task4)

        tasksets: list[Taskset] = [
            [task1, task2, task3],
            [task2, task3],
            [task1],
            [task1, task2, task3, task4],
        ]
        ns_result = [True, True, True, False]
        sufficient = [False, True, False, False]
        for taskset, ns, s in zip(tasksets, ns_result, sufficient):
            self.task_db.insert_taskset(taskset, ns, s)

    def test_get_tasksets_dict(self):
        self.task_db.clear()
        task2 = TaskInfo(id=2, type=PeriodicTask, wcet=3, deadline=4, period=4)
        task1 = TaskInfo(id=1, type=PeriodicTask, wcet=5, deadline=6, period=7)
        task3 = TaskInfo(id=3, type=PeriodicTask, wcet=8, deadline=9, period=9)
        task4 = TaskInfo(id=4, type=PeriodicTask, wcet=8, deadline=9, period=9)
        self.task_db.insert_task(task1)
        self.task_db.insert_task(task2)
        self.task_db.insert_task(task3)
        self.task_db.insert_task(task4)

        tasksets: list[Taskset] = [
            [task1, task2, task3],
            [task2, task3],
            [task1],
            [task1, task2, task3, task4],
        ]
        ns_result = [True, True, True, False]
        sufficient = [False, True, False, False]
        for taskset, ns, s in zip(tasksets, ns_result, sufficient):
            self.task_db.insert_taskset(taskset, ns, s)
        self.task_db.commit()

        tasksets_dict = self.task_db.get_tasksets_dict()

        for i, j in zip(tasksets_dict.keys(), tasksets):
            self.assertEqual(list(i), j)

        for i, ns, s in zip(tasksets_dict.values(), ns_result, sufficient):
            self.assertEqual(i, (ns, s))
