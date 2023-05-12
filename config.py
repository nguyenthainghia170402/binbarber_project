# config.py

class Config(object):
    """
    Cấu hình chung
    """

    # Đưa các config env vào đây


class DevelopmentConfig(Config):
    """
    Cấu hình môi trường development
    """

    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """
    Cấu hình môi trường production
    """

    DEBUG = False

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
