from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List
from geopy.distance import geodesic
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./addresses.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Define the Address model using SQLAlchemy ORM
class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)

# Create the tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# validation
class AddressRequest(BaseModel):
    name: str
    latitude: float
    longitude: float

# Pydantic model for address 
class AddressResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float

# SQLite session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# create a new address
@app.post("/addresses/", response_model=AddressResponse)
def create_address(address: AddressRequest, db: Session = Depends(get_db)):
    existing_address = db.query(Address).filter(Address.name == address.name).first()
    if existing_address:
        raise HTTPException(status_code=400, detail="Address with this name already exists")

    # Create and add the new address
    new_address = Address(**address.dict())
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address

# update an  address
@app.put("/addresses/{address_id}", response_model=AddressResponse)
def update_address(address_id: int, address: AddressRequest, db: Session = Depends(get_db)):
    db_address = db.query(Address).filter(Address.id == address_id).first()
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")

    # Update the address 
    db_address.name = address.name
    db_address.latitude = address.latitude
    db_address.longitude = address.longitude
    db.commit()
    db.refresh(db_address)
    return db_address

# delete an address
@app.delete("/addresses/{address_id}")
def delete_address(address_id: int, db: Session = Depends(get_db)):
    db_address = db.query(Address).filter(Address.id == address_id).first()
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")

    # Delete the address
    db.delete(db_address)
    db.commit()
    return {"message": "Address deleted successfully"}

# Get all addresses
@app.get("/addresses/", response_model=List[AddressResponse])
def get_addresses(db: Session = Depends(get_db)):
    addresses = db.query(Address).all()
    return addresses

# Get addresses within a given distance from a location
@app.get("/addresses/distance/", response_model=List[AddressResponse])
def get_addresses_within_distance(latitude: float = Query(..., description="Latitude of the user"),
                                  longitude: float = Query(..., description="Longitude of the user"),
                                  distance: float = Query(..., description="Distance in kilometers"),
                                  db: Session = Depends(get_db)):
    # Query all addresses
    all_addresses = db.query(Address).all()

    location_coords = (latitude, longitude)
    addresses_within_distance = []
    for address in all_addresses:
        address_coords = (address.latitude, address.longitude)
        if geodesic(location_coords, address_coords).kilometers <= distance:
            addresses_within_distance.append(address)

    return addresses_within_distance

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
