from app.utils.security import verify_password
from sqlalchemy.orm import Session
from app.utils.jwt_handler import create_access_token
from app.utils.security import hash_password
from app.database import SessionLocal
from app.models import User

class AuthService:

    def register(self, name: str, email: str, password: str):

        db = SessionLocal()

        user = User(
            name=name,
            email=email,
            password=hash_password(password)
        )

        db.add(user)
        db.commit()
        db.close()

        return "User Registered Successfully"
    

    def login(self, email: str, password: str):

        db = SessionLocal()

        user = db.query(User).filter(User.email == email).first()

        if not user:
            db.close()
            raise Exception("User not found")

        if not verify_password(password, user.password):
            db.close()
            raise Exception("Invalid password")

        token = create_access_token(
            {
                "email": user.email
            }
        )

        db.close()

        return token