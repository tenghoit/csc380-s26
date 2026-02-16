import math
from pathlib import Path
from abc import ABC, abstractmethod
import copy

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
        return f"Throughput: {self.throughput} | Turnaround: {self.turnaround} | Context Switches: {self.context_switches}"



class Scheduler(ABC):
    def __init__(self, jobs: list[Job]) -> None:
        self.unfinished_jobs: list[Job] = jobs
        self.queue: list[Job] = []
        self.current_job: Job = None 
        self.finished_jobs: list[Job] = []

        self.total_jobs: int = len(self.unfinished_jobs)
        self.time = 0
        self.total_context_switches: int = 0


    def get_ready_jobs(self) -> None:
        ready = [job for job in self.unfinished_jobs if job.submitted_at <= self.time]
        self.unfinished_jobs = [j for j in self.unfinished_jobs if j.submitted_at > self.time]
        self.queue.extend(ready)


    def work(self) -> None:
        if self.current_job is not None:
            self.current_job.work()


    @abstractmethod
    def context_switch(self) -> None:
        pass


    def get_performance(self) -> PerformanceMetric:
        throughput = self.total_jobs / self.time
        turnaround = sum([job.getTurnaround() for job in self.finished_jobs]) / self.total_jobs
        return PerformanceMetric(throughput, turnaround, self.total_context_switches)

    
    def run(self) -> PerformanceMetric:
        while len(self.finished_jobs) != self.total_jobs:
            # print(f"finished: {len(self.finished_jobs)}")
            self.get_ready_jobs()
            self.work()
            self.context_switch()
            self.time += 1

        return self.get_performance()



class FCFS(Scheduler):
    def __init__(self, jobs: list[Job]) -> None:
        super().__init__(jobs)


    def context_switch(self) -> None:

        if self.current_job is not None and self.current_job.is_finished():
            self.current_job.finish(self.time)
            print(f"Finished at {self.time}: {self.current_job}")
            self.finished_jobs.append(self.current_job)
            self.current_job = None

        if self.current_job is None:
            if len(self.queue) == 0: return

            self.current_job = self.queue.pop(0)
            self.total_context_switches += 1
            



class Simulation:
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


    def runFCFS(self):
        jobs_copy = copy.deepcopy(self.jobs)
        manager = FCFS(jobs_copy)

        result = manager.run()

        print(result)
            
        




def main():
    data_path = Path("data.txt")

    world: Simulation = Simulation(data_path=data_path)

    world.runFCFS()





if __name__ == "__main__":
    main()