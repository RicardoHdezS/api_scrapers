from db.alchemy_connector import MySQLDBConnection
from .helper import ScrapersValidations
from data.models import IcapsulaData
from utils.logger import logger
from dotenv import load_dotenv
import os

load_dotenv()
validations = ScrapersValidations()

class ScrapersInstance:

    distance_enabled = os.getenv("DISTANCE", "False").lower() == "true"
    def validate_data(self, item):

        try:
            self.testing_enabled = os.getenv("TESTING", "False").lower() == "true"

            if self.testing_enabled:
                db_connection = MySQLDBConnection(
                    user=os.getenv("MYSQL_USER_TEST"),
                    password=os.getenv("MYSQL_PASSWORD_TEST"),
                    host=os.getenv("MYSQL_HOST_TEST"),
                    port=int(os.getenv("MYSQL_PORT_TEST")),
                    database=os.getenv("MYSQL_DB_NAME_TEST"),
                    type="Pruebas"
                )

                self.server_clie, self.session_clie = None, None

            else:
                db_connection = MySQLDBConnection(
                    user=os.getenv("MYSQL_USER"),
                    password=os.getenv("MYSQL_PASSWORD"),
                    host=os.getenv("MYSQL_HOST"),
                    port=int(os.getenv("MYSQL_PORT")),
                    database=os.getenv("MYSQL_DB_NAME"),
                    type="Produccion"
                )

                db_connection_clientes = MySQLDBConnection(
                    user=os.getenv("MYSQL_USER_CLIE"),
                    password=os.getenv("MYSQL_PASSWORD_CLIE"),
                    host=os.getenv("MYSQL_HOST_CLIE"),
                    port=int(os.getenv("MYSQL_PORT_CLIE")),
                    database=os.getenv("MYSQL_DB_NAME_CLIE"),
                    type="Clientes"
                )

                self.server_clie, self.session_clie = db_connection_clientes.get_session()

            self.server, self.session = db_connection.get_session()

            logger.info("Buscando registro en la base de datos")
            query = (
                self.session.query(
                    IcapsulaData.CAPTITULO, IcapsulaData.CAPURLORIGINAL,
                    IcapsulaData.CAPTEXTCOMP, IcapsulaData.CAPFCAPTURA,
                    IcapsulaData.CAPFCAPSULA, IcapsulaData.CAPFMODIF,
                    IcapsulaData.CAPNOMBRE, IcapsulaData.CAPCLAVE
                )
                .filter(IcapsulaData.CAPMEDIO == 8)
                .filter(IcapsulaData.CAPNOMBRE == item.news_cve_medio)
                .filter(IcapsulaData.CAPURLORIGINAL == item.news_url)
            )

            result = query.all()

            if len(result) > 1:
                logger.warning("Se encontro mas de un registro con la misma URL: %s", item.news_url)
            elif len(result) == 1:
                logger.info("Registro existente: %s", item.news_url)
                logger.info("Analizando elementos")

                update = validations.update_title_or_content(self.session, item, result[0], '')
                if self.session_clie:
                    update = validations.update_title_or_content(self.session_clie, item, result[0], 'Clientes')

                if update['status'] == 'success':
                    logger.info("Registro actualizado: %s", item.news_url)
                elif update['status'] == 'error':
                    logger.error("Error al actualizar el registro: %s", update['exception'])
                elif update['status'] == 'no_changes':
                    logger.warning("No hay elementos por actualizar: %s", item.news_url)
            else:
                logger.info("Registro nuevo: %s", item.news_url)
                logger.info("Insertando elementos")

                insert_item = validations.insert_new_register(self.session, item, self.session_clie)

                if insert_item['status'] == 'success':
                    logger.info("Registro insertado: %s", item.news_url)
                elif insert_item['status'] == 'error':
                    logger.error("Error al insertar el registro: %s", insert_item['exception'])

            if self.testing_enabled:
                self.session.close()
                if self.distance_enabled:
                    self.server.close()
            else:
                self.session.close()
                self.session_clie.close()
                if self.distance_enabled:
                    self.server.close()
                    self.server_clie.close()
        except TypeError as e:
            logger.error("Error al entrar al item: %s", e)
