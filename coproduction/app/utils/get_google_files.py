from app.general.db.session import SessionLocal
from app.models import InternalAsset
import requests

res = requests.get("http://catalogue/api/v1/interlinkers/get_by_name/Google%20Drive").json()

db = SessionLocal()
try:
    assets = db.query(InternalAsset).filter(InternalAsset.softwareinterlinker_id == res.get("id")).all()
    print([str(asset.external_asset_id) for asset in assets])
except Exception as e:
    db.close()