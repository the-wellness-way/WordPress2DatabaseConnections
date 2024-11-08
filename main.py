import json
import logging
import pymysql
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DB_HOST = os.environ['DB_HOST']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']

def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def get_one_email(email):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id, member_email, member_pass FROM tww_members WHERE member_email = %s"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
            if result:
                return {"user_id": result[0], "email": result[1], "password": result[2]}  # Formatted for auth0 purposes
            else:
                return None
    finally:
        connection.close()

def get_emails():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT member_email FROM tww_members"
            cursor.execute(sql)
            result = cursor.fetchall()
            emails = [row[0] for row in result]
            return emails
    finally:
        connection.close()

def insert_member(email, password, user_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO tww_members (member_email, member_pass, user_id) VALUES (%s, %s, %s)"
            cursor.execute(sql, (email, password, user_id))
            connection.commit()  
            
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error inserting user: {e}")
        return None
    finally:
        connection.close()

def HandleRequest(event, context):
    logger.info("Newest Received event: %s", json.dumps(event, indent=2))

    path = event.get('path')

    if path == "/change_password":
        body = json.loads(event['body'])
        email = body.get('email')
        password = body.get('password')
        newPassword = body.get('newPassword')

        if not email or not password or not newPassword:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required params."})
            }
        else:
            try: 
                connection = get_connection()
                with connection.cursor() as cursor:
                    cursor.execute("SELECT member_pass FROM tww_members WHERE member_email = %s", (email,))
                    result = cursor.fetchone()
                    
                    if not result:
                        return {
                            "statusCode": 404,
                            "body": json.dumps({"error": "User not found."})
                        }

                    stored_password = result[0]
                    if password != stored_password:
                        return {
                            "statusCode": 401,
                            "body": json.dumps({"error": "Incorrect password."})
                        }
                    
                    cursor.execute(
                        "UPDATE tww_members SET member_pass = %s WHERE member_email = %s",
                        (newPassword, email)
                    )
                    connection.commit()

                return {
                    "statusCode": 200,
                    "body": json.dumps({"success": True, "message": "Password changed successfully."})
                }
            except Exception as e:
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": "Error updating password.", "details": str(e)})
                }
            finally:
                connection.close()

    if path == "/delete_user":
        user_id = event['queryStringParameters'].get('user_id')

        if not user_id: 
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "User ID is required"})
            }
        else:
            try:
                connection = get_connection()
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM tww_members WHERE user_id = %s", (user_id,))
                    user = cursor.fetchone()

                    if user is None:
                        return {
                            "statusCode": 404,
                            "body": json.dumps({"error": "User not found"})
                        }

                    cursor.execute("DELETE FROM tww_members WHERE user_id = %s", (user_id,))
                    connection.commit()

                    return {
                        "statusCode": 200,
                        "body": json.dumps({"success": True})
                    }
            except Exception as e:
                logger.error(f"Error deleting user: {e}")
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": "Failed to delete user"})
                }
            finally:
                connection.close()


    if path == "/create_user":
        body = json.loads(event['body'])
        user_id = body.get('user_id')
        email = body.get('email')
        password = body.get('password')
        
        if not email or not password or not user_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Email, User ID, and password are required"})
            }
        
        member = get_one_email(email)

        if member is None:
            created_id = insert_member(email, password, user_id)

            if created_id is None:
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": "Failed to create user"})
                }

            new_user = TwwUser.from_id(created_id)

            if new_user:
                data = {
                    "id": new_user.id,               # Incremental ID
                    "member_email": new_user.member_email,
                    "user_id": new_user.user_id      # Auth0 ID
                }
                
                return {
                    "statusCode": 200,
                    "body": json.dumps(data)
                }
            else:
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": "Failed to fetch new user data"})
                }
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "User already exists"})
            } 

    elif path == "/verify":
        body = json.loads(event['body'])
        email = body.get('email')

        if not email:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Email is required"})
            }
        else:
            try:
                connection = get_connection()
                with connection.cursor() as cursor:
                    # Update is_active to 1 for the provided email
                    cursor.execute(
                        "UPDATE tww_members SET is_active = 1 WHERE member_email = %s",
                        (email,)
                    )
                    connection.commit()

                return {
                    "statusCode": 200,
                    "body": json.dumps({"success": True, "message": "Email verified successfully."})
                }
            except Exception as e:
                logger.error(f"Error verifying email: {e}")
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": "Failed to verify email", "details": str(e)})
                }
            finally:
                connection.close() 
    
    elif path == "/get_user":
        body = json.loads(event['body'])
        email = body.get('email')
        if not email:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Email is required"})
            }
        
        member = get_one_email(email)
        
        if member:
            data = {
                "user_id": member["user_id"],
                "email": member["email"],
                "password": member["password"]
            }
        else:
            data = {
                "user_id": None,
                "email": None,
                "password": None
            }
        
        return {
            "statusCode": 200,
            "body": json.dumps(data)
        }
    
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Route not found"})
        }

class TwwUser:
    def __init__(self, id, member_email, member_pass, user_id):
        self.id = id                     # Incremental ID
        self.member_email = member_email
        self.member_pass = member_pass
        self.user_id = user_id           # Auth0 ID

    @classmethod
    def from_id(cls, id):
        """Fetches a user from the database by ID and returns a TwwUser instance."""
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, member_email, member_pass, user_id FROM tww_members WHERE id = %s", (id,))
                data = cursor.fetchone()
                if data:
                    return cls(data[0], data[1], data[2], data[3])  # Map all fields to TwwUser attributes
                else:
                    return None
        finally:
            connection.close()

