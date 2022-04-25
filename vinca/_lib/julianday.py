import sqlite3
con = sqlite3.connect(":memory:")

def julianday():
        return list(con.execute("select julianday('now')"))[0][0]
