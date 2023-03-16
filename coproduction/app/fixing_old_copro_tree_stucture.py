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

def fixInconsistencies(connection=None):
    #Establish the first time connection if dont exist
    if not connection:
        connection = psycopg2.connect(user=username,
                                    password=password,
                                    host=postgres_server,
                                    port="5432",
                                    database=postgres_db)

    cursor = connection.cursor()

    #Fix coproduction tree references:

    #Obtain all parents nodes with multiple dependants (inconsistences)

    query_inconsistent_parents = "SELECT treeitem_b_id, COUNT(*) AS Count FROM treeitem_prerequisites GROUP BY  treeitem_b_id HAVING COUNT(*) > 1;" 
    
    #Obtain the number of results:
    cursor.execute(query_inconsistent_parents)
    numeroIconsistencias=len(cursor.fetchall())

    if numeroIconsistencias==0:
        print('No se encuentra ninguna inconsistencia')
        return numeroIconsistencias

    
    
    #Again do the query to loop the results:
    print(query_inconsistent_parents)
    cursor = connection.cursor()
    cursor.execute(query_inconsistent_parents)
    

    while True:

        try:
            itemInconsistencia = cursor.fetchone()        
        except (Exception, psycopg2.Error) as error:
            itemInconsistencia=None
        
        
        
        if not itemInconsistencia:
            break
        print("Found an inconsistenci in:"+' '.join([str(elem) for elem in itemInconsistencia]))
        print("")
        original_parent_Id=itemInconsistencia[0]


        #Now I found all childrens of the parents found
        query_children = "SELECT treeitem_a_id FROM treeitem_prerequisites where treeitem_b_id='"+original_parent_Id+"';" 
        print(query_children)

        #Obtain the number of results:
        cursor = connection.cursor()
        cursor.execute(query_children)
        numberofSons=len(cursor.fetchall())
        print("El numero de hijos encontrados son:"+str(numberofSons))
        print('')

        if (numberofSons>0 ):
            cursor = connection.cursor()
            cursor.execute(query_children)

            #Recorro cada hijo y actualizo su padre con el hijo anterior
            id_previous_son=None
            while True:
                try:
                    item_son = cursor.fetchone()
                except (Exception, psycopg2.Error) as error:
                    item_son=None
                

                if not item_son:
                    break
                #print("Los hijos son:"+' '.join([str(elem) for elem in item_son]))
                son_id=item_son[0]
                print("El hijo es:"+son_id)

                if (id_previous_son):
                    #Update the child parent
                    update_parent="UPDATE treeitem_prerequisites SET treeitem_b_id='"+id_previous_son+"' WHERE treeitem_a_id='"+son_id+"' AND treeitem_b_id='"+original_parent_Id+"';"
                    print(update_parent)
                    postgres_update_query = """UPDATE treeitem_prerequisites SET treeitem_b_id=%s WHERE treeitem_a_id=%s AND treeitem_b_id=%s """
                    record_to_update = (id_previous_son, son_id, original_parent_Id)
                    cursor.execute(postgres_update_query, record_to_update)
                    connection.commit()

                #set the previos son id
                id_previous_son=son_id


    #Compruebo que no existan mas inconsistencias:
    cursor = connection.cursor()
    cursor.execute(query_inconsistent_parents)
    numeroIconsistencias=len(cursor.fetchall())

    if(numeroIconsistencias>0):
        print('Aun se han encontrado inconsistencias'+str(numeroIconsistencias))
        #Comienzo nuevamente el proceso:
        fixInconsistencies(connection)


    #Close the db connection:
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

#Start the excecution
try:
    fixInconsistencies()

except (Exception, psycopg2.Error) as error:
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
