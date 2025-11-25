try:
    import flask
    import flask_jwt_extended
    import pandas
    import openpyxl
    import bcrypt
    import psycopg2
    import flask_sqlalchemy
    import flask_bcrypt
    print("All imports successful")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
