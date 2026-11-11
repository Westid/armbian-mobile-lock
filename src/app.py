import os
import sqlite3
import asyncio
from datetime import datetime
from loguru import logger
import serial 


connection = sqlite3.connection('data/service.db')

if __name__ == "__main__":
    logger.info("")
