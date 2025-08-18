from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from common.env import MQSQL_CONNECTION_STRING

import logging
import os
import uuid
import json
import datetime
import sqlalchemy
from decimal import Decimal


# Pool size is dependent on our QueryPerSeconds and running time of queries on average timespan ~1Day avg
engine = create_engine(
    MQSQL_CONNECTION_STRING,
    pool_size=100,
    pool_recycle=3600,
    connect_args={"connect_timeout": 10},
)
Session = sessionmaker(bind=engine)


def sql_execute_on_session(session, sql_command):
    return session.execute(sql_command)


def sql_execute_on_engine(sql_command):
    return engine.execute(sql_command)


def session_wrap_ambiguous(functionHandler, autoflush=False):
    def wrap(*args, **kwargs):
        if kwargs.get("session"):
            session = kwargs["session"]
        elif any(isinstance(x, sqlalchemy.orm.session.Session) for x in args):
            args_array = [
                x for x in args if isinstance(x, sqlalchemy.orm.session.Session)
            ]
            session = args_array[0]
        else:
            session = Session(autoflush=autoflush)
            kwargs["session"] = session

        try:
            result = functionHandler(*args, **kwargs)
        except Exception as e:
            session.rollback()
            logging.error("SQL Commit Error: {}".format(e))
            raise e
        finally:
            session.close()

        return result

    return wrap


def session_wrap(functionHandler, autoflush=False):
    def wrap(*args, **kwargs):
        session = Session(autoflush=autoflush)
        kwargs["session"] = session

        try:
            result = functionHandler(*args, **kwargs)
        except Exception as e:
            session.rollback()
            logging.error("SQL Commit Error: {}".format(e))
            raise e
        finally:
            session.close()

        return result

    return wrap


def session_wrap_noautoflush(functionHandler):
    return session_wrap(functionHandler, autoflush=False)


def sql_clone(model, row):
    copy = model()

    for col in row.__table__.columns:
        try:
            copy.__setattr__(col.name, getattr(row, col.name))
        except Exception as e:
            print(e)
            continue

    return copy


def sql_to_dict(sql_object, serializable=False, table_columns=None, for_bq=False):
    if not table_columns:
        table_columns = sql_object.__table__.columns.keys()

    base_dict = dict((col, getattr(sql_object, col)) for col in table_columns)

    if serializable:
        return json.loads(json.dumps(base_dict, default=str))

    if for_bq:
        for key in base_dict:
            if isinstance(
                base_dict[key], (datetime.datetime, datetime.date, list, dict)
            ):
                base_dict[key] = str(base_dict[key])
            if isinstance(base_dict[key], Decimal):
                base_dict[key] = float(base_dict[key])

    return base_dict


# def sql_unittest_restore_dump(dumpFilePath):
#     command = "mysql -u {} -p{} unittest_plutus_exchange < {}".format(
#         SQL_DBUSER, SQL_DBPASS, dumpFilePath
#     )
#     os.system(command)


def sql_check_positivity(self, key, amount):
    if float(amount) < 0:
        raise ValueError(
            "{} for {} cannot be negative. Found to be {}".format(
                key, type(self).__name__, amount
            )
        )
    return amount


def sql_check_choices(self, key, value, choices):
    if value in choices:
        return value
    raise ValueError(
        "'{}' is not a valid choice for '{}' column in '{}' table".format(
            value, key, type(self).__name__
        )
    )


def sql_create_table(headers, session, name=None):
    if not name:
        name = "rand_table_{}".format(str(uuid.uuid4())).replace("-", "_")
        sql_execute_on_session(session, "DROP TABLE IF EXISTS {}".format(name))

    header_string = "f_id INT AUTO_INCREMENT PRIMARY KEY,\n"
    for header in headers:
        header_string += "`" + header + "` VARCHAR(100),\n"

    header_string = header_string.strip(",\n")

    sql_execute_on_session(
        session,
        """
    CREATE TABLE {name} (
    {header_string}
    );""".format(
            name=name, header_string=header_string
        ),
    )

    session.commit()

    return name
