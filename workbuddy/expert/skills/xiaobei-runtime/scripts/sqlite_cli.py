#!/usr/bin/env python3
"""SQLite CLI subset used by the preserved record tools, using Python stdlib."""
import json
from pathlib import Path
import sqlite3
import sys


def main(argv):
    mode, headers, separator = 'list', False, '|'
    args = list(argv)
    while args and args[0].startswith('-'):
        option = args.pop(0)
        if option == '-json':
            mode = 'json'
        elif option == '-column':
            mode = 'column'
        elif option in ('-header', '-headers'):
            headers = True
        elif option == '-separator':
            separator = args.pop(0)
        elif option != '-bail':
            raise ValueError(f'unsupported SQLite option: {option}')
    if not args:
        raise ValueError('database path required')
    database = args.pop(0)
    sql = args.pop(0) if args else sys.stdin.read()
    if args:
        raise ValueError('unexpected SQLite arguments')
    connection = sqlite3.connect(database, isolation_level=None)
    connection.create_function('readfile', 1, lambda name: Path(name).read_bytes())
    statement = ''
    try:
        for character in sql + '\n':
            statement += character
            if character != ';' or not sqlite3.complete_statement(statement):
                continue
            cursor = connection.execute(statement)
            statement = ''
            if cursor.description is None:
                continue
            names = [item[0] for item in cursor.description]
            rows = cursor.fetchall()
            if mode == 'json':
                if rows:
                    print(json.dumps([dict(zip(names, row)) for row in rows], ensure_ascii=False))
            else:
                if headers:
                    print(separator.join(names))
                for row in rows:
                    print(separator.join('' if value is None else str(value) for value in row))
        if statement.strip():
            cursor = connection.execute(statement)
            if cursor.description:
                names = [item[0] for item in cursor.description]
                rows = cursor.fetchall()
                if mode == 'json' and rows:
                    print(json.dumps([dict(zip(names, row)) for row in rows], ensure_ascii=False))
                else:
                    for row in rows:
                        print(separator.join('' if value is None else str(value) for value in row))
    finally:
        connection.close()


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except (ValueError, OSError, sqlite3.Error) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
