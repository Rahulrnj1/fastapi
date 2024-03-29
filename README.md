# FastAPI Address Book App
#FastAPI: Install FastAPI using
pip install fastapi
pip install sqlalchemy
pip install geopy
pip install uvicorn
**Port:** By default, the application runs on port 8000.
run the code use this cmd 
python -m uvicorn main:app --reload
This is a FastAPI application for managing addresses, including CRUD operations and distance-based queries.
**Create Address:** POST `/addresses/`
**Update Address:** PUT `/addresses/{address_id}`
**Delete Address:** DELETE `/addresses/{address_id}`
**Get All Addresses:** GET `/addresses/`
**Get Addresses Within Distance:** GET `/addresses/distance/`
