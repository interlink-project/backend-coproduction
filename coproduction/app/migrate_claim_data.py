import psycopg2
import os
import json
from datetime import datetime, timezone

# Get the environment variables:
username = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "changethis")
postgres_server = os.getenv("POSTGRES_SERVER", "localhost")
postgres_db = os.getenv("POSTGRES_DB", "coproduction")

def create_connection():
    try:
        connection = psycopg2.connect(
            user=username,
            password=password,
            host=postgres_server,
            port="5432",
            database=postgres_db
        )
        print("Connected to the database.")
        return connection
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def migrate_data_claims(connection):
    total_inserted_rows = 0

    cursor = connection.cursor()

    # Delete all previous claims from the table:
    query_delete_claims = "DELETE FROM claim;"
    cursor.execute(query_delete_claims)
    print("Deleted previous claims.")

    # Obtain all parent nodes with multiple dependents (inconsistencies):
    query_coproductionprocessnotification = """
        SELECT id, coproductionprocess_id, asset_id, user_id, parameters, created_at
        FROM coproductionprocessnotification
        WHERE claim_type='development';
    """
    cursor.execute(query_coproductionprocessnotification)
    rows = cursor.fetchall()

    for row in rows:
        id,coproductionprocess_id, asset_id, user_id, parameters, created_at = row
       
        parameters_dict = json.loads(parameters)
    
        assetId = parameters_dict.get('assetId')
        commentTitle = parameters_dict.get('commentTitle')
        commentDescription = parameters_dict.get('commentDescription')
        treeitem_id = parameters_dict.get('treeitem_id')
        
        print(f'coproductionprocess_id: {coproductionprocess_id}, asset_id: {asset_id}, user_id: {user_id}, assetId: {assetId}, task_id: {treeitem_id}, created_at {created_at}, commentTitle: {commentTitle}')

        # Insert the new claim
        query_insert_claim = """
            INSERT INTO claim (id, user_id, asset_id, task_id, coproductionprocess_id, title, description, state, claim_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON CONFLICT (id) DO NOTHING RETURNING id;
        """
        values = (id,user_id, asset_id, treeitem_id, coproductionprocess_id, commentTitle, commentDescription, False, 'development')
        
        try:
            cursor.execute(query_insert_claim, values)
            result = cursor.fetchone()

            if result is not None:
                claim_id = result[0]

                # Update the created_at field
                query_update_claim = "UPDATE claim SET created_at = %s WHERE id = %s;"
                values = (created_at, claim_id)
                cursor.execute(query_update_claim, values)
                connection.commit()  # Commit the transaction
                
                total_inserted_rows += 1
                print(f'Claim inserted: claim_id: {claim_id} created_at: {created_at}')
            else:
                print(f'A row with id {id} already exists.')

        except psycopg2.errors.ForeignKeyViolation as e:
            # Handle the foreign key constraint violation here
            print(f'Foreign key constraint violation: {e}')
            
            # Print the constraint name
            constraint_name = e.diag.constraint_name
            print(f'Constraint name: {constraint_name}')
            
            # Print the values that caused the violation
            violated_values = e.diag.violation_column_values
            print(f'Violated values: {violated_values}')
            
            # You can choose to log the error or take other actions as needed.

    print(f'Total inserted rows: {total_inserted_rows}')

def main():
    connection = create_connection()
    if connection:
        try:
            migrate_data_claims(connection)
        finally:
            connection.close()

if __name__ == "__main__":
    main()
