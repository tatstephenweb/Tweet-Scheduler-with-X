"""
db_helpers.py — Poster database functions
Requires: pip install mysql-connector-python werkzeug
"""

import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="poster_db"
    )


# ---------- Traditional signup / login ----------

def create_user(name, email, password):
    hashed_pw = generate_password_hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)"
    cursor.execute(query, (name, email, hashed_pw))
    conn.commit()

    new_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return new_id


def verify_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query, (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user and check_password_hash(user["password_hash"], password):
        return user
    return None

# ---------- Twitter account linking ----------
def link_twitter_account(user_id, twitter_user_id, twitter_username,
                          access_token, refresh_token=None):
    """
    Save or update a linked Twitter account for a given user.
    Call this right after a successful OAuth callback.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO twitter_accounts
            (user_id, twitter_user_id, twitter_username, access_token, refresh_token)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            twitter_username = %s,
            access_token = %s,
            refresh_token = %s
    """
    cursor.execute(query, (
        user_id, twitter_user_id, twitter_username, access_token, refresh_token,
        twitter_username, access_token, refresh_token
    ))
    conn.commit()

    cursor.close()
    conn.close()

def get_twitter_accounts(user_id):
    """Return all Twitter accounts linked to a given user."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM twitter_accounts WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    accounts = cursor.fetchall()

    cursor.close()
    conn.close()
    return accounts

#change user password
def change_password(email, newpassword):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = ("SELECT * FROM users where email = %s",(email))
    cursor.execute(query)
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        return user
    return None
