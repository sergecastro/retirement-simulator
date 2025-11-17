import html

class InputSanitizer:
    @staticmethod
    def sanitize_text(text: str, max_length=None) -> str:
        if not isinstance(text, str):
            return ""
        safe = html.escape(text.strip())
        if max_length:
            safe = safe[:max_length]
        return safe

    @staticmethod
    def sanitize_number(value, min_val=None, max_val=None, default=0) -> float:
        try:
            val = float(value)
            if min_val is not None:
                val = max(min_val, val)
            if max_val is not None:
                val = min(max_val, val)
            return val
        except (TypeError, ValueError):
            return default

    @staticmethod
    def sanitize_age(age) -> int:
        return int(InputSanitizer.sanitize_number(age, min_val=18, max_val=120, default=30))

    @staticmethod
    def sanitize_currency(amount) -> float:
        return InputSanitizer.sanitize_number(amount, min_val=0, max_val=100_000_000, default=0.0)

def safe_text(text): return InputSanitizer.sanitize_text(text)
def safe_number(value): return InputSanitizer.sanitize_number(value)
def safe_age(age): return InputSanitizer.sanitize_age(age)
def safe_currency(amount): return InputSanitizer.sanitize_currency(amount)
