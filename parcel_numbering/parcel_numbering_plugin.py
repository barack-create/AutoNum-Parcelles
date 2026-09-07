# -*- coding: utf-8 -*-
from qgis.core import QgsApplication
from .parcel_numbering_provider import ParcelNumberingProvider


class ParcelNumberingPlugin:
    """Classe principale du plugin : s'enregistre auprès de QGIS Processing."""

    def __init__(self, iface):
        self.iface = iface
        self.provider = None

    def initGui(self):
        self.provider = ParcelNumberingProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        if self.provider is not None:
            QgsApplication.processingRegistry().removeProvider(self.provider)
