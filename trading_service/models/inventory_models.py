from enum import Enum

from sqlalchemy.dialects.postgresql import ENUM

from trading_service.database import db
from datetime import datetime

CommodityPropertyTypeEnum = ENUM(
    "color", "material", "size", name="commoditypropertytype", create_type=False
)

class CommodityPropertyType(Enum):
    COLOR = "color"
    MATERIAL = "material"
    SIZE = "size"

class Commodity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    properties = db.relationship('CommodityProperty', backref='commodity', lazy=True, cascade="all, delete-orphan")

class CommodityProperty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commodity_id = db.Column(db.Integer, db.ForeignKey('commodity.id', ondelete="CASCADE"))
    property_name = db.Column(CommodityPropertyTypeEnum, nullable=False)
    property_value = db.Column(db.String(100), nullable=False)

class TraderInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trader_id = db.Column(db.Integer, db.ForeignKey('trader.id'))
    commodity_id = db.Column(db.Integer, db.ForeignKey('commodity.id'))
    quantity = db.Column(db.Integer, nullable=False)
