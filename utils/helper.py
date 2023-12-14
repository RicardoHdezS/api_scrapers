import datetime
from utils.logger import logger
from data.models import (IcapsulaData, IcapsulaSequence,
                         IclippingImagen, IclippingPlutem,
                         IfteNombre, WitnessSequence)
from sqlalchemy import update, insert, case, text
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()


class ScrapersValidations:
    testing_enabled = os.getenv("TESTING", "False").lower() == "true"
    def insert_new_register(self, session, item, session_clie = None):
        try:

            seq_insert = self.insert_sequence_capsula_imagen(session)

            if seq_insert['status'] == 'success':
                logger.info("Capsula e Imagen insertadas: %s", item.news_url)
                iftenombre_data = self.get_iftenombre(session, item)

                if iftenombre_data['status'] == 'success':
                    logger.info("Complemento de registro obtenido: %s", item.news_url)

                    values = self.set_values_to_insert(item, seq_insert['last_inserted_id_note'], iftenombre_data)
                    try:
                        logger.info("Insertando en ICAPSULA")
                        values_icapsula = {
                            'CAPCLAVE': values[0],
                            'CAPAUTOR': values[1],
                            'CAPFCAPTURA': values[2],
                            'CAPFCAPSULA': values[3],
                            'CAPMODIF': values[4],
                            'CAPFMODIF': values[5],
                            'CAPAMBITO': values[6],
                            'CAPESTADO': values[7],
                            'CAPTIPOMEDIO': values[8],
                            'CAPMEDIO': values[9],
                            'CAPNOMBRE': values[10],
                            'CAPCLASIFICACION': values[11],
                            'CAPTERMINADO': values[12],
                            'CAPTITULO': values[13],
                            'CAPCOMENTARIO': values[14],
                            'CAPPERSISTENT': values[15],
                            'CAPTEXTCOMP': values[16],
                            'CAPTEXTSINT': values[17],
                            'CAPORIGEN': values[18],
                            'CAPTESTIGO': values[19],
                            'CAPURLORIGINAL': values[20],
                        }
                        query_icapsula = insert(IcapsulaData).values(values_icapsula)
                        session.execute(query_icapsula)

                        logger.info("Insertando en ICLIPPINGPLUTEM")
                        values_iclipingplutem = {
                            'CPTCLIPPING': seq_insert['last_inserted_id_note'],
                            'CPTCAPTEMA': seq_insert['last_inserted_id_note']
                        }
                        query_iclippingplutem = insert(IclippingPlutem).values(values_iclipingplutem)
                        session.execute(query_iclippingplutem)

                        logger.info("Insertando en ICLIPPINGIMAGEN")
                        values_iclippingimagen = {
                            'CIMCLIPPING': seq_insert['last_inserted_id_note'],
                            'CIMNOMBREARCHIVO': seq_insert['pdf_filename']
                        }
                        query_iclippingimagen = insert(IclippingImagen).values(values_iclippingimagen)
                        session.execute(query_iclippingimagen)

                        logger.info("Insertando en ICAPSULAALCANCE")
                        query_icapsulaalcance = """
                        INSERT INTO 
                            INTELITE_ICAPSULAALCANCE 
                                (caacapsula, caadist8a12, caadist13a17, caadist18a24,
                                caadist25a34, caadist35a44, caadist45a54, caadist55amas,
                                caadistalto, caadistmedio, caadistbajo, caadisthombre,
                                caadistmujer, caabanda, caaalcancereal)
                                SELECT DISTINCT 
                                    :capclave, caldist8a12, caldist13a17, caldist18a24,
                                    caldist25a34, caldist35a44, caldist45a54, caldist55amas,
                                    caldistalto, caldistmedio, caldistbajo, caldisthombre,
                                    caldistmujer, calbanda, caldisthombre+caldistmujer
                                FROM 
                                    INTELITE_ICATALCANCE
                                WHERE 
                                    calcvemedio = :cvemedio
                        """
                        values_icapsulaalcance = {
                            'capclave': values[0],
                            'cvemedio': values[9]
                        }
                        session.execute(text(query_icapsulaalcance), values_icapsulaalcance)

                        if self.testing_enabled:
                            session.commit()
                        else:
                            logger.info("Insertando en ICAPSULA Clientes")
                            session_clie.execute(query_icapsula)

                            logger.info("Insertando en ICLIPPINGPLUTEM Clientes")
                            session_clie.execute(query_iclippingplutem)

                            logger.info("Insertando en ICLIPPINGIMAGEN Clientes")
                            session_clie.execute(query_iclippingimagen)

                            logger.info("Insertando en ICAPSULAALCANCE Clientes")
                            session_clie.execute(text(query_icapsulaalcance), values_icapsulaalcance)

                            session.commit()
                            session_clie.commit()

                        return {
                            'status': 'success',
                        }

                    except Exception as e:

                        session.rollback()

                        return {
                            'status': 'error',
                            'exception': e
                        }

            else:
                logger.error("Error al insertar la secuencia: %s", seq_insert['exception'])

                return {
                    'status': 'error',
                    'exception': seq_insert['exception']
                }


        except Exception as e:
            logger.error("Error al insertar el nuevo registro: %s", e)
            session.rollback()

    def insert_sequence_capsula_imagen(self, session):
        try:
            logger.info("Insertando secuencia de notas")
            insert_sequence_note = insert(IcapsulaSequence).values({})
            exec_stmt_note = session.execute(insert_sequence_note)

            logger.info("Insertando secuencia de testigos")
            insert_sequence_witness = insert(WitnessSequence).values({})
            exec_stmt_witness = session.execute(insert_sequence_witness)

            session.commit()

            last_inserted_id_note = exec_stmt_note.lastrowid
            last_inserted_id_witness = exec_stmt_witness.lastrowid

            pdf_filename = f"SELECT CONCAT(DATE_FORMAT(NOW(),'%d%m%Y'), (lpad('{last_inserted_id_witness}' ,'6','0')), 'wd.pdf')"

            filename = session.execute(text(pdf_filename))
            filename = filename.scalar()

            logger.info("Nombre del archivo: %s", filename)

            return {
                'status': 'success',
                'last_inserted_id_note': last_inserted_id_note,
                'last_inserted_id_witness': last_inserted_id_witness,
                'pdf_filename': filename
            }

        except Exception as InsrtSeqException:
            session.rollback()

            return {
                'status': 'error',
                'exception': InsrtSeqException
            }

    def get_iftenombre(self, session, item):
        try:
            logger.info("Obteniendo complemento de registro")
            query = (
                session.query(
                    IfteNombre.FNOCLAVE,
                    IfteNombre.FNOMEDIO,
                    IfteNombre.FNOESTADO,
                    case(
                        (IfteNombre.FNOESTADO == 9, 1),
                        (IfteNombre.FNOESTADO == 1, 3),
                    else_=2)
                    .label('FNOAMBITO')
                )
                .filter(IfteNombre.FNOCLAVE == item.news_cve_medio)
            )

            result = query.all()

            if len(result) == 1:

                return {
                    'status': 'success',
                    'data': result[0],
                }

            else:

                return {
                    'status': 'error',
                    'data': result,
                }

        except Exception as e:

            session.rollback()

            return {
                'status': 'error',
                'exception': e,
            }

    def set_values_to_insert(self, item, sequence, iftenombre_data):
        logger.info("Asignando valores para insertar")
        # Asignación de valores
        capclave = sequence  # Valor de la secuencia (seq_capsula) para el campo "capclave"
        capautor = 12390  # Valor por defecto
        capfcaptura = datetime.now()
        capfcapsula = item.news_publication_date  # Fecha nota
        capmodif = 12390  # Valor por defecto
        capfmodif = item.news_modified_date  # Fecha update nota
        capambito = iftenombre_data['data'][3]  # fnoambito from iftenombre
        capestado = iftenombre_data['data'][2]  # fnoestado from iftenombre
        captipomedio = 2  # Tipo medio (valor por defecto 2)
        capmedio = iftenombre_data['data'][1]  # fnomedio from iftenombre (valor 8 = web)
        capnombre = iftenombre_data['data'][0]  # Clave del medio (fnoclave from iftenombre)
        capclasificacion = 1  # Género (valor por defecto 1 = información)
        capterminado = 'S'  # Valor por defecto
        captitulo = item.news_head_title  # Título de la nota
        capcomentario = item.news_author  # Nombre del periodista, articulista o columnista (autor de la nota)
        cappersistent = 'S'  # Valor por defecto
        captextcomp = item.news_content  # Contenido de la nota
        captextsint = item.news_content  # Se guarda el mismo contenido de captextcomp
        caporigen = 'A'  # Valor por defecto
        captestigo = ['Y' if item.news_cve_medio in (2111, 12487, 11947) else 'N'][0]  # Valor por defecto
        capurloriginal = item.news_url  # URL de la nota

        return (capclave, capautor, capfcaptura, capfcapsula, capmodif, capfmodif, capambito, capestado,
                captipomedio, capmedio, capnombre, capclasificacion, capterminado, captitulo, capcomentario,
                cappersistent, captextcomp, captextsint, caporigen, captestigo, capurloriginal)

    def update_title_or_content(self, session, item, result, session_clie = None):

        data = {
            'CAPFMODIF' : item.news_modified_date,
            'CAPTESTIGO' : 'N',
            'CAPTENDENCIA2' : None,
            'CAPINTENTOS' : '0',
            'CAPNOMBRE' : item.news_cve_medio,
        }

        if item.news_head_title != result.CAPTITULO:
            data['CAPTITULO'] = item.news_head_title

        if item.news_content != result.CAPTEXTCOMP:
            data['CAPTEXTCOMP'] = item.news_content
            data['CAPTEXTSINT'] = item.news_content

        if 'CAPTEXTCOMP' in data or 'CAPTITULO' in data:
            try:
                logger.info("Actualizando registro")
                update_content_or_title = (
                    update(IcapsulaData)
                    .values(data)
                    .where(
                        (IcapsulaData.CAPCLAVE == result.CAPCLAVE) &
                        (IcapsulaData.CAPNOMBRE == item.news_cve_medio) &
                        (IcapsulaData.CAPURLORIGINAL == item.news_url)
                    )
                )

                if self.testing_enabled:
                    session.execute(update_content_or_title)
                    session.commit()
                else:
                    session.execute(update_content_or_title)
                    logger.info("Actualizando registro en Clientes")
                    session_clie.execute(update_content_or_title)
                    session_clie.commit()
                    session.commit()

                return {
                    'status' : 'success',
                    'data' : data
                }

            except Exception as UpdtException:

                logger.exception("Error al actualizar el registro: %s", UpdtException)
                session.rollback()

                return {
                    'status' : 'error',
                    'data' : data,
                    'exception' : UpdtException
                }
        else:

            return {
                'status' : 'no_changes'
            }

