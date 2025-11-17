import os, json, time, threading
from collections import deque

class AIRateLimiter:
    def __init__(self, max_calls=5, time_window=86400, cache_dir=".cache", cache_file="ai_rate_limits.json"):
        self.max_calls = max_calls
        self.time_window = time_window
        self.cache_path = os.path.join(cache_dir, cache_file)
        self._lock = threading.Lock()
        self._history = {}
        os.makedirs(cache_dir, exist_ok=True)
        self._load_from_disk()

    def _load_from_disk(self):
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r") as f:
                    raw = json.load(f)
                    self._history = {uid: deque(times, maxlen=self.max_calls) for uid, times in raw.items()}
            except Exception:
                pass

    def _save_to_disk(self):
        with self._lock:
            try:
                with open(self.cache_path, "w") as f:
                    json.dump({uid: list(q) for uid, q in self._history.items()}, f, indent=2)
            except Exception:
                pass

    def check_limit(self, user_id="default") -> tuple[bool, int]:
        now = time.time()
        q = self._history.setdefault(user_id, deque(maxlen=self.max_calls))
        q = deque([t for t in q if now - t < self.time_window], maxlen=self.max_calls)
        self._history[user_id] = q
        allowed = len(q) < self.max_calls
        remaining = self.max_calls - len(q)
        return allowed, remaining

    def record_call(self, user_id="default"):
        now = time.time()
        with self._lock:
            q = self._history.setdefault(user_id, deque(maxlen=self.max_calls))
            q = deque([t for t in q if now - t < self.time_window], maxlen=self.max_calls)
            q.append(now)
            self._history[user_id] = q
            self._save_to_disk()

    def get_reset_time(self, user_id="default") -> float:
        now = time.time()
        q = self._history.get(user_id, deque())
        if not q:
            return 0.0
        return max(0.0, self.time_window - (now - q[0]))
