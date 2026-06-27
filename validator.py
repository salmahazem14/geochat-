import sqlglot

BLOCKED = ["delete","update","drop","insert","truncate","copy","pg_","information_schema","alter","create","grant"]

def validate_sql(sql: str) -> tuple[bool, str]:
    lower = sql.lower()
    for word in BLOCKED:
        if word in lower:
            return False, f"Blocked keyword detected: {word}"
    try:
        parsed = sqlglot.parse_one(sql)
        if parsed.key != "select":
            return False, "Only SELECT statements are allowed"
    except Exception as e:
        return False, f"SQL parse error: {str(e)}"
    return True, "OK"