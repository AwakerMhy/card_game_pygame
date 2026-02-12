"""
动画系统：动画队列、缓动、可跳过
"""
import time
from typing import Callable, List, Optional


def ease_in_out(t: float) -> float:
    """缓动函数：ease-in-out"""
    if t < 0.5:
        return 2 * t * t
    return 1 - pow(-2 * t + 2, 2) / 2


class Animation:
    def __init__(self, duration: float, on_update: Callable[[float], None],
                 on_complete: Optional[Callable] = None):
        self.duration = duration
        self.on_update = on_update
        self.on_complete = on_complete
        self.start_time = 0
        self.running = False

    def start(self):
        self.start_time = time.time()
        self.running = True

    def tick(self) -> bool:
        if not self.running:
            return False
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            self.on_update(1.0)
            if self.on_complete:
                self.on_complete()
            self.running = False
            return False
        t = ease_in_out(elapsed / self.duration)
        self.on_update(t)
        return True


class AnimationQueue:
    def __init__(self):
        self.queue: List[Animation] = []
        self.current: Optional[Animation] = None

    def add(self, anim: Animation):
        self.queue.append(anim)

    def tick(self) -> bool:
        if self.current:
            if self.current.tick():
                return True
            self.current = None
        if self.queue:
            self.current = self.queue.pop(0)
            self.current.start()
            return self.current.tick()
        return False

    def skip_all(self):
        self.queue.clear()
        if self.current:
            self.current.on_update(1.0)
            if self.current.on_complete:
                self.current.on_complete()
            self.current = None
