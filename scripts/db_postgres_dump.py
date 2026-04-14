"""
Script used on 14th Apr 2026 to backup the Google Postgres database to a local SQLite file. This is not intended to be a general purpose script, but it can be adapted for other uses if needed.

To use this script you will need a postgres config file service name and a local path to save the SQLite file to. You can run this script from the command line with `python db_postgres_dump.py` after filling in those details.

Philip Bailey
2026-04-14
"""
import logging
import itertools

from sqlalchemy import create_engine, inspect, text
from sqlite_utils import Database

logging.basicConfig(level=logging.INFO)


def db_dump(
    connection: str,
    path: str,
    export_all: bool,
    table,
    skip,
    redact,
    sql,
    output,
    pk,
    index_fks: bool,
    progress: bool,
    postgres_schema: str,
):
    """
    Load data from any database into SQLite.

    PATH is a path to the SQLite file to create, e.c. /tmp/my_database.db

    CONNECTION is a SQLAlchemy connection string, for example:

        postgresql://localhost/my_database
        postgresql://username:passwd@localhost/my_database

        mysql://root@localhost/my_database
        mysql://username:passwd@localhost/my_database

    More: https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls
    """

    if not export_all and not table and not sql:
        raise Exception("--all OR --table OR --sql required")

    if skip and not export_all:
        raise Exception("--skip can only be used with --all")

    redact_columns = {}
    for table_name, column_name in redact:
        redact_columns.setdefault(table_name, set()).add(column_name)

    db_obj = Database(path)
    # build list of schema names from comma separated argument.
    schemas = postgres_schema.split(',') if postgres_schema is not None else [None]
    for schema in schemas:
        conn_args = {"options": f"-csearch_path={schema}"} if schema is not None else {}
        if connection.startswith("postgres://"):
            connection = connection.replace("postgres://", "postgresql://")
        db_conn = create_engine(connection, connect_args=conn_args).connect()
        inspector = inspect(db_conn)
        # Figure out which tables we are copying, if any
        tables = table
        if export_all:
            tables = inspector.get_table_names()
        if tables:
            foreign_keys_to_add = []
            for i, table in enumerate(tables):
                if progress:
                    print(f"{i+1}/{len(tables)}: {table}")
                if table in skip:
                    if progress:
                        print("  ... skipping")
                    continue
                pks = inspector.get_pk_constraint(table)["constrained_columns"]
                if len(pks) == 1:
                    pks = pks[0]
                fks = inspector.get_foreign_keys(table)
                foreign_keys_to_add.extend(
                    [
                        (
                            # table, column, other_table, other_column
                            table,
                            fk["constrained_columns"][0],
                            fk["referred_table"],
                            fk["referred_columns"][0],
                        )
                        for fk in fks
                    ]
                )
                table_quoted = db_conn.dialect.identifier_preparer.quote_identifier(table)
                results = db_conn.execute(text(f"select * from {table_quoted}")).mappings()
                redact_these = redact_columns.get(table) or set()
                rows = (redacted_dict(r, redact_these) for r in results)
                # Make sure generator is not empty
                try:
                    first = next(rows)
                except StopIteration:
                    # This is an empty table - create an empty copy
                    if not db_obj[table].exists():
                        create_columns = {}
                        for column in inspector.get_columns(table):
                            try:
                                column_type = column["type"].python_type
                            except NotImplementedError:
                                column_type = str
                            create_columns[column["name"]] = column_type
                        db_obj[table].create(create_columns)
                else:
                    rows = itertools.chain([first], rows)
                    db_obj[table].insert_all(rows, pk=pks, replace=True)
            foreign_keys_to_add_final = []
            for table, column, other_table, other_column in foreign_keys_to_add:
                # Make sure both tables exist and are not skipped - they may not
                # exist if they were empty and hence .insert_all() didn't have a
                # reason to create them.
                if (
                    db_obj[table].exists()
                    and table not in skip
                    and db_obj[other_table].exists()
                    and other_table not in skip
                    # Also skip if this column is redacted
                    and ((table, column) not in redact)
                ):
                    foreign_keys_to_add_final.append(
                        (table, column, other_table, other_column)
                    )
            if foreign_keys_to_add_final:
                # Add using .add_foreign_keys() to avoid running multiple VACUUMs
                if progress:
                    print(
                        "\nAdding {} foreign key{}\n{}".format(
                            len(foreign_keys_to_add_final),
                            "s" if len(foreign_keys_to_add_final) != 1 else "",
                            "\n".join(
                                "  {}.{} => {}.{}".format(*fk)
                                for fk in foreign_keys_to_add_final
                            ),
                        )
                    )
                db_obj.add_foreign_keys(foreign_keys_to_add_final)
        if sql:
            if not output:
                raise Exception("--sql must be accompanied by --output")
            results = db_conn.execute(text(sql)).mappings()
            rows = (dict(r) for r in results)
            db_obj[output].insert_all(rows, pk=pk)
        if index_fks:
            db_obj.index_foreign_keys()


def detect_primary_key(db_conn, table):
    """_summary_

    Args:
        db_conn (_type_): _description_
        table (_type_): _description_

    Raises:
        Exception: _description_

    Returns:
        _type_: _description_
    """
    inspector = inspect(db_conn)
    pks = inspector.get_pk_constraint(table)["constrained_columns"]
    if len(pks) > 1:
        raise Exception("Multiple primary keys not currently supported")
    return pks[0] if pks else None


def redacted_dict(row, redact):
    """_summary_

    Args:
        row (_type_): _description_
        redact (_type_): _description_

    Returns:
        _type_: _description_
    """
    out_dict = dict(row)
    for key in redact:
        if key in out_dict:
            out_dict[key] = "***"
    return out_dict


def main():
    """_summary_

    Raises:
        Exception: _description_
    """

    postgres_conn_str = f"postgresql://?service={'CHaMPGooglePostgres'}"
    sqlite_path = "TODO: PUT local path here, e.g. /tmp/my_database.db"

    # Example usage:
    db_dump(
        connection=postgres_conn_str,
        path=sqlite_path,
        export_all=True,
        table=None,
        skip=[],
        redact={},  # redact=[("users", "email")],
        sql=None,
        output=None,
        pk=None,
        index_fks=True,
        progress=True,
        postgres_schema="public"
    )


if __name__ == "__main__":
    main()
