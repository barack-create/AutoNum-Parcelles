# -*- coding: utf-8 -*-
from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon
import os

from .parcel_numbering_algorithm import ParcelNumberingAlgorithm


class ParcelNumberingProvider(QgsProcessingProvider):

    def id(self):
        return "cadastre_tools"

    def name(self):
        return "Outils Cadastre"

    def icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QgsProcessingProvider.icon(self)

    def loadAlgorithms(self):
        self.addAlgorithm(ParcelNumberingAlgorithm())
