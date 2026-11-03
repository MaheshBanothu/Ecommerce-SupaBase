from database.connection import DatabaseConnction


class AuthQueries:

    @staticmethod
    def getUserData(email: str):
        db_config = None
        cursor = None

        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)

            query = """
                SELECT *
                FROM users
                WHERE email = %s
            """

            cursor.execute(query, (email,))
            user = cursor.fetchone()

            if user:
                return True, user

            return False, "Email Not Exists"

        except Exception as e:
            return False, (
                f"Something wrong in database/utilsDB."
                f"AuthQueries.getUserData(): {e}"
            )

        finally:
            if cursor:
                cursor.close()

            if db_config:
                db_config.close()

    @staticmethod
    def insertUserRecord(
        name: str,
        email: str,
        phone: str,
        password: str
    ):
        db_config = None
        cursor = None

        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor()

            query = """
                INSERT INTO users (
                    username,
                    email,
                    hashpassword,
                    phone,
                    role
                )
                VALUES (%s, %s, %s, %s, %s::user_role)
            """

            cursor.execute(
                query,
                (name, email, password, phone, "user")
            )

            db_config.commit()

            return True, "Successfully account created"

        except Exception as e:
            if db_config:
                db_config.rollback()

            return False, (
                f"Something wrong in database/utilsDB."
                f"AuthQueries.insertUserRecord(): {e}"
            )

        finally:
            if cursor:
                cursor.close()

            if db_config:
                db_config.close()