from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging

class MongoDbClient:
    _instance = None
    _client = None
    _db = None

    @classmethod
    def get_instance(cls, db_name):
        if cls._instance is None:
            cls._instance = cls(db_name)
        return cls._instance

    def __init__(self, db_name):
        if self._instance is not None:
            raise RuntimeError("Use get_instance() instead")
        self.logger = logging.getLogger(__name__)
        self.mongo_uri = self._load_mongo_uri()
        self.db_name = db_name
        self._connect()

    def _load_mongo_uri(self):
        load_dotenv(override=True)
        uri = os.getenv('MONGO_URI_DEV') if os.getenv('LOCAL_DEV') == 'true' else os.getenv('MONGO_URI')
        self.logger.info(f"Loaded MongoDB URI: {uri}")
        return uri

    def _connect(self):
        if not self._client:
            self.logger.info(f"Attempting to connect to MongoDB at {self.mongo_uri}")
            try:
                self._client = AsyncIOMotorClient(self.mongo_uri)
                self._db = self._client[self.db_name]
                self.logger.info(f"Successfully connected to MongoDB database: {self.db_name}")
            except Exception as e:
                self.logger.error(f"Failed to connect to MongoDB: {str(e)}")
                raise

    @property
    def db(self):
        if self._db is None:
            self._connect()
        return self._db

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
            self._db = None