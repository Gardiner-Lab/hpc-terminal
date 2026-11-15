"""
Who may see whose sessions in the overview: an administrator sees everyone's; a lab lead or lab
administrator sees the sessions of the members of the labs they lead or administer. What they see is who
is connected to which machine, since when and from where, never what is on anyone's screen.

Read from the suite's own stores, read-only: administrators from the account directory (MoClo's
users.is_admin), labs from the suite database (lab_members: role 'lab_lead', or lab_admin).
"""
import os
import sqlite3
from typing import Optional, Set


def _read(path: str, sql: str, args=()) -> list:
    try:
        conn = sqlite3.connect(f'file:{path}?mode=ro', uri=True, timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            return conn.execute(sql, args).fetchall()
        finally:
            conn.close()
    except sqlite3.Error:
        return []


def is_admin(username: str) -> bool:
    rows = _read(os.environ.get('MOCLO_DB', '/moclo/moclo.db'), 'SELECT * FROM users WHERE username = ?', (username,))
    return bool(rows and 'is_admin' in rows[0].keys() and rows[0]['is_admin'])


def overseen(username: str) -> Optional[Set[str]]:
    """
    Whose sessions this member may see in the overview: None for everyone's (an administrator), else the
    members of the labs they lead or administer (empty: none, and no overview).
    """
    if is_admin(username):
        return None
    suite = os.environ.get('SUITE_DATABASE_PATH', '/suite/suite.db')
    labs = [r['lab_id'] for r in _read(
        suite, "SELECT lab_id FROM lab_members WHERE username = ? AND (role = 'lab_lead' OR lab_admin = 1)", (username,))]
    if not labs:
        return set()
    marks = ','.join('?' * len(labs))
    return {r['username'] for r in _read(suite, f'SELECT username FROM lab_members WHERE lab_id IN ({marks})', labs)}
