from typing import List

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()
engine = create_engine('sqlite:////britebadge.db?check_same_thread=False')


class Configuration(Base):
    __tablename__ = "configuration"
    config_id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    config_key = Column(String(50), nullable=False, unique=True)
    config_value = Column(String(50), nullable=False)


class PrintQueue(Base):
    __tablename__ = "print_queue"
    queue_id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    name = Column(String(70), nullable=False)
    purchase_id = Column(ForeignKey('purchase.purchase_id'), nullable=False)
    printed = Column(Boolean, nullable=False)
    purchase = relationship("Purchase")


class ProductPurchased(Base):
    __tablename__ = "product_purchased"
    product_purchase_id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    product_uuid = Column(String(50), nullable=False)
    unit_price = Column(Integer, nullable=False)
    details = Column(String(150), nullable=True)
    product_name = Column(String(50), nullable=False)
    product_variations = Column(String(50), nullable=True)
    comment = Column(String(50), nullable=True)
    purchase_id = Column(ForeignKey('purchase.purchase_id'), nullable=False)
    purchase = relationship("Purchase")

    @hybrid_property
    def cost(self):
        return self.unit_price / 100.0

    @hybrid_property
    def clean_product_variations(self):
        variations = self.product_variations.split(",")
        to_return = ""
        for variation in variations:
            if "None" not in variation:
                to_return = to_return + variation
        return to_return



class Purchase(Base):
    __tablename__ = "purchase"
    purchase_id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    purchase_uuid = Column(String(100), nullable=False)
    amount = Column(Integer, nullable=False)
    badges_printed = relationship("PrintQueue", foreign_keys=PrintQueue.purchase_id)
    products_purchased: List[ProductPurchased] = relationship("ProductPurchased")

    @hybrid_property
    def cost(self):
        return self.amount / 100.0


Base.metadata.create_all(engine)
