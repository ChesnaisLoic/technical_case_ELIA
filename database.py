from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from config import settings

DB_CONNECTION_STRING = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_engine(DB_CONNECTION_STRING)

Base = declarative_base()


class CurrentSystemImbalance(Base):
    __tablename__ = "current_system_imbalance"

    id = Column(Integer, nullable=False, primary_key=True)
    datetime = Column(DateTime(timezone=True), nullable=False)
    resolutioncode = Column(String, nullable=True)
    qualitystatus = Column(String, nullable=True)
    systemimbalance = Column(Float, nullable=True)
    ace = Column(Float, nullable=True)
    igccvolumeup = Column(Float, nullable=True)
    afrrvolumeup = Column(Float, nullable=True)
    mfrrsaup = Column(Float, nullable=True)
    mfrrdaup = Column(Float, nullable=True)
    reserve_sharing_import = Column(Float, nullable=True)
    igccvolumedown = Column(Float, nullable=True)
    afrrvolumedown = Column(Float, nullable=True)
    mfrrsadown = Column(Float, nullable=True)
    mfrrdadown = Column(Float, nullable=True)
    reserve_sharing_export = Column(Float, nullable=True)


class ImbalancePricesPerQuarterhour(Base):
    __tablename__ = "imbalance_prices_per_quarter-hour"

    id = Column(Integer, nullable=False, primary_key=True)
    datetime = Column(DateTime(timezone=True), nullable=False)
    resolutioncode = Column(String, nullable=True)
    qualitystatus = Column(String, nullable=True)
    ace = Column(Float, nullable=True)
    systemimbalance = Column(Float, nullable=True)
    alpha = Column(Float, nullable=True)
    alpha_prime = Column(Float, nullable=True)
    marginalincrementalprice = Column(Float, nullable=True)
    marginaldecrementalprice = Column(Float, nullable=True)
    imbalanceprice = Column(Float, nullable=True)


class AggregatedVolumesUpDownPerQuarterhour(Base):
    __tablename__ = "aggregated_volumes_up_down_per_quarter-hour"

    id = Column(Integer, nullable=False, primary_key=True)
    datetime = Column(DateTime(timezone=True), nullable=False)
    affrvolumeup = Column(Float, nullable=True)
    affrvolumedown = Column(Float, nullable=True)


def database_initialization():
    Base.metadata.create_all(engine)
