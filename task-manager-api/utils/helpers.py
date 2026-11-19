from datetime import datetime, timezone
import re

VALID_STATUSES = ["pending", "in_progress", "done", "cancelled"]
VALID_ROLES = ["user", "admin", "manager"]
MAX_TITLE_LENGTH = 200
MIN_TITLE_LENGTH = 3
MIN_PASSWORD_LENGTH = 4
DEFAULT_PRIORITY = 3
DEFAULT_COLOR = "#000000"
MIN_PRIORITY = 1
MAX_PRIORITY = 5


def utcnow():
    """UTC timestamp. Replaces the deprecated datetime.utcnow()."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def format_date(date_obj):
    if date_obj:
        return str(date_obj)
    return None


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    return re.match(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$", email) is not None


def sanitize_string(value):
    if value:
        return value.strip()
    return value


def generate_id():
    import uuid
    return str(uuid.uuid4())


def log_action(action, details=None):
    timestamp = utcnow()
    print(f"[{timestamp}] ACTION: {action}")
    if details:
        print(f"  DETAILS: {details}")


def parse_date(date_string):
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except (TypeError, ValueError):
        return None


def is_valid_color(color):
    return bool(color) and len(color) == 7 and color[0] == "#"


def process_task_data(data, existing_task=None):
    result = {}

    if "title" in data:
        title = data["title"] or ""
        if len(title) < MIN_TITLE_LENGTH:
            return None, "Título muito curto"
        if len(title) > MAX_TITLE_LENGTH:
            return None, "Título muito longo"
        result["title"] = title

    if "description" in data:
        result["description"] = data["description"]

    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return None, "Status inválido"
        result["status"] = data["status"]

    if "priority" in data:
        try:
            priority = int(data["priority"])
        except (TypeError, ValueError):
            return None, "Prioridade inválida"
        if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
            return None, "Prioridade deve ser entre 1 e 5"
        result["priority"] = priority

    if "due_date" in data:
        if data["due_date"]:
            parsed = parse_date(data["due_date"])
            if parsed is None:
                return None, "Formato de data inválido. Use YYYY-MM-DD"
            result["due_date"] = parsed
        else:
            result["due_date"] = None

    if "tags" in data:
        tags = data["tags"]
        if isinstance(tags, list):
            result["tags"] = ",".join(tags)
        else:
            result["tags"] = tags

    return result, None
