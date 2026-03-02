from pathlib import Path
from abc import ABC, abstractmethod
import copy
import logging
import math


class PageReplacementAlgo(ABC):
    def __init__(self, total_page_frames: int, pages: list[int]) -> None:
        self.total_page_frames: int = total_page_frames
        self.frames: list = []
        self.pages: list[int] = pages


    def isFull(self) -> bool:
        return True if len(self.frames) >= self.total_page_frames else False
    

    @abstractmethod
    def get_page(self, index: int):
        pass


    @abstractmethod
    def add_page(self, index: int):
        page: int = self.pages[index]
        self.frames.append(page)


    @abstractmethod
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


    def get_page(self, index: int):
        pass


    def add_page(self, index: int):
        page: int = self.pages[index]
        self.frames.append(page)


    def replace_page(self, index: int):
        """
        Replace the page whose next reference is furthest in future
        """

        remaining_pages = self.pages[index+1:] # only looking at future references

        # getting future references for current frames (inf if no more references)
        next_references = [remaining_pages.index(page) if page in remaining_pages else math.inf for page in self.frames]

        furthest_reference = max(next_references)
        furthest_index = next_references.index(furthest_reference)

        self.frames.pop(furthest_index)
        self.add_page(index)



class FIFO(PageReplacementAlgo):
    def __init__(self, total_page_frames: int, pages: list[int]) -> None:
        super().__init__(total_page_frames, pages)


    def get_page(self, index: int):
        pass


    def add_page(self, index: int):
        page: int = self.pages[index]
        self.frames.append(page)

    
    def replace_page(self, index: int):
        self.frames.pop(0)
        self.add_page(index)



class LRU(PageReplacementAlgo):
    def __init__(self, total_page_frames: int, pages: list[int]) -> None:
        super().__init__(total_page_frames, pages)


    def get_page(self, index):
        """
        Referenced page gets put back to the top of the stack
        """
        page: int = self.pages[index]
        self.frames.pop(self.frames.index(page))
        self.add_page(index)


    def add_page(self, index: int):
        page: int = self.pages[index]
        self.frames.append(page)

    
    def replace_page(self, index: int):
        """
        Replace least recently referenced page which is at the bottom of the stack
        """
        self.frames.pop(0)
        self.add_page(index)



class SecondChance(PageReplacementAlgo): 
    def __init__(self, total_page_frames: int, pages: list[int]) -> None:
        super().__init__(total_page_frames, pages)
        self.frames = [None] * total_page_frames
        self.bits = [0] * total_page_frames
        self.hand = 0 
        self.current_size = 0 # Track how many slots are actually filled


    def isFull(self) -> bool:
        return self.current_size >= self.total_page_frames


    def advance_hand(self) -> None:
        """
        Advance hand to next frame
        """
        self.hand = (self.hand + 1) % self.total_page_frames


    def get_page(self, index: int):
        """
        Referenced page get its second chance
        """
        page = self.pages[index]
        frame_index = self.frames.index(page)
        self.bits[frame_index] = 1


    def add_page(self, index: int):
        """
        Add page to frame and set second change to 0
        """
        page = self.pages[index]
        self.frames[self.hand] = page
        self.bits[self.hand] = 0
        self.current_size += 1
        self.advance_hand()


    def replace_page(self, index: int):   
        """
        Cycle through frames acknowleding second chances until it finds one page with no second chance
        """     
        while True:
            if self.bits[self.hand] == 1:
                self.bits[self.hand] = 0
                self.advance_hand()
            else:
                self.frames[self.hand] = None
                self.current_size -= 1
                self.add_page(index)
                break



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
                self.pages.append(int(line.strip()))
                line = f.readline()


    def __str__(self) -> str:
        return f"Simulation | Total Page Frames: {self.total_page_frames} | # Pages: {len(self.pages)}"
    

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