import psycopg2
import os
import json
from datetime import datetime, timezone
import uuid
                    
#Get the environment variables:
username = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "")
postgres_server = os.getenv("POSTGRES_SERVER", "db")
postgres_db = os.getenv("POSTGRES_DB", "app")
connection = psycopg2.connect(user=username,
                                  password=password,
                                  host=postgres_server,
                                  port="5432",
                                  database=postgres_db)
cursor = connection.cursor()
postgres_select_query = "DELETE from coproductionprocessnotification"
cursor.execute(postgres_select_query)
connection.commit()
cursor.close()
connection.close()