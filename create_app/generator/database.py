def resolve_database_dependencies(database_choice):
    """
    🗄️  Maps database selections to their required Python packages.
    Returns a formatted string of dependencies for requirements.txt.
    """

    # 🔗 Dependency Matrix
    database_map = {
        "None": "",
        
        "SQLite": "sqlalchemy",
        
        "PostgreSQL": "sqlalchemy\npsycopg2-binary",
        
        "MySQL": "sqlalchemy\npymysql",
        
        "MongoDB": "pymongo",
        
        "Redis": "redis" # ⚡ Added for caching support
    }

    # 🎯 Return the matching driver or an empty string if not found
    return database_map.get(database_choice, "")