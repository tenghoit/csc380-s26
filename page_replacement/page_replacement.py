from pathlib import Path
from abc import ABC, abstractmethod
import copy
import logging
import math


class PageReplacementAlgo:
    def __init__(self, total_page_frames: int, pages: list[int]) -> None:
        self.total_page_frames: int = total_page_frames
        self.frames: list[int] = []
        self.pages: list[int] = pages


    def isFull(self) -> bool:
        return True if len(self.frames) >= self.total_page_frames else False
    

    def get_page(self, index: int):
        pass


    def add_page(self, index: int):
        page: int = self.pages[index]
        self.frames.append(page)


    def replace_page(self, index: int):
        self.frames.pop(0)
        self.add_page(index)

    
    def run(self) -> int:
        total_page_faults: int = 0

        for index, page in enumerate(self.pages):

            if page in self.frames: 
                self.get_page(index)
                continue

            if self.isFull():
                self.replace_page(index)
            else:
                self.add_page(index)

            total_page_faults += 1


        return total_page_faults



class Optimal(PageReplacementAlgo):
    def __init__(self, total_page_frames: int, pages: list[int]) -> None:
        super().__init__(total_page_frames, pages)


    def replace_page(self, index: int):
        remaining_pages = self.pages[index:]

        next_references = [remaining_pages.index(page) if page in remaining_pages else math.inf for page in self.frames]

        furthest_reference = max(next_references)
        furthest_index = next_references.index(furthest_reference)

        self.frames.pop(furthest_index)
        self.add_page(index)



class FIFO(PageReplacementAlgo):
    def __init__(self, total_page_frames: int, pages: list[int]) -> None:
        super().__init__(total_page_frames, pages)



class LRU(PageReplacementAlgo):
    def __init__(self, total_page_frames: int, pages: list[int]) -> None:
        super().__init__(total_page_frames, pages)


    def get_page(self, index):
        page: int = self.pages[index]
        self.frames.pop(self.frames.index(page))
        self.add_page(index)



class SecondChance(LRU):
    def __init__(self, total_page_frames: int, pages: list[int]) -> None:
        super().__init__(total_page_frames, pages)
        self.second_chances: dict = {}

    
    def get_page(self, index: int):
        super().get_page(index)
        page: int = self.pages[index]
        self.second_chances[page] = 1


    def add_page(self, index: int):
        super().add_page(index)
        page: int = self.pages[index]
        self.second_chances[page] = 0


    def replace_page(self, index: int):
        new_page: int = self.pages[index]

        for i in range(len(self.frames) - 2, 0, -1):
            current_page = self.frames[i]
            if self.second_chances[current_page] == 1: 
                self.second_chances[current_page] = 0
                continue
            else:
                self.frames.pop(i)
                break

        self.add_page(index)







class Simulation:
    def __init__(self, data_path: Path) -> None:
        self.total_page_frames: int = 0
        self.pages: list[int] = []
        self.read_data(data_path)


    def read_data(self, data_path: Path) -> None: 
        with open(data_path, "r") as f:
            self.total_page_frames = int(f.readline())

            line = f.readline()
            while line != "":
                # print(line)
                self.pages.append(int(line.strip()))
                line = f.readline()


    def __str__(self) -> str:
        return f"Total Page Frames: {self.total_page_frames} | # Pages: {len(self.pages)}"
    

    def run(self):

        algos = [Optimal, FIFO, LRU, SecondChance]
        for algo in algos:
            thing = algo(self.total_page_frames, self.pages)
            result = thing.run()
            print(f"{algo.__name__}: {result}")
            




def main():
    data_path = Path("data.txt")
    world = Simulation(data_path)
    world.run()





if __name__ == "__main__":
    main()