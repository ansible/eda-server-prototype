import os


class _Settings:
    def __init__(self):
        self.SECRET = "SECRET"
        self.load_env()

    def load_env(self):
        if os.path.exists(".env"):
            with open(".env") as f:
                for line in f.readlines():
                    key, _, value = line.partition("=")
                    setattr(self, key, value.strip())


settings = _Settings()
