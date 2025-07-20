from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Travel Item Models
class TravelItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    name_ar: str
    category: str
    is_packed: bool = False
    notes: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TravelItemCreate(BaseModel):
    name: str
    name_ar: str
    category: str
    notes: str = ""

class TravelItemUpdate(BaseModel):
    name: Optional[str] = None
    name_ar: Optional[str] = None
    is_packed: Optional[bool] = None
    notes: Optional[str] = None

class TravelCategory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    name_ar: str
    icon: str
    color: str

class TravelList(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    destination: str = ""
    items: List[TravelItem] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TravelListCreate(BaseModel):
    name: str
    destination: str = ""

# Initialize default categories and items
default_categories = [
    {"id": "clothes", "name": "Clothes", "name_ar": "الملابس", "icon": "👕", "color": "bg-blue-100 text-blue-800"},
    {"id": "toiletries", "name": "Toiletries", "name_ar": "أدوات النظافة", "icon": "🧴", "color": "bg-green-100 text-green-800"},
    {"id": "electronics", "name": "Electronics", "name_ar": "الإلكترونيات", "icon": "📱", "color": "bg-purple-100 text-purple-800"},
    {"id": "documents", "name": "Documents", "name_ar": "الوثائق", "icon": "📄", "color": "bg-red-100 text-red-800"},
    {"id": "medicine", "name": "Medicine", "name_ar": "الأدوية", "icon": "💊", "color": "bg-pink-100 text-pink-800"},
    {"id": "miscellaneous", "name": "Miscellaneous", "name_ar": "متنوعات", "icon": "🎒", "color": "bg-yellow-100 text-yellow-800"}
]

default_items = [
    # Clothes
    {"name": "T-Shirts", "name_ar": "تيشيرتات", "category": "clothes"},
    {"name": "Pants/Jeans", "name_ar": "بناطيل/جينز", "category": "clothes"},
    {"name": "Underwear", "name_ar": "ملابس داخلية", "category": "clothes"},
    {"name": "Socks", "name_ar": "جوارب", "category": "clothes"},
    {"name": "Pajamas", "name_ar": "بيجامة", "category": "clothes"},
    {"name": "Shoes", "name_ar": "أحذية", "category": "clothes"},
    {"name": "Jacket/Coat", "name_ar": "جاكيت/معطف", "category": "clothes"},
    {"name": "Swimwear", "name_ar": "ملابس السباحة", "category": "clothes"},
    
    # Toiletries
    {"name": "Toothbrush", "name_ar": "فرشاة أسنان", "category": "toiletries"},
    {"name": "Toothpaste", "name_ar": "معجون أسنان", "category": "toiletries"},
    {"name": "Shampoo", "name_ar": "شامبو", "category": "toiletries"},
    {"name": "Body Wash", "name_ar": "غسول الجسم", "category": "toiletries"},
    {"name": "Deodorant", "name_ar": "مزيل العرق", "category": "toiletries"},
    {"name": "Razor", "name_ar": "ماكينة حلاقة", "category": "toiletries"},
    {"name": "Moisturizer", "name_ar": "مرطب", "category": "toiletries"},
    {"name": "Sunscreen", "name_ar": "واقي شمس", "category": "toiletries"},
    
    # Electronics
    {"name": "Phone Charger", "name_ar": "شاحن الهاتف", "category": "electronics"},
    {"name": "Power Bank", "name_ar": "بطارية محمولة", "category": "electronics"},
    {"name": "Camera", "name_ar": "كاميرا", "category": "electronics"},
    {"name": "Headphones", "name_ar": "سماعات", "category": "electronics"},
    {"name": "Adapter/Converter", "name_ar": "محول كهربائي", "category": "electronics"},
    {"name": "Laptop", "name_ar": "حاسوب محمول", "category": "electronics"},
    
    # Documents
    {"name": "Passport", "name_ar": "جواز السفر", "category": "documents"},
    {"name": "Visa", "name_ar": "فيزا", "category": "documents"},
    {"name": "Flight Tickets", "name_ar": "تذاكر الطيران", "category": "documents"},
    {"name": "Hotel Reservations", "name_ar": "حجوزات الفندق", "category": "documents"},
    {"name": "Travel Insurance", "name_ar": "تأمين السفر", "category": "documents"},
    {"name": "Driver's License", "name_ar": "رخصة القيادة", "category": "documents"},
    {"name": "ID Card", "name_ar": "بطاقة الهوية", "category": "documents"},
    
    # Medicine
    {"name": "Prescription Medicines", "name_ar": "الأدوية الموصوفة", "category": "medicine"},
    {"name": "Pain Relievers", "name_ar": "مسكنات الألم", "category": "medicine"},
    {"name": "First Aid Kit", "name_ar": "حقيبة إسعافات أولية", "category": "medicine"},
    {"name": "Vitamins", "name_ar": "فيتامينات", "category": "medicine"},
    {"name": "Band-aids", "name_ar": "لاصقات طبية", "category": "medicine"},
    
    # Miscellaneous
    {"name": "Sunglasses", "name_ar": "نظارات شمسية", "category": "miscellaneous"},
    {"name": "Travel Pillow", "name_ar": "وسادة السفر", "category": "miscellaneous"},
    {"name": "Snacks", "name_ar": "وجبات خفيفة", "category": "miscellaneous"},
    {"name": "Water Bottle", "name_ar": "قارورة ماء", "category": "miscellaneous"},
    {"name": "Books/E-reader", "name_ar": "كتب/قارئ إلكتروني", "category": "miscellaneous"},
    {"name": "Travel Guide", "name_ar": "دليل السفر", "category": "miscellaneous"},
    {"name": "Cash/Credit Cards", "name_ar": "نقود/بطاقات ائتمان", "category": "miscellaneous"}
]

# API Routes

# Get all categories
@api_router.get("/categories", response_model=List[TravelCategory])
async def get_categories():
    categories = await db.categories.find().to_list(1000)
    if not categories:
        # Initialize default categories
        for cat in default_categories:
            await db.categories.insert_one(cat)
        categories = await db.categories.find().to_list(1000)
    return [TravelCategory(**cat) for cat in categories]

# Get all travel lists
@api_router.get("/travel-lists", response_model=List[TravelList])
async def get_travel_lists():
    lists = await db.travel_lists.find().to_list(1000)
    return [TravelList(**travel_list) for travel_list in lists]

# Create a new travel list
@api_router.post("/travel-lists", response_model=TravelList)
async def create_travel_list(travel_list: TravelListCreate):
    # Create default items for the new list
    items = []
    for item_data in default_items:
        item = TravelItem(**item_data)
        items.append(item.dict())
    
    new_list = TravelList(
        name=travel_list.name,
        destination=travel_list.destination,
        items=items
    )
    
    await db.travel_lists.insert_one(new_list.dict())
    return new_list

# Get a specific travel list
@api_router.get("/travel-lists/{list_id}", response_model=TravelList)
async def get_travel_list(list_id: str):
    travel_list = await db.travel_lists.find_one({"id": list_id})
    if not travel_list:
        raise HTTPException(status_code=404, detail="Travel list not found")
    return TravelList(**travel_list)

# Update travel list
@api_router.put("/travel-lists/{list_id}", response_model=TravelList)
async def update_travel_list(list_id: str, updates: dict):
    updates["updated_at"] = datetime.utcnow()
    result = await db.travel_lists.update_one(
        {"id": list_id}, 
        {"$set": updates}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Travel list not found")
    
    updated_list = await db.travel_lists.find_one({"id": list_id})
    return TravelList(**updated_list)

# Add item to travel list
@api_router.post("/travel-lists/{list_id}/items", response_model=TravelItem)
async def add_item_to_list(list_id: str, item: TravelItemCreate):
    new_item = TravelItem(**item.dict())
    
    result = await db.travel_lists.update_one(
        {"id": list_id},
        {"$push": {"items": new_item.dict()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Travel list not found")
    
    return new_item

# Update item in travel list
@api_router.put("/travel-lists/{list_id}/items/{item_id}", response_model=TravelItem)
async def update_item_in_list(list_id: str, item_id: str, updates: TravelItemUpdate):
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    
    result = await db.travel_lists.update_one(
        {"id": list_id, "items.id": item_id},
        {"$set": {f"items.$.{k}": v for k, v in update_dict.items()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Travel list or item not found")
    
    # Get the updated item
    travel_list = await db.travel_lists.find_one({"id": list_id})
    updated_item = next((item for item in travel_list["items"] if item["id"] == item_id), None)
    
    return TravelItem(**updated_item)

# Delete item from travel list
@api_router.delete("/travel-lists/{list_id}/items/{item_id}")
async def delete_item_from_list(list_id: str, item_id: str):
    result = await db.travel_lists.update_one(
        {"id": list_id},
        {"$pull": {"items": {"id": item_id}}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Travel list not found")
    
    return {"message": "Item deleted successfully"}

# Get progress statistics
@api_router.get("/travel-lists/{list_id}/stats")
async def get_list_stats(list_id: str):
    travel_list = await db.travel_lists.find_one({"id": list_id})
    if not travel_list:
        raise HTTPException(status_code=404, detail="Travel list not found")
    
    items = travel_list.get("items", [])
    total_items = len(items)
    packed_items = len([item for item in items if item.get("is_packed", False)])
    
    progress_percentage = (packed_items / total_items * 100) if total_items > 0 else 0
    
    # Category-wise stats
    category_stats = {}
    for item in items:
        category = item.get("category", "miscellaneous")
        if category not in category_stats:
            category_stats[category] = {"total": 0, "packed": 0}
        category_stats[category]["total"] += 1
        if item.get("is_packed", False):
            category_stats[category]["packed"] += 1
    
    return {
        "total_items": total_items,
        "packed_items": packed_items,
        "remaining_items": total_items - packed_items,
        "progress_percentage": round(progress_percentage, 1),
        "category_stats": category_stats
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()