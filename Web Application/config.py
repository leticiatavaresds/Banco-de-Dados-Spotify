import yaml

with open("config.yaml") as file:
    _config = yaml.load(file, Loader=yaml.FullLoader)

_database_conf = _config.get("database", {})

DATABASE_NAME = _database_conf.get("name")
DATABASE_USER = _database_conf.get("username")
DATABASE_PASSWORD = _database_conf.get("password")
DATABASE_HOST = _database_conf.get("host", "localhost")
DATABASE_PORT = _database_conf.get("port", 3306)

DEGUB = _config.get("debug", False)
