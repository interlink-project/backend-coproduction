from locale import strcoll
import os
import uuid
from typing import Any, Dict, List, Optional
from fastapi_pagination import Page
from fastapi.responses import StreamingResponse, JSONResponse

import aiofiles
import requests
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.general import deps
from app.sockets import socket_manager 
from app.locales import get_language
from app.general.emails import send_email
from fastapi.responses import FileResponse
from app.models import UserNotification
from app.models import ParticipationRequest
import os
import zipfile
import json
import html
import datetime as dt
import shutil
from pathlib import Path
import requests
from urllib.parse import unquote
import re
from datetime import datetime
from uuid import UUID

import logging
from fastapi import BackgroundTasks
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("", response_model=List[schemas.CoproductionProcessOutFull])
async def list_coproductionprocesses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
    search: str = Query(None)
) -> Any:
    """
    Retrieve coproductionprocesses.
    """
    if not crud.coproductionprocess.can_list(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.coproductionprocess.get_multi_by_user(db, user=current_user, search=search)

@router.get("/public", response_model=Page[Any])
async def list_coproductionprocesses(
    db: Session = Depends(deps.get_db),
    rating: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    tag: Optional[List[str]] = Query(None),
    skip: int = 0,
    limit: int = 100,
    language: str = Depends(get_language)

) -> Any:
    """
    Retrieve Public Coproduction Processes.
    """
    # print("search", search)
    # print("rating", rating)
    # print("tag", tag)
    # if not crud.coproductionprocess.can_list(current_user):
    #     raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.coproductionprocess.get_multi_public(db, search=search,  rating=rating,  language=language, tag=tag)


@router.post("", response_model=schemas.CoproductionProcessOutFull)
async def create_coproductionprocess(
    *,
    db: Session = Depends(deps.get_db),
    coproductionprocess_in: schemas.CoproductionProcessCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new coproductionprocess.
    """
    if not crud.coproductionprocess.can_create(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.coproductionprocess.create(db=db, obj_in=coproductionprocess_in, creator=current_user, set_creator_admin=True)


@router.post("/{id}/logotype", response_model=schemas.CoproductionProcessOutFull)
async def set_logotype(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    file: UploadFile = File(...),
) -> Any:
    if (coproductionprocess := await crud.coproductionprocess.get(db=db, id=id)):
        if crud.coproductionprocess.can_update(user=current_user, object=coproductionprocess):
            filename, extension = os.path.splitext(file.filename)
            out_file_path = f"/static/coproductionprocesses/{coproductionprocess.id}{extension}"

            async with aiofiles.open("/app" + out_file_path, 'wb') as out_file:
                content = await file.read()  # async read
                await out_file.write(content)  # async write
            return await crud.coproductionprocess.update(db=db, db_obj=coproductionprocess, obj_in=schemas.CoproductionProcessPatch(logotype=out_file_path))
        raise HTTPException(
            status_code=403, detail="You are not allowed to update this coproductionprocess")
    raise HTTPException(status_code=404, detail="Coproduction process not found")


@router.post("/{id}/set_schema", response_model=schemas.CoproductionProcessOutFull)
async def set_schema(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    schema: dict,
) -> Any:
    if (coproductionprocess := await crud.coproductionprocess.get(db=db, id=id)):
        if crud.coproductionprocess.can_update(current_user, coproductionprocess):
            return await crud.coproductionprocess.set_schema(db=db, coproductionschema=schema, coproductionprocess=coproductionprocess)
        raise HTTPException(
            status_code=404, detail="You do not have permissions to update the coproductionprocess")
    raise HTTPException(status_code=404, detail="Coproduction process not found")


@router.post("/{id}/clear_schema", response_model=schemas.CoproductionProcessOutFull)
async def clear_schema(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    if (coproductionprocess := await crud.coproductionprocess.get(db=db, id=id)):
        if crud.coproductionprocess.can_update(current_user, coproductionprocess):
            return await crud.coproductionprocess.clear_schema(db=db, coproductionprocess=coproductionprocess)
        raise HTTPException(
            status_code=404, detail="You do not have permissions to update the coproductionprocess")
    raise HTTPException(status_code=404, detail="Coproduction process not found")



class TeamIn(BaseModel):
    team_id: uuid.UUID


@router.post("/{id}/add_team")
async def add_team(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    team_in: TeamIn,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add team to coproductionprocess (with async default role)
    """
    if coproductionprocess := await crud.coproductionprocess.get(db=db, id=id):
        if team := await crud.team.get(db=db, id=team_in.team_id):
            await crud.coproductionprocess.add_team(
                db=db, coproductionprocess=coproductionprocess, team=team)
            return True
        raise HTTPException(status_code=400, detail="Team not found")
    raise HTTPException(status_code=404, detail="Coproductionprocess not found")

@router.post("/{id}/add_user")
async def add_user(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    user_in: schemas.UserIn,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add user to coproductionprocess (with async default role)
    """
    if coproductionprocess := await crud.coproductionprocess.get(db=db, id=id):
        if user := await crud.user.get(db=db, id=user_in.user_id):
            await crud.coproductionprocess.add_user(
                db=db, coproductionprocess=coproductionprocess, user=user)
            return True
        raise HTTPException(status_code=400, detail="User not found")
    raise HTTPException(status_code=404, detail="Coproductionprocess not found")


@router.put("/{id}", response_model=schemas.CoproductionProcessOutFull)
async def update_coproductionprocess(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    coproductionprocess_in: schemas.CoproductionProcessPatch,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an coproductionprocess.
    """
    
    coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    if not crud.coproductionprocess.can_update(user=current_user, object=coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if coproductionprocess_in.tags:
        tmp_tags = []
        for tag in coproductionprocess_in.tags:
            t = await crud.tag.get(db=db, id=tag['id'])
            tmp_tags.append(t)
        coproductionprocess_in.tags = tmp_tags
        print(coproductionprocess_in.tags)
    return await crud.coproductionprocess.update(
        db=db, db_obj=coproductionprocess, obj_in=coproductionprocess_in)


@router.get("/{id}", response_model=schemas.CoproductionProcessOutFull)
async def read_coproductionprocess(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get coproductionprocess by ID.
    """
    coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    if not crud.coproductionprocess.can_read(db=db, user=current_user, object=coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return coproductionprocess

@router.get("/public/{id}", response_model=schemas.CoproductionPublicProcessOutFull)
async def read_public_coproductionprocess(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID
) -> Any:
    """
    Get coproductionprocess by ID.
    """
    coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    return coproductionprocess

@router.get("/{id}/catalogue", response_model=schemas.CoproductionProcessOutFull)
async def read_coproductionprocess_catalogue(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get coproductionprocess by ID.
    """
    coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
   
    return coproductionprocess


@router.delete("/{id}")
async def delete_coproductionprocess(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an coproductionprocess.
    """
    coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)

    # If the coproductionprocess is part of a publication it most delete the story first.
    if (coproductionprocess.is_part_of_publication):
        #Delete the story
        story = await crud.story.get_stories_bycopro_catalogue(db=db, coproductionprocess_cloneforpub_id=id,user=current_user)
        if(story):
            await crud.story.remove(db=db, id=story.id)
        
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    if not crud.coproductionprocess.can_remove(user=current_user, object=coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    #Delete all user notification related with this coproduction process
    listUserNotifications=await crud.usernotification.get_user_notifications_by_coproid(db=db,copro_id=id)
    for usernotification in listUserNotifications:
        await crud.usernotification.remove(db=db,id=usernotification.id)

    await crud.coproductionprocess.remove(db=db, id=id)
    return None


# specific

@router.get("/{id}/tree", response_model=Optional[List[schemas.PhaseOutFull]])
async def get_coproductionprocess_tree(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get coproductionprocess tree.
    """
    coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    if not crud.coproductionprocess.can_read(db=db, user=current_user, object=coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return coproductionprocess.children



# Order the phases by the order of the tasks
def topological_sort(tasks):
    visited = set()
    stack = []
    mapping = {task.name: task for task in tasks}

    def visit(task):
        if task.name not in visited:
            visited.add(task.name)
            for prereq_name in task.prerequisites:
                if prereq_name.name in mapping:
                    visit(mapping[prereq_name.name])
            stack.append(task)

    # Visit tasks without prerequisites first
    for task in tasks:
        if not task.prerequisites:
            visit(task)

    # Then visit the rest
    for task in tasks:
        if task.name not in visited:
            visit(task)

    return stack

def sanitize_filename(filename, replacement="_"):
    """
    Sanitize a filename by removing or replacing characters that are not valid 
    or safe in filenames across major operating systems.

    Args:
    - filename (str): The original filename.
    - replacement (str): The character to replace invalid characters with. Default is underscore.

    Returns:
    - str: The sanitized filename.
    """

    # Split filename and extension
    if "." in filename:
        name, ext = filename.rsplit(".", 1)
        ext = "." + ext
    else:
        name = filename
        ext = ""

    # Remove or replace characters that are unsafe for filenames
    # This regex aims at capturing most problematic characters in filenames across major OS
    name = re.sub(r'[<>:"/\\|?*]', replacement, name)
    
    # Remove leading and trailing periods, spaces, and hyphens
    name = name.strip(". -")

    # Ensure the filename doesn't use any reserved names (CON, PRN, AUX, etc.)
    # irrespective of its extension (e.g., CON.txt is invalid on Windows)
    reserved_names = ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4","COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3","LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"]
    
    if name.upper() in reserved_names:
        name = replacement + name
    
    return name + ext

#Download the asset into the assets folder
def downloadAsset(asset,dirpath,token):

    #print("The asset type: "+str(asset.type))
    if asset.type=="internalasset":
        #print("The info del internal asset: "+json.dumps(asset.internalData))

        asset_id = asset.internalData['id']  
        asset_name= asset.internalData['name']   
        icon=asset.internalData['icon']   

        # print('AssetId:'+asset_id)
        # print('AssetName:'+asset_name)
        #print('AssetIcon:'+icon)

        # Replace 'http://localhost:8000' with your actual API base URL and 'YOUR_ASSET_ID' with the actual asset ID
        url = f'http://googledrive:80/assets/{asset_id}/download'

        # Specify the directory where you want to save the file
        directory_assetPath = dirpath+'/assets'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Authorization': token
        }


        # Configuración para el número máximo de intentos de reintento
        max_retries = 10
        for attempt in range(max_retries):
            try:
                # Intenta hacer una solicitud GET con un tiempo de espera (timeout) de 10 segundos
                time.sleep(2) 
                response = requests.get(url, headers=headers, allow_redirects=True, timeout=30)
                response.raise_for_status()

                # Comprueba si la solicitud fue exitosa
                if response.status_code == 200:

                    # Intenta extraer el nombre del archivo del encabezado Content-Disposition
                    content_disposition = response.headers.get('Content-Disposition')
                    if content_disposition:

                        # Usa una expresión regular para encontrar el nombre del archivo
                        match = re.search(r'filename\*?="([^"]+)', content_disposition)
                        if match:
                            filename = match.group(1)
                            # print('Filename: ' + filename)
                        else:
                            print('No filename found')

                    else:
                        filename = asset_name  # Usa un nombre predeterminado si no se encuentra el encabezado

                    # Crea el directorio Asset si no existe
                    if not os.path.exists(directory_assetPath):
                        os.makedirs(directory_assetPath)

                    filename = sanitize_filename(filename=filename)
                    file_path = os.path.join(directory_assetPath, str(asset.id) + "." + filename)

                    # Guarda el contenido de la respuesta en un archivo
                    with open(file_path, 'wb') as file:
                        file.write(response.content)
                    print(f"Downloaded at {file_path}")
                    break
            except requests.exceptions.HTTPError as http_err:
                print(f"Request http error.. ({attempt + 1}/{max_retries})")
                time.sleep(5)  # Espera 4 segundos antes de reintentar

            except Exception as err:
                print(f"An error occurred: {err}")
                print(f"Exception when downloading error.. ({attempt + 1}/{max_retries})")
                time.sleep(5)  # Espera 4 segundos antes de reintentar

            

    #print(asset)


def datetime_serializer(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError("Type not serializable")


def sanitize_filename(filename):
    # Replace spaces with underscores
    sanitized = filename.replace(" ", "_")
    # Remove any other disallowed characters
    # This is a simple example; you might need to add more characters based on your needs
    disallowed_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in disallowed_characters:
        sanitized = sanitized.replace(char, '')
    return sanitized

#Method to get the last zip file info and content:

@router.get("/{id}/last_created_zip")
async def last_created_zip(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
    token: str = Depends(deps.get_current_active_token)
):
    try:
        coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)
    except Exception as e:
        logger.error(f"Error fetching coproduction process: {e}")
        return {"error": "Error fetching coproduction process"}
    
    zip_directory = 'zipfiles'

    if not os.path.exists(zip_directory):
        os.makedirs(zip_directory)

    files = [f for f in os.listdir(zip_directory) if f.startswith(str(id)) and f.endswith('.zip')]

    def extract_datetime_from_filename(filename):
        parts = filename.split('_')
        return parts[1] + "_" + parts[2]

    files.sort(key=extract_datetime_from_filename, reverse=True)

    # If there's no file, return a meaningful error response
    if not files:
        return JSONResponse(content={"error": "No file found"}, status_code=404)

    # Get the datetime from the filename
    datetime_from_filename = extract_datetime_from_filename(files[0]).replace('.zip','')

    # Prepare the path of the file to stream back
    file_path = os.path.join(zip_directory, files[0])

    # Sanitize the process name for the filename
    sanitized_name = sanitize_filename(coproductionprocess.name)

    # Return the file as a stream with the appropriate headers
    return StreamingResponse(
        open(file_path, 'rb'), 
        media_type="application/octet-stream", 
        headers={
            'Content-Disposition': f'attachment; filename="{sanitized_name}.zip"',
            'X-File-Creation-Datetime': datetime_from_filename  # This line adds the datetime to the headers
        }
    )


#Download the coproduction process in a zip file:

@router.get("/{id}/download")
async def download_zip(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
    token: str = Depends(deps.get_current_active_token),
    background_tasks: BackgroundTasks
):
    # logger.info("Start the download Process:")
    try:
        coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)
    except Exception as e:
        logger.error(f"Error fetching coproduction process: {e}")
        return {"error": "Error fetching coproduction process"}

    # Define the directory name
    try:
        # Define the directory name and create it if doesn't exist
        dir_root = 'processes_exported'
        dir_name = os.path.join(dir_root, coproductionprocess.name.replace(' ', '_'))

        os.makedirs(dir_name, exist_ok=True)
    except Exception as e:
        logger.error(f"Error creating directory: {e}")
        return {"error": "Error creating directory"}
    
    try:

        #Phases:
        #Order the phases using the topological sort:
        ordered_phases = topological_sort(coproductionprocess.children)
        phase_dict_list = [phase.to_dict() for phase in ordered_phases]

        cont_phases=0
        for phase in ordered_phases:

            print('Enter phase:')
            #print(phase)

            ordered_objectives=topological_sort(phase.children)
            objectives_dict_list = [obj.to_dict() for obj in ordered_objectives]
            phase_dict_list[cont_phases]["objectives"]=objectives_dict_list
            
            cont_objectives=0
            for objective in ordered_objectives:
    
                ordered_tasks=topological_sort(objective.children)
                tasks_dict_list = [task.to_dict() for task in ordered_tasks]
                phase_dict_list[cont_phases]["objectives"][cont_objectives]["tasks"]=tasks_dict_list

                cont_tasks=0
                for task in ordered_tasks:
                    assets=await crud.asset.get_multi_withIntData(db, task=task, token=token)
                    
                    assets_dict_list=[]
                    cont_assets=0
                    for asset in assets:
                        
                        #print("The asset type: "+str(asset.type))
                        try:
                            downloadAsset(asset=asset,dirpath=dir_name,token=token)
                            assets_dict_list.append(asset.dict())
                        except Exception as e:  
                            logger.error(f"Error while trying to download the asset: {asset.dict()}")
                        
                        cont_assets=cont_assets+1

                    
                    phase_dict_list[cont_phases]["objectives"][cont_objectives]["tasks"][cont_tasks]["assets"]=assets_dict_list

                    cont_tasks=cont_tasks+1


                cont_objectives=cont_objectives+1

            cont_phases=cont_phases+1
        #print(phase_dict_list)
    except Exception as e:
        logger.error(f"Error during phase ordering and processing: {e}")
        return {"error": "Error during phase ordering and processing"}

    try:

        phases_json = json.dumps(phase_dict_list, indent=2, default=datetime_serializer)
        #print(phases_json)

        # Now write the JSON string to a file in the new directory
        with open(os.path.join(dir_name, 'schema.json'), 'w') as f:
            f.write(phases_json)

    except Exception as e:
        logger.error(f"Error writing to schema.json: {e}")
        return {"error": "Error writing to schema.json"}
    

    try:
        # To do a process to download the process information in a file.
        # Convert the CoproductionProcess object to a dictionary
        coproduction_dict = coproductionprocess.to_dict()
        coproduction_dict['name']="import_"+coproduction_dict['name']

        # Specify the directory and filename
        directory = dir_name
        filename = "coproduction.json"

        # Create the full file path
        file_path = os.path.join(directory, filename)

        # Convert the dictionary to JSON
        json_data = json.dumps(coproduction_dict)

        # Write the JSON data to the specified file
        with open(file_path, "w") as json_file:
            json_file.write(json_data)
    except Exception as e:
        logger.error(f"Error writing to coproduction.json: {e}")
        return {"error": "Error writing to coproduction.json"}

    
    #Save the logotype file:
    try:
        import shutil

        # Specify the source file and the destination directory
        source_file = '/app'+coproductionprocess.logotype
        destination_directory = directory

        # Use shutil.copy() to copy the file
        shutil.copy(source_file, destination_directory)
    except Exception as e:
        logger.error(f"Error saving logotype file: {e}")
        return {"error": "Error saving logotype file"}


    try:

        # I need to create a json file with the coproduction process
        # specify your directory
        directory = dir_name

        # specify the directory where the zip file will be stored
        zip_directory = 'zipfiles'

        # Check if directory exists. If not, create it.
        if not os.path.exists(zip_directory):
            os.makedirs(zip_directory)

        # specify the name of your zip file
        from datetime import datetime

        # Get the current date and time
        now = datetime.now()

        # Format the date and time as a string (for example, in the format "YYYYMMDD_HHMMSS")
        formatted_date = now.strftime("%Y%m%d_%H%M%S")

        # Use the formatted date and time in the filename
        file_name = f"{coproductionprocess.id}_{formatted_date}.zip"

        # create the full zip file path
        zip_path = os.path.join(zip_directory, file_name)

        zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)

        # compress all files in the directory
        for root, dirs, files in os.walk(directory):
            for file in files:
                zipf.write(os.path.join(root, file))

        zipf.close()


        print("The zip file is: "+zip_path)

    except Exception as e:
        logger.error(f"Error creating zip file: {e}")
        return {"error": "Error creating zip file"}

    #Store the response
    try:
        response = FileResponse(zip_path, media_type='application/zip', filename=file_name)

        def remove_files():
            try:
                # List all files in dir_root with the specific ID
                # Assuming filename format is like: ID_DATETIME.zip
                files = [f for f in os.listdir(zip_directory) if f.startswith(str(coproductionprocess.id)) and f.endswith('.zip')]

                # Function to extract datetime from filename
                def extract_datetime_from_filename(filename):
                    # Split the filename into its ID and datetime components
                    parts = filename.split('_')
                    # Combine date and time parts and return
                    return parts[1] + "_" + parts[2]

                # Sort files based on datetime
                files.sort(key=extract_datetime_from_filename, reverse=True)

                # Delete all files except the first one (most recent after reverse sort)
                for file in files[1:]:
                    os.remove(os.path.join(zip_directory, file))
                #Borro Archivos temporales usados para la compression.
                shutil.rmtree(dir_root)
                
                logger.info(f"Successfully removed temporary files except the most recent one")
            except Exception as e:
                logger.error(f"Error removing temporary files: {e}")

        # Schedule the remove_files function to be run in the background
        background_tasks.add_task(remove_files)

        return response

    except Exception as e:
        logger.error(f"Error creating file response: {e}")
        return {"error": "Error creating file response"}



def get_file_by_asset_id(asset_id, directory='assets'):
    try:
        # List all files in the directory
        files = os.listdir(directory)

        # Loop through all files
        for file in files:
            # Check if the file name starts with the asset ID
            if file.startswith(asset_id):
                # Return the full path of the file
                return os.path.join(directory, file)

        # If no file is found with the asset ID, return a message indicating this
        return "No file found with the specified asset ID."
    except Exception as e:
        # If there's an error (like the directory not existing), return the error message
        return str(e)


from pathlib import Path

def get_modified_file_name(file_path):
    try:
        # Create a Path object
        path = Path(file_path)
        
        # Get the file name
        file_name = path.name

        # Find the first dot in the file name
        first_dot_index = file_name.find('.')

        # If a dot is found, return the part of the file name after the first dot
        # Otherwise, return the entire file name
        if first_dot_index != -1:
            return file_name[first_dot_index+1:]
        else:
            return file_name
    except Exception as e:
        return str(e)

@router.post("/import")
async def import_file(
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
    token: str = Depends(deps.get_current_active_token)
    ):

    # ensure the uploads directory exists
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)


    temp_file = uploads_dir / file.filename
    with temp_file.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


     # get the creation time of the file
    timestamp = os.path.getctime(temp_file)
    creation_time = dt.datetime.fromtimestamp(timestamp)
    print("Creation Time:", creation_time)


    # format the creation_time as a string and concatenate with the file name
    creation_time_str = creation_time.strftime("%Y%m%d%H%M%S")
    filename_split=file.filename.split('.')
    unzipped_folder_name = f"{filename_split[0]}_{creation_time_str}.{filename_split[1]}"


    # unzip the file
    with zipfile.ZipFile(temp_file, 'r') as zip_ref:
        zip_ref.extractall(unzipped_folder_name)

    # remove the temp file
    temp_file.unlink()

    # list contents of the unzipped folder
    unzipped_folder = Path(unzipped_folder_name+"/processes_exported")

    
    #Get the process name:
    process_name=''
    for directory in unzipped_folder.iterdir():
        if directory.is_dir():
            process_name= directory.name

    #Get the process files:
    path_coproduction_file = Path(unzipped_folder_name+"/processes_exported/"+process_name+"/coproduction.json")
    logotypepath=''
    with open(path_coproduction_file, 'r') as f:
        coproduction_json = json.load(f)
        #print(coproduction_json)
        logotypepath=coproduction_json['logotype']

        #Need to Data transform:
        #Convert the string "None" to an actual None value for the rating
        if coproduction_json['rating'] == "None":
            coproduction_json['rating'] = None
        
        #Lets create the process!!
        process = schemas.CoproductionProcessCreate(**coproduction_json)
        created_process=await crud.coproductionprocess.create(db,obj_in=process,creator=current_user,set_creator_admin=current_user)

    #Copy the logo:

    file_name_logo = os.path.basename(logotypepath)
    path_logo_file = Path(unzipped_folder_name+"/processes_exported/"+process_name+"/"+file_name_logo)

 
    filename, extension = os.path.splitext(str(path_logo_file).split('/')[-1])
    in_file_path = path_logo_file
    out_file_path = f"/static/coproductionprocesses/{created_process.id}{extension}"
    #print("in_file_path", in_file_path)
    
    async with aiofiles.open(in_file_path, 'rb') as in_file:
        content = await in_file.read()
        #print("content", content)
        async with aiofiles.open("/app" + out_file_path, 'wb') as out_file:
            #print("out_file", out_file_path)
            await out_file.write(content) 
                # async write
    #print("PREUPDATE")
    await crud.coproductionprocess.set_logotype(db=db, coproductionprocess=created_process,logotype_path=out_file_path)


    #Get the schema files:
    path_schema_file = Path(unzipped_folder_name+"/processes_exported/"+process_name+"/schema.json")
    with open(path_schema_file, 'r') as f:
        schema_json = json.load(f)
        
        #Lets create the phase:
        prev_phase=None
        for phase_i in range(len(schema_json)):

            # print('---ini---')
            # print('La parte seleccionada es:')
            
            phase=schema_json[phase_i]

            # print('')
            # print(phase)
            # print('')
            
            # print(phase['id'])
            # print(phase['type'])
            # print(phase['name'])


            if (phase['type']=='phase'):

                #In case it have been remove the reference to user most be None:
                #The disabler user dont exists
                phase["disabler_id"] = None
                
                phase_obj = schemas.PhaseCreate(**phase)
                phase_obj.coproductionprocess_id=created_process.id
                
                #Set the previous item:
                if prev_phase:
                 phase_obj.prerequisites_ids=[prev_phase.id]
                
                phase_created=await crud.phase.create(db,obj_in=phase_obj,creator=current_user)
                #Store the previous created object
                prev_phase=phase_created

                # print('The phase  created is:')
                print(phase_created)
                print('The phase is: '+phase_created.name)
                # print('---fin---')

                #Ask if the phase has objectives:
                prev_objective=None
                for objective_i in range(len(phase['objectives'])):

                    # print('---ini Objective---')
                    # print('La parte seleccionada es:')
                    
                    objective=phase['objectives'][objective_i]

                    # print('')
                    # print(objective)
                    # print('')
                    
                    # print(objective['id'])
                    # print(objective['type'])
                    print('The objective is: '+objective['name'])

                    # print('---fin Objective---')

                    if (objective['type']=='objective'):

                        #In case it have been remove the reference to user most be None:
                        #The disabler user dont exists
                        objective["disabler_id"] = None

                        objective_obj = schemas.ObjectiveCreate(**objective)
                        objective_obj.phase_id=phase_created.id

                        #Set the previous item:
                        if prev_objective:
                            objective_obj.prerequisites_ids=[prev_objective.id]


                        objective_created=await crud.objective.create(db,obj_in=objective_obj,creator=current_user)

                        #Store the previous created object
                        prev_objective=objective_created

                        # print('The objective created is:')
                        # print(objective_created)
                        # print('---fin---')
                

                        #Ask if the phase has objectives:
                        prev_task=None
                        for task_i in range(len(objective['tasks'])):

                            # print('---ini Task---')
                            # print('La parte seleccionada es:')
                            
                            task=objective['tasks'][task_i]

                            # print('')
                            # print(task)
                            # print('')
                            
                            # print(task['id'])
                            # print(task['type'])
                            # print(task['name'])

                            # print('---fin Task---')

                            if (task['type']=='task'):

                                #In case it have been remove the reference to user most be None:
                                #The disabler user dont exists
                                task["disabler_id"] = None

                                task_obj = schemas.TaskCreate(**task)
                                task_obj.objective_id=objective_created.id

                                if prev_task:
                                    task_obj.prerequisites_ids=[prev_task.id]


                                task_created=await crud.task.create(db,obj_in=task_obj,creator=current_user)

                                #Store the previous created object
                                prev_task=task_created
                            
                                # print('The task created is:')
                                # print(task_created)
                                # print('---fin---')


                                #Go over each asset:

                                for asset_i in range(len(task['assets'])):
                                    asset=task['assets'][asset_i]
                                    
                                    if(asset["type"]=="internalasset"):

                                        knowledgeinterlinker_id=None
                                        #Look if it has a knowledge interlinker
                                        if asset["knowledgeinterlinker_id"]:
                                            #Get the name of the interlinker:
                                            knowledgeName=asset["knowledgeinterlinker"]["name"]
                                            #Search if this interlink exist in the catalogue:
                                         
                                            url = f'http://catalogue:80/api/v1/interlinkers/get_by_name/{knowledgeName}'
                                            headers = {
                                                'Authorization': token
                                                }
                                            response = requests.get(url,headers=headers)

                                            # Check if the request was successful
                                            if response.status_code == 200:
                                                # Parse the JSON response
                                                knowledgeinterlinker = response.json()
                                                print("The knowledge interlinker found is:"+knowledgeinterlinker["id"])
                                                print("- its name is: "+knowledgeinterlinker["name"]) 
                                                knowledgeinterlinker_id=knowledgeinterlinker["id"]     
                                                
                                                #print("Success:", knowledgeinterlinker)
                                            else:
                                                print("Failed. Status code:", response.status_code)

                                        
                                        #Create the asset in the service

                                        #Find the service name:
                                        # Pattern to match the service name (matches the portion between "http://" and the first slash)
                                        pattern = re.compile(r'http://(.*?)/')
                                        match = pattern.search(asset['internal_link'])

                                        if match:
                                            service_name = match.group(1)
                                            #print("Service Name:", service_name)
                                        else:
                                            print("Service name not found")
                                        

                                        #Upload the file to drive (googledrive):
                                        url = f'http://{service_name}:80/assets'

                                        # Specify the path to your file
                                        path_asset_folder = Path(unzipped_folder_name+"/processes_exported/"+process_name+"/assets/")
                                        
                                        #print('The asset Id is:')
                                        print('The asset Id is:'+str(asset['id']))
                                        file_path=get_file_by_asset_id(asset['id'],path_asset_folder)

                                        # Define the new name
                                        
                                        new_file_name = get_modified_file_name(file_path)  # Replace with the actual new name and extension
                                        new_file_path = str(path_asset_folder / new_file_name)

                                        # Copy the file to the new location with the new name
                                        shutil.copy(file_path, new_file_path)
                                        
                                        with open(new_file_path, 'rb') as f:
                                            files = {'file': f}
                                            headers = {
                                            'Authorization': token
                                            }
                                            response = requests.post(url,headers=headers, files=files)

                                        # Check the response
                                        if response.status_code == 201:
                                            #print("File uploaded successfully!")
                                            #print("Response:", response.json())
                                            pass
                                        else:
                                            print("Failed to upload file. Status code:", response.status_code)
                                            print("Response:", response.json())

                                        asset_service=response.json()

                                        #Get the googledrive software interlinker ID

                                        serviceName=service_name
                                        url = f'http://catalogue:80/api/v1/softwareinterlinkers/'+serviceName
                                        headers = {
                                            'Authorization': token
                                            }
                                        response = requests.get(url,headers=headers)

                                        # Check if the request was successful
                                        if response.status_code == 200:
                                            # Parse the JSON response
                                            serviceinfo = response.json()
                                            
                                            #print("Success:", serviceinfo)
                                        else:
                                            print("Failed. Status code:", response.status_code)



                                        #asset_obj = schemas.InternalAssetCreate(**asset)
                                        # Creating an instance of the class

                                        asset_obj = schemas.InternalAssetCreate(
                                        task_id=task_created.id,
                                        softwareinterlinker_id=UUID(serviceinfo['id']),
                                        knowledgeinterlinker_id=knowledgeinterlinker_id,
                                        external_asset_id=asset_service['id']
                                        )




                                    if(asset["type"]=="externalasset"):
                                        #asset_obj = schemas.ExternalAssetCreate(**asset)
                                        # Creating an instance of the class
                                        print('Creating External Asset: ' +asset['name'])
                                        asset_obj = schemas.ExternalAssetCreate(
                                        task_id=task_created.id,
                                        externalinterlinker_id=None,
                                        name=asset['name'],
                                        uri=asset['uri']
                                        )

                                      

                    

                                    asset_created=await crud.asset.create(db,asset=asset_obj,creator=current_user,task=task_created)
                                    # print('The asset created is:')
                                    # print(asset_obj)
                                    
                                    # print(asset_created)
                                    # print('---fin---')
                           
                
    contents = created_process

    shutil.rmtree(unzipped_folder)
    shutil.rmtree(Path(unzipped_folder_name))

    return contents

@router.get("/{id}/tree/catalogue", response_model=Optional[List[schemas.PhaseOutFull]])
async def get_coproductionprocess_tree_catalogue(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get coproductionprocess tree.
    """
    coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
   
    return coproductionprocess.children


# specific

@router.get("/{id}/activity")
async def get_activity(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get coproductionprocess activity.
    """
    coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    return requests.get(f"http://logging/api/v1/log?coproductionprocess_ids={id}&size=20").json()


@router.get("/{id}/assets")
async def read_coproductionprocess_assets(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: Optional[models.User] = Depends(deps.get_current_active_user),
    token: str = Depends(deps.get_current_active_token)
) -> Any:
    """
    Get coproductionprocess by ID.
    """

    coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)

    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    if not crud.coproductionprocess.can_read(db=db, user=current_user, object=coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return await crud.coproductionprocess.get_assets(db=db, user=current_user, coproductionprocess=coproductionprocess,token=token)


@router.post("/{id}/administrators")
async def add_administrator(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_in: schemas.UserIn,
) -> Any:
    if (user := await crud.user.get(db=db, id=user_in.user_id)):
        if (coproductionprocess := await crud.coproductionprocess.get(db=db, id=id)):
            if crud.coproductionprocess.can_update(user=current_user, object=coproductionprocess):
                return await crud.coproductionprocess.add_administrator(db=db, db_obj=coproductionprocess, user=user)
            raise HTTPException(
                status_code=403, detail="You are not allowed to update this coproductionprocess")
        raise HTTPException(status_code=404, detail="Coproductionprocess not found")
    raise HTTPException(status_code=404, detail="User not found")


@router.delete("/{id}/administrators/{user_id}")
async def delete_administrator(
    *,
    id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_id: str
) -> Any:
    if (user := await crud.user.get(db=db, id=user_id)):
        if (coproductionprocess := await crud.coproductionprocess.get(db=db, id=id)):
            if crud.coproductionprocess.can_update(user=current_user, object=coproductionprocess):
                return await crud.coproductionprocess.remove_administrator(db=db, db_obj=coproductionprocess, user=user)
            raise HTTPException(
                status_code=403, detail="You are not allowed to update this coproductionprocess")
        raise HTTPException(status_code=404, detail="Coproductionprocess not found")
    raise HTTPException(status_code=404, detail="User not found")

@router.post("/send_message")
async def send_message(
    *,
    id: uuid.UUID,
    message: str
) -> Any:
    await socket_manager.send_to_id(id=id, data={"data": message})


@router.post("/emailApplyToBeContributor")
async def sendEmailApplyToBeContributor(
    *,
    db: Session = Depends(deps.get_db),
    data: dict,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    if (coproductionprocess := await crud.coproductionprocess.get(db=db, id=data["processId"])):
        print("The coproductionprocess is: "+str(coproductionprocess.id))
        
        #Create an request application to be contributor
        newParticipationRequest = ParticipationRequest() 
        newParticipationRequest.candidate_id = current_user.id
        newParticipationRequest.coproductionprocess_id = coproductionprocess.id
        newParticipationRequest.razon=data["razon"]
        db.add(newParticipationRequest)
        db.commit()
        db.refresh(newParticipationRequest)

        
        #Lets create a notification in-app of the solicitude.
        notification = await crud.notification.get_notification_by_event(db=db, event="apply_submited", language=coproductionprocess.language)
        if (notification):
            print("The notification is: "+str(notification.id))
            #I need to create a notification for every admin of the process:
            for admin_id in coproductionprocess.administrators_ids:
                newUserNotification = UserNotification()
                newUserNotification.user_id = admin_id

                newUserNotification.notification_id = notification.id
                newUserNotification.channel = "in_app"
                newUserNotification.state = False
                newUserNotification.coproductionprocess_id = str(
                    coproductionprocess.id)
                newUserNotification.parameters = "{'razon':'"+data["razon"]+"','userName':'"+current_user.full_name+"','userEmail':'"+current_user.email+"','processName':'"+html.escape(
                    coproductionprocess.name)+"','copro_id':'"+str(coproductionprocess.id)+"'}"
            
                print("Create a notification for the user: "+str(admin_id)+" with the notification: "+str(notification.id)+" and the coproductionprocess: "+str(coproductionprocess.id)+" and the parameters: "+str(newUserNotification.parameters))
                db.add(newUserNotification)
                db.commit()
                db.refresh(newUserNotification)


        #if crud.coproductionprocess.can_update(user=current_user, object=coproductionprocess):
        print(data["adminEmails"])
        for admin_email in data["adminEmails"]:
            print("Send email to: "+admin_email)
            send_email(admin_email, "apply_to_be_contributor",
                            {"coprod_id": data["processId"],
                                "user_name": current_user.full_name,
                                "user_email": current_user.email,
                                "coproductionprocess_name": data["coproductionName"],
                                "razon": data["razon"],
                            })

    return "Done"


@router.websocket("/{id}/ws")
async def websocket_endpoint(
    *,
    id: uuid.UUID,
    websocket: WebSocket
):
    await socket_manager.connect(websocket, id)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        socket_manager.disconnect(websocket, id)


@router.post("/{id}/copy")
async def copy_coproductionprocess(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
    token: str = Depends(deps.get_current_active_token),
    label_name: str = '',
    from_view:str='',
) -> Any:
    """
    Copy a coproductionprocess.
    """
    coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    
    if(from_view != 'story'):    
        if not crud.coproductionprocess.can_remove(user=current_user, object=coproductionprocess):
            raise HTTPException(status_code=403, detail="Not enough permissions")

    new_coprod = await crud.coproductionprocess.copy(db=db, coproductionprocess=coproductionprocess, user=current_user, token=token, label_name=label_name,from_view=from_view)
    #print("new_coprod", new_coprod)
    if coproductionprocess.logotype:
        filename, extension = os.path.splitext(coproductionprocess.logotype.split('/')[-1])
        in_file_path = coproductionprocess.logotype
        out_file_path = f"/static/coproductionprocesses/{new_coprod.id}{extension}"
        #print("in_file_path", in_file_path)
        
        async with aiofiles.open("/app" + in_file_path, 'rb') as in_file:
            content = await in_file.read()
            #print("content", content)
            async with aiofiles.open("/app" + out_file_path, 'wb') as out_file:
                #print("out_file", out_file_path)
                await out_file.write(content) 
                 # async write
        #print("PREUPDATE")

    
        await crud.coproductionprocess.set_logotype(db=db, coproductionprocess=new_coprod,logotype_path=out_file_path)
    #print("POSTUPDATE")
    # If new_coprod is returned it raises an error regarding recursion with Python
    return new_coprod.id

@router.post("/{id}/addTag")
async def add_tag(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
    tag: schemas.Tag,
) -> Any:
    """
    Add tag to coproductionprocess.
    """
    coproductionprocess = await crud.coproductionprocess.get(db=db, id=id)
    if not coproductionprocess:
        raise HTTPException(status_code=404, detail="CoproductionProcess not found")
    if not crud.coproductionprocess.can_update(user=current_user, object=coproductionprocess):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.coproductionprocess.add_tag(db=db, db_obj=coproductionprocess, tag=tag)