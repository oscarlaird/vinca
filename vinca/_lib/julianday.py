import sqlite3
conn = sqlite3.connect(":memory:")

def now():
        return conn.execute("select julianday('now','localtime') + 0.5").fetchone()[0]
def today():
        return int(now())
