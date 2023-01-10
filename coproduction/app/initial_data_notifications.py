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

try:
    connection = psycopg2.connect(user=username,
                                  password=password,
                                  host=postgres_server,
                                  port="5432",
                                  database=postgres_db)
    cursor = connection.cursor()

    #Get data from folders:
    rootdir='/app/notification-data'
    for root, dirs, files in os.walk(rootdir):
        for name in files:
            if name.endswith((".json")):

                full_path = os.path.join(root, name)
                #print(full_path)
    
                # Opening JSON file
                f = open(full_path)
                # returns JSON object as 
                dataNotification = json.load(f)

                #Get all data of the file:
                event=dataNotification['event']
                title=dataNotification['title']
                subtitle=dataNotification['subtitle']
                text=dataNotification['text']
                html_template=dataNotification['html_template']
                url_link=dataNotification['url_link']

                #Verify if exists:
                postgres_select_query = "SELECT count(*) from notification WHERE event='"+event+"'"

                cursor.execute(postgres_select_query)
                filasEncontradas=cursor.fetchone()[0]
                
                if(filasEncontradas==0):
                    #Creo
                    newId = str(uuid.uuid4())
                    postgres_insert_query = """ INSERT INTO notification (ID,EVENT, TITLE, SUBTITLE,TEXT,HTML_TEMPLATE,URL_LINK) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
                    record_to_insert = (newId,event,title,subtitle,text,html_template,url_link)
                    cursor.execute(postgres_insert_query, record_to_insert)
                    connection.commit()

                else:
                    #Actualizo
                    dt = datetime.now(timezone.utc)
                    postgres_update_query = """UPDATE notification SET title=%s, subtitle=%s, text=%s, html_template=%s,url_link=%s,updated_at=%s where event=%s"""
                    record_to_update = (title, subtitle, text,html_template,url_link,dt,event)
                    cursor.execute(postgres_update_query, record_to_update)
                    connection.commit()

    #For delete a row:
    #DELETE FROM notification WHERE id = '310cecb7-d285-4ab6-bd83-425cd6ebea7b';

    print( "All Record Notification were inserted successfully into notification table")


    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

except (Exception, psycopg2.Error) as error:
    print("Failed to insert record into notification table", error)
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")


    