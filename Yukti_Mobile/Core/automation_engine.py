import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "Database" / "yukti.db"

class AutomationEngine:
    def __init__(self):
        self.db=str(DB_PATH)

    def _connect(self):
        print("=" * 60)
        print("Automation Engine DB :", self.db)
        print("=" * 60)
        return sqlite3.connect(self.db)

    def register(self,name):
        conn=self._connect()
        cur=conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS automation_modules(
            module_name TEXT PRIMARY KEY,
            status TEXT,last_run TEXT,records INTEGER,success INTEGER,
            failed INTEGER,duration TEXT,version TEXT,health INTEGER,
            machine TEXT,enabled INTEGER)''')
        cur.execute("SELECT 1 FROM automation_modules WHERE module_name=?",(name,))
        if cur.fetchone() is None:
            cur.execute("INSERT INTO automation_modules VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (name,'Idle','-',0,0,0,'0 sec','1.0',100,'SERVER',1))
        conn.commit();conn.close()

    def start(self,name):
        self._status(name,'Running')

    def stop(self,name):
        self._status(name,'Completed')

    def error(self,name):
        self._status(name,'Error')

    def _status(self,name,status):
        conn=self._connect();cur=conn.cursor()
        cur.execute('UPDATE automation_modules SET status=?,last_run=? WHERE module_name=?',
        (status,datetime.now().strftime('%d-%m-%Y %H:%M:%S'),name))
        conn.commit();conn.close()

    def update_stats(self,name,records=0,success=0,failed=0,duration='0 sec'):
        conn=self._connect();cur=conn.cursor()
        cur.execute('''UPDATE automation_modules
        SET records=?,success=?,failed=?,duration=?,last_run=?
        WHERE module_name=?''',
        (records,success,failed,duration,datetime.now().strftime('%d-%m-%Y %H:%M:%S'),name))
        conn.commit();conn.close()

    def get_module(self,name):
        conn=self._connect();conn.row_factory=sqlite3.Row
        cur=conn.cursor()
        cur.execute('SELECT * FROM automation_modules WHERE module_name=?',(name,))
        r=cur.fetchone();conn.close()
        return dict(r) if r else None

    def get_all(self):
        conn=self._connect();conn.row_factory=sqlite3.Row
        cur=conn.cursor();cur.execute('SELECT * FROM automation_modules')
        rows=[dict(x) for x in cur.fetchall()]
        conn.close()
        return {r['module_name']:r for r in rows}

    def enable(self,name):
        conn=self._connect();cur=conn.cursor()
        cur.execute('UPDATE automation_modules SET enabled=1 WHERE module_name=?',(name,))
        conn.commit();conn.close()

    def disable(self,name):
        conn=self._connect();cur=conn.cursor()
        cur.execute('UPDATE automation_modules SET enabled=0 WHERE module_name=?',(name,))
        conn.commit();conn.close()


