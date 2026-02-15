def resolve_database_dependencies(database_choice):

    database_map = {

        "None": "",

        "SQLite": "sqlalchemy",

        "PostgreSQL": "sqlalchemy\npsycopg2-binary",

        "MySQL": "sqlalchemy\npymysql",

        "MongoDB": "pymongo",
    }

    return database_map.get(database_choice, "")
