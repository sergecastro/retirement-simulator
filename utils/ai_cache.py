import os, json, time, hashlib, threading

class AICache:
    def __init__(self, cache_dir=".cache", cache_file="ai_explanations.json", ttl_seconds=None):
        self.cache_dir = cache_dir
        self.cache_path = os.path.join(cache_dir, cache_file)
        self.ttl_seconds = ttl_seconds
        self._lock = threading.Lock()
        self._memory_cache = {}
        os.makedirs(self.cache_dir, exist_ok=True)
        self._load_from_disk()

    def _hash_key(self, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()

    def _load_from_disk(self):
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r") as f:
                    self._memory_cache.update(json.load(f))
            except Exception:
                pass

    def _save_to_disk(self):
        with self._lock:
            try:
                with open(self.cache_path, "w") as f:
                    json.dump(self._memory_cache, f, indent=2)
            except Exception:
                pass

    def get_or_cache(self, key, compute_fn, ttl_seconds=None):
        hashed = self._hash_key(key)
        now = time.time()
        entry = self._memory_cache.get(hashed)
        if entry:
            value, timestamp = entry["value"], entry["timestamp"]
            if ttl_seconds is None:
                ttl_seconds = self.ttl_seconds
            if ttl_seconds is None or now - timestamp < ttl_seconds:
                return value
        value = compute_fn()
        self._memory_cache[hashed] = {"value": value, "timestamp": now}
        self._save_to_disk()
        return value
