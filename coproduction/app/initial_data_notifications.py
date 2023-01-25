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

    listlanguagesfolders=os.listdir(rootdir)
    for languagefolder in listlanguagesfolders:
        rootdirlanguage='/app/notification-data/'+languagefolder

        for root, dirs, files in os.walk(rootdirlanguage):
            for name in files:
                if name.endswith((".json")):

                    full_path = os.path.join(root, name)
        
                    # Opening JSON file
                    f = open(full_path)
                    # returns JSON object as 
                    dataNotification = json.load(f)

                    #Get all data of the file:
                    event=dataNotification['event']

                    if "event" in dataNotification:
                        event=dataNotification['event']
                    else:
                        #Skip this loop run
                        continue
                
                    if "title" in dataNotification:
                        title=dataNotification['title']
                    else:
                        title=''
                    
                    if "subtitle" in dataNotification:
                        subtitle=dataNotification['subtitle']
                    else:
                        subtitle=''

                    if "text" in dataNotification:
                        text=dataNotification['text']
                    else:
                        text=''
                
                
                    if "url_link" in dataNotification:
                        url_link=dataNotification['url_link']
                    else:
                        url_link='/'
                    
                    if "html_template" in dataNotification:
                        html_template=dataNotification['html_template']
                    else:
                        html_template=''
                    

                    if "icon" in dataNotification:
                        icon=dataNotification['icon']
                    else:
                        icon=''

                    if "language" in dataNotification:
                        language=dataNotification['language']
                    else:
                        language=''
                    
                    print(event)
                    
                    #Verify if exists:
                    postgres_select_query = "SELECT count(*) from notification WHERE event='"+event+"' and language='"+language+"'" 
                    cursor.execute(postgres_select_query)
                    filasEncontradas=cursor.fetchone()[0]
                    
                    if(filasEncontradas==0):
                        print('L> Create')
                        #Creo
                        newId = str(uuid.uuid4())
                        postgres_insert_query = """ INSERT INTO notification (ID,EVENT, TITLE, SUBTITLE,TEXT,HTML_TEMPLATE,URL_LINK,ICON,LANGUAGE) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                        record_to_insert = (newId,event,title,subtitle,text,html_template,url_link,icon,language)
                        cursor.execute(postgres_insert_query, record_to_insert)
                        connection.commit()

                    else:
                        print('L> Update')
                        #Actualizo
                        dt = datetime.now(timezone.utc)
                        postgres_update_query = """UPDATE notification SET title=%s, subtitle=%s, text=%s, html_template=%s,url_link=%s,icon=%s,language=%s,updated_at=%s where event=%s"""
                        record_to_update = (title, subtitle, text,html_template,url_link,icon,language,dt,event)
                        
                        cursor.execute(postgres_update_query, record_to_update)
                        connection.commit()

        #For delete a row:
        #DELETE FROM notification WHERE id = '310cecb7-d285-4ab6-bd83-425cd6ebea7b';

        print( "Finish create and update all Notification in "+languagefolder+".")


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


    