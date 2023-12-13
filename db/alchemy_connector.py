from sshtunnel import SSHTunnelForwarder
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from utils.logger import logger
from dotenv import load_dotenv
import os

load_dotenv()

class MySQLDBConnection():

    distance_enabled = os.getenv("DISTANCE", "False").lower() == "true"

    def __init__(self, user, password, host, port, database, type):

        logger.info(f"Conectando con MySQL {type}")
        if self.distance_enabled:
            try:
                self.ssh_server = SSHTunnelForwarder(
                        (os.getenv('SSH_HOSTNAME'), int(os.getenv('SSH_PORT'))),
                        ssh_username=os.getenv('SSH_USERNAME'),
                        ssh_password=os.getenv('SSH_PASSWORD'),
                        remote_bind_address=(host, port)
                )
                self.ssh_server.start()

                self.engine = create_engine(f"mysql+pymysql://{user}:{password}@127.0.0.1:{self.ssh_server.local_bind_port}/{database}")
            except ConnectionError as e:
                logger.error("Failed to connect to MySQL: %s", e)
            except Exception as e:
                logger.error("Error desconocido ocurrido: %s", e)

        else:
            try:
                self.engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")
            except ConnectionError as e:
                logger.error("Failed to connect to MySQL: %s", e)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    def get_session(self):

        if self.distance_enabled:
            return self.ssh_server, self.session

        return None, self.session

