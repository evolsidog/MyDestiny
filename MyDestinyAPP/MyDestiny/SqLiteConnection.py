#!/usr/bin/python
# -*- coding: UTF8 -*-
#
import sqlite3
from constants import *


class SqLiteConnection():
    """ Conector para conectarse a SqLite
Atributo: Directorio de la base de datos
    """

    SID = None
    connection = None

    def __init__(self, bd=PATH_DB):
        self.bd = bd
        self.connection = ''

    def _open(self):
        """Open connection"""
        self.connection = sqlite3.connect(self.bd)

    def _close(self):
        """Close connection"""
        self.connection.close()

    def connector(self):
        self._open()
        return self.connection

    def execute_query(self, query):
        """Execute a query
        Args: query
        Returns: A handler with the query results
        """
        self._open()
        try:
            con = self.connection
            dbHandler = con.cursor()
            dbHandler.execute(query)
            con.commit()
            result = dbHandler.fetchall()
            self._close()
            return result
        except Exception as e:
            print e
            self._close()
            return 1
