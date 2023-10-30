from fastapi import FastAPI
import sqlalchemy as db
import uvicorn
import hashlib

RESPONSE_FIELD = "response"
USERNAME_FIELD = 'username'
PASSWORD_FIELD = 'password'
USER_TABLE = 'Users'
APP_PORT = 7112
MAX_NAME_LENGTH = 100
PASS_FIELD_SIZE = 32

engine = db.create_engine(f'sqlite:///database.sqlite')
conn = engine.connect()
metadata = db.MetaData()

User = db.Table(USER_TABLE, metadata,
                    db.Column(USERNAME_FIELD, db.String(MAX_NAME_LENGTH), primary_key=True),
                    db.Column(PASSWORD_FIELD, db.String(PASS_FIELD_SIZE), nullable=False))
app = FastAPI()

def get_hash(s: str) -> str:
    h = hashlib.shake_256(s.encode())
    return  h.hexdigest(PASS_FIELD_SIZE)


@app.get("/sign_up")
def sign_up(username: str, password: str):
    user = conn.execute(db.text(f"SELECT {USERNAME_FIELD} FROM {USER_TABLE} WHERE '{username}' = {USERNAME_FIELD}")).fetchall()
    if user:
        return {RESPONSE_FIELD: f"user already exists"}
    query = db.insert(User).values(username=username, password=get_hash(password))
    conn.execute(query)

    return {RESPONSE_FIELD: f"new user created"}


@app.get("/sign_out")
def sign_out(username: str, password: str):
    query = db.text(f"SELECT {PASSWORD_FIELD} FROM {USER_TABLE} WHERE '{username}' = {USERNAME_FIELD}")
    password_hash = (conn.execute(query).fetchall())[0][0]
    if password_hash == get_hash(password):
        conn.execute(db.text(f"DELETE FROM {USER_TABLE} WHERE '{username}' = {USERNAME_FIELD}"))
        return {RESPONSE_FIELD: f"user deleted"}
    return {RESPONSE_FIELD: f"cant delete user, incorrect password"}

@app.get("/auth")
def auth(username: str, password: str):
    query = db.text(f"SELECT {PASSWORD_FIELD} FROM {USER_TABLE} WHERE '{username}' = {USERNAME_FIELD}")
    password_hash = (conn.execute(query).fetchall())
    if password_hash:
        password_hash = password_hash[0][0]
        if password_hash == get_hash(password):
            return {RESPONSE_FIELD: f"user authenticated"}
    return {RESPONSE_FIELD: f"user authentication failed"}

@app.get("/health")
def health():
    return {RESPONSE_FIELD: "hello"}


if __name__ == '__main__':
    metadata.create_all(engine)
    query = db.insert(User).values(username="Test", password=get_hash("test"))
    Result = conn.execute(query)

    uvicorn.run(app, host="127.0.0.1", port=7112)
