import enum

from sqlalchemy.dialects.postgresql import ENUM

from app.database import db
from datetime import datetime

TraderTypeEnum = ENUM("elf", "wizard", "dwarf", name="tradertype", create_type=False)

class TraderType(enum.Enum):
    ELF = 'elf'
    DWARF = 'dwarf'
    WIZARD = 'wizard'

class Trader(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    trader_type = db.Column(TraderTypeEnum, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
