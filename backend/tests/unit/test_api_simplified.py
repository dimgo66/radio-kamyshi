"""
Упрощенные тесты для API эндпоинтов
"""
import pytest
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, relationship, declarative_base
from datetime import timedelta

# Создаем базовый класс модели
Base = declarative_base()

# Модели
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

# Создаем тестовую базу данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базу и таблицы для тестов
Base.metadata.create_all(bind=engine)

# Зависимость для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функции безопасности
def get_password_hash(password: str) -> str:
    """Заглушка для хеширования пароля"""
    return f"hashed_{password}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Заглушка для проверки пароля"""
    return hashed_password == f"hashed_{plain_password}"

def create_access_token(data: dict) -> str:
    """Заглушка для создания токена"""
    return f"token_for_{data['sub']}"

# Создаем приложение
app = FastAPI()

# Эндпоинты
@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в API Радио Камыши!"}

# Схемы
from pydantic import BaseModel, EmailStr, field_validator

class UserBase(BaseModel):
    email: EmailStr
    username: str
    is_active: bool = True
    is_superuser: bool = False
    first_name: str | None = None
    last_name: str | None = None

class UserCreate(UserBase):
    password: str
    
    @field_validator("password")
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        return v

class UserDB(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# CRUD операции
def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        print(f"User with email {email} not found")
        return False
    
    # Для отладки
    print(f"Authenticating user: {email}")
    print(f"Received password: {password}")
    print(f"Stored hash: {user.hashed_password}")
    print(f"Expected hash: hashed_{password}")
    
    if not verify_password(password, str(user.hashed_password)):
        print(f"Password verification failed")
        return False
    
    print(f"Authentication successful")
    return user

# Зависимости
from fastapi.security import OAuth2PasswordBearer
from fastapi import Security

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(db: Session = Depends(get_db), token: str = Security(oauth2_scheme)):
    # Заглушка: просто извлекаем email из токена
    email = token.replace("token_for_", "")
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Неактивный пользователь")
    return current_user

def get_current_active_superuser(current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав доступа",
        )
    return current_user

# Маршруты
from fastapi.security import OAuth2PasswordRequestForm

@app.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserDB)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.post("/users/", response_model=UserDB)
def create_new_user(user: UserCreate, db: Session = Depends(get_db), 
                   current_user: User = Depends(get_current_active_superuser)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    return create_user(db=db, user=user)

@app.get("/users/", response_model=list[UserDB])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), 
              current_user: User = Depends(get_current_active_superuser)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# Тесты
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def admin_user(db):
    # Проверяем, существует ли пользователь
    admin = get_user_by_email(db, "admin@example.com")
    if not admin:
        # Создаем пользователя-админа
        admin_data = UserCreate(
            email="admin@example.com",
            username="admin",
            password="adminpass",  # Это будет "hashed_adminpass"
            is_active=True,
            is_superuser=True
        )
        admin = create_user(db, admin_data)
    
    # Для отладки
    print(f"Admin user created/found: {admin.email}, password hash: {admin.hashed_password}")
    return admin

@pytest.fixture
def normal_user(db):
    # Проверяем, существует ли пользователь
    user = get_user_by_email(db, "user@example.com")
    if not user:
        # Создаем обычного пользователя
        user_data = UserCreate(
            email="user@example.com",
            username="normaluser",
            password="userpassword",  # Минимум 8 символов
            is_active=True,
            is_superuser=False
        )
        user = create_user(db, user_data)
    return user

def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Добро пожаловать в API Радио Камыши!" == data["message"]

def test_login(client, admin_user):
    response = client.post(
        "/login",
        data={"username": "admin@example.com", "password": "adminpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"] == "token_for_admin@example.com"

def test_read_users_me(client, admin_user):
    # Сначала получаем токен
    token = "token_for_admin@example.com"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@example.com"
    assert data["is_superuser"] is True

def test_create_user(client, admin_user):
    # Сначала получаем токен
    token = "token_for_admin@example.com"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Создаем нового пользователя с уникальным email
    import random
    random_suffix = random.randint(1000, 9999)
    
    user_data = {
        "email": f"newuser{random_suffix}@example.com",
        "username": f"newuser{random_suffix}",
        "password": "newuserpassword",  # Минимум 8 символов
        "is_active": True,
        "is_superuser": False,
        "first_name": "New",
        "last_name": "User"
    }
    
    response = client.post("/users/", headers=headers, json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == f"newuser{random_suffix}@example.com"
    assert data["username"] == f"newuser{random_suffix}"
    assert "id" in data
    
    # Тестируем валидацию пароля
    short_password_data = {
        "email": f"short{random_suffix}@example.com",
        "username": f"short{random_suffix}",
        "password": "short",  # Слишком короткий пароль
        "is_active": True
    }
    
    response = client.post("/users/", headers=headers, json=short_password_data)
    assert response.status_code == 422  # Validation error

def test_normal_user_cant_create_user(client, normal_user):
    # Токен для обычного пользователя
    token = "token_for_user@example.com"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Попытка создать нового пользователя
    user_data = {
        "email": "anotheruser@example.com",
        "username": "anotheruser",
        "password": "anotherpassword",  # Минимум 8 символов
        "is_active": True
    }
    
    response = client.post("/users/", headers=headers, json=user_data)
    assert response.status_code == 403  # Forbidden 