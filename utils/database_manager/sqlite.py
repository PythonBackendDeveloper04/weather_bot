import sqlite3
class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db
    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)
    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    # Create table
    def users_table(self):
        sql = """
               CREATE TABLE IF NOT EXISTS Users (
               id SERIAL PRIMARY KEY,
               telegram_id BIGINT NOT NULL UNIQUE,
               region TEXT,
               time TEXT
               );
               """
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, id: int = None,telegram_id: str = None, region: str = None, time: str = None):

        sql = """
        INSERT INTO Users(id,telegram_id, region, time) VALUES(?, ?, ?, ?)
        """
        self.execute(sql, parameters=(id,telegram_id,region,time), commit=True)

    def select_all_user(self):
        sql = """
        SELECT * FROM Users
        """
        return self.execute(sql, fetchall=True)

    # db.py
    def select_user(self, telegram_id):
        sql = "SELECT * FROM Users WHERE telegram_id = ?"
        result = self.execute(sql, parameters=(telegram_id,), fetchone=True)
        if result:
            return {
                "id": result[0],
                "telegram_id": result[1],
                "region": result[2],
                "time": result[3],
            }
        return None

    def update_user_fullname(self, email, id):

        sql = f"""
        UPDATE Users SET fullname=? WHERE id=?
        """
        return self.execute(sql, parameters=(email, id), commit=True)
    def update_user_time(self, time, telegram_id):

        sql = f"""
        UPDATE Users SET time=? WHERE telegram_id=?
        """
        return self.execute(sql, parameters=(time, telegram_id), commit=True)

    def update_user_location(self,region,telegram_id):
        sql = f"""UPDATE Users SET region=? WHERE telegram_id = ?"""
        return self.execute(sql,parameters=(region,telegram_id,),commit=True)