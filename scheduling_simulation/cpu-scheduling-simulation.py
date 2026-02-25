import math
from pathlib import Path
from abc import ABC, abstractmethod
import copy
import logging

class Job:
    def __init__(self, id, submitted_at, duration) -> None:
        self.id = int(id)
        self.submitted_at = int(submitted_at)
        self.duration = int(duration)

        self.currentDuration = self.duration
        self.finished_at = math.inf


    def is_finished(self) -> bool:
        return self.currentDuration <= 0 
    

    def finish(self, time) -> None:
        self.finished_at = time


    def getTurnaround(self) -> float:
        return self.finished_at - self.submitted_at
    

    def work(self) -> None:
        self.currentDuration -= 1


    def __str__(self) -> str:
        return f"Job {self.id} submitted at {self.submitted_at} with duration {self.duration}"
    


class PerformanceMetric:
    def __init__(self, throughput, turnaround, context_switches) -> None:
        self.throughput = throughput
        self.turnaround = turnaround
        self.context_switches = context_switches


    def __str__(self) -> str:
        return f"{self.turnaround}, {self.context_switches}"



class Scheduler(ABC):
    def __init__(self, jobs: list[Job]) -> None:
        self.unfinished_jobs: list[Job] = jobs
        self.queue: list[Job] = []
        self.current_job: Job = None 
        self.finished_jobs: list[Job] = []

        self.total_jobs: int = len(self.unfinished_jobs)
        self.time = 0
        self.total_context_switches: int = 0
        self.added_jobs: bool = False


    def get_ready_jobs(self) -> None:
        """
        Add ready jobs to queue base on current time
        """
        ready = [job for job in self.unfinished_jobs if job.submitted_at <= self.time]
        if ready: self.added_jobs = True
        self.unfinished_jobs = [j for j in self.unfinished_jobs if j.submitted_at > self.time]
        self.queue.extend(ready)


    def work(self) -> None:
        """
        Work on current job and manages the finishing process
        """
        if self.current_job is not None:
            self.current_job.work()

        if self.current_job is not None and self.current_job.is_finished():
            self.current_job.finish(self.time)
            # print(f"Finished at {self.time}: {self.current_job}")
            self.finished_jobs.append(self.current_job)
            self.current_job = None


    @abstractmethod
    def context_switch(self) -> None:
        """
        Each scheduler will implement a different context_switch
        """
        pass


    def get_performance(self) -> PerformanceMetric:
        throughput = self.total_jobs / self.time
        turnaround = sum([job.getTurnaround() for job in self.finished_jobs]) / self.total_jobs
        return PerformanceMetric(throughput, turnaround, self.total_context_switches)

    
    def run(self) -> PerformanceMetric:
        """
        Template Pattern shared across all schedulers
        """
        while len(self.finished_jobs) != self.total_jobs:
            self.get_ready_jobs()
            self.work()
            self.context_switch()
            self.time += 1
            self.added_jobs = False

        return self.get_performance()



class FCFS(Scheduler):
    """
    First-come First-served
    """
    def __init__(self, jobs: list[Job]) -> None:
        super().__init__(jobs)


    def context_switch(self) -> None:
        if not self.queue: return

        if self.current_job is None:
            self.current_job = self.queue.pop(0) # get next job
            self.total_context_switches += 1



class SJF(Scheduler):
    """
    Shortest Job First
    """
    def __init__(self, jobs: list[Job]) -> None:
        super().__init__(jobs)


    def context_switch(self) -> None:
        if not self.queue: return

        if self.current_job is None:      
            shortest_job = min(self.queue, key=lambda job: job.duration) # get shortest job in queue
            self.queue.remove(shortest_job)
            self.current_job = shortest_job
            self.total_context_switches += 1



class SRTN(Scheduler):
    """
    Shortest Runtime Next
    """
    def __init__(self, jobs: list[Job]) -> None:
        super().__init__(jobs)


    def context_switch(self) -> None:
        if not self.queue: return

        shortest_runtime_job = min(self.queue, key=lambda job: job.currentDuration)

        if self.current_job is None:
            self.queue.remove(shortest_runtime_job)
            self.current_job = shortest_runtime_job
            self.total_context_switches += 1

        elif shortest_runtime_job.currentDuration < self.current_job.currentDuration:
            self.queue.remove(shortest_runtime_job)
            self.queue.append(self.current_job) # incomplete job gets added back to queue
            self.current_job = shortest_runtime_job
            self.total_context_switches += 1
        
        elif shortest_runtime_job.currentDuration >= self.current_job.currentDuration and self.added_jobs:
            self.total_context_switches += 1



class RR(Scheduler):
    """
    Round Robin
    """
    def __init__(self, jobs: list[Job]) -> None:
        super().__init__(jobs)


    def context_switch(self) -> None:
        self.total_context_switches += 1
        if not self.queue: return

        if self.current_job is not None: self.queue.append(self.current_job) # incomplete job gets added back to queue
        self.current_job = self.queue.pop(0)



class Simulation:
    """
    Responsible for running experiments
    """
    def __init__(self, data_path):
        self.jobs = self.read_data(data_path)


    def read_data(self, file_path: Path) -> list[Job]:
        jobs: list[Job] = []

        with open(file_path, "r") as f:
            line = f.readline()
            while line != "":
                tokens = line.split()
                jobs.append(Job(tokens[0], tokens[1], tokens[2]))
                line = f.readline()

        return jobs
    

    def printJobs(self) -> None:
        for job in self.jobs:
            print(job)


    def run(self):
        schedulers = [FCFS, SJF, SRTN, RR]
        print(f"algorithm, turnaround, context_switches")
        for scheduler in schedulers:
            jobs_copy = copy.deepcopy(self.jobs)
            manager = scheduler(jobs_copy)
            result = manager.run()
            print(f"{scheduler.__name__}, {result}")



def main():
    data_path = Path("data.txt")
    world: Simulation = Simulation(data_path=data_path)
    world.run()


if __name__ == "__main__":
    main()