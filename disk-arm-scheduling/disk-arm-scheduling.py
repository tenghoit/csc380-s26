import random
from pathlib import Path

def generate_requests(num_requests: int, num_tracks: int, output_path: Path):
    # Divide disk into thirds
    left_boundary: int = num_tracks // 3
    right_boundary: int = 2 * num_tracks // 3

    left_tracks = range(0, left_boundary)
    middle_tracks = range(left_boundary, right_boundary)
    right_tracks = range(right_boundary, num_tracks)

    current_side = "left"
    current_time = 0

    with open(output_path, "w") as f:
        f.write(f"{num_tracks}\n")
        current_time = 0
        
        for i in range(num_requests):
            
            # Switch the 'favored' side every 100 requests
            if i % 100 == 0:
                current_side = "right" if current_side == "left" else "left"

            roll = random.random()

            if roll < 0.8:
                track = random.choice(left_tracks if current_side == "left" else right_tracks)
            else:
                track = random.choice(middle_tracks)

            current_time += random.randint(1, 10)
            f.write(f"{current_time} {track}\n")

if __name__ == "__main__":
    generate_requests(2000, 5000, Path("data.txt"))