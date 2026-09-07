# -*- coding: utf-8 -*-
"""
Plugin QGIS : AutoNum Parcelles
"""


def classFactory(iface):
    from .parcel_numbering_plugin import ParcelNumberingPlugin
    return ParcelNumberingPlugin(iface)
