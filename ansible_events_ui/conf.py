from environs import Env

env = Env()

# Reads .env file
env.read_env()


class _Settings:
    def __init__(self):
        self.SECRET = env.str("SECRET", default="secret")


settings = _Settings()
