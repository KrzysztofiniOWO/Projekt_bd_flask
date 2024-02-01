class Config:
    MYSQL_DATABASE_HOST = 'localhost'
    MYSQL_DATABASE_USER = 'root'
    MYSQL_DATABASE_PASSWORD = 'root'
    MYSQL_DATABASE_DB = 'kebAPPka'
    MYSQL_DATABASE_PORT = 3306
    SECRET_KEY = 'bardzo_tajny_klucz'
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    CODE_EXPIRY_MINUTES = 30
    LINK_EXPIRY_MINUTES = 60
    BASE_URL = 'http://localhost:5000'