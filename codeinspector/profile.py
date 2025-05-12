import cProfile
import pstats
from pathlib import Path


def profile_function(func, *args, output_file: str = "profiling.log", **kwargs):
    profile = cProfile.Profile()
    profile.enable()
    result = func(*args, **kwargs)
    profile.disable()

    log_path = Path(output_file)
    with log_path.open("w", encoding="utf-8") as stream:
        stats = pstats.Stats(profile, stream=stream)
        stats.strip_dirs().sort_stats(pstats.SortKey.CUMULATIVE).print_stats()

    return result
