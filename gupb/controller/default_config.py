from gupb.controller import keyboard, ancymon
from gupb.controller import random

CONFIGURATION = {
    "arenas": [
        "lone_sanctum",
    ],
    "controllers": [
        ancymon.AncymonController("Ancymon"),
        random.RandomController("Alice"),
        random.RandomController("Bob"),
        random.RandomController("Cecilia"),
        random.RandomController("Darius"),
    ],
    "start_balancing": False,
    "visualise": False,
    "show_sight": ancymon.AncymonController("Ancymon"),
    "runs_no": 100,
    "profiling_metrics": [],
}
