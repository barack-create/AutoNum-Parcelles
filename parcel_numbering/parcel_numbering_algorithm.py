# -*- coding: utf-8 -*-
"""
Algorithme QGIS Processing : numérote une couche de parcelles (polygones)
de façon consécutive, par plus proche voisin (parcours glouton, départ
nord-ouest).
"""

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterString,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFeatureSink,
    QgsField,
    QgsFields,
    QgsFeature,
    QgsFeatureSink,
    QgsWkbTypes,
    QgsProcessingException,
)


class ParcelNumberingAlgorithm(QgsProcessingAlgorithm):

    INPUT = "INPUT"
    FIELD_NAME = "FIELD_NAME"
    START_NUMBER = "START_NUMBER"
    DIGITS = "DIGITS"
    OUTPUT = "OUTPUT"

    def tr(self, string):
        return QCoreApplication.translate("ParcelNumberingAlgorithm", string)

    def createInstance(self):
        return ParcelNumberingAlgorithm()

    def name(self):
        return "numeroter_parcelles_proximite"

    def displayName(self):
        return self.tr("Numéroter les parcelles")

    def group(self):
        return self.tr("Cadastre")

    def groupId(self):
        return "cadastre"

    def shortHelpString(self):
        return self.tr(
            "Attribue un numéro consécutif à chaque parcelle (entité polygonale) "
            "d'une couche, par plus proche voisin : le parcours démarre à la "
            "parcelle la plus au nord-ouest, puis avance toujours vers la "
            "parcelle non numérotée la plus proche.\n\n"
            "Le résultat est une nouvelle couche identique à l'entrée, avec un champ "
            "supplémentaire contenant le numéro attribué.\n\n"
            "Remarque : pour des couches très volumineuses (plusieurs milliers "
            "d'entités), ce mode (en O(n²)) peut être lent."
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr("Couche de parcelles (polygones)"),
                [QgsProcessing.TypeVectorPolygon],
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.FIELD_NAME,
                self.tr("Nom du champ à créer pour le numéro"),
                defaultValue="NUM_PARC",
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.START_NUMBER,
                self.tr("Numéro de départ"),
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=1,
                minValue=0,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.DIGITS,
                self.tr("Nombre de chiffres (1 = pas de zéro, 2 = 01, 3 = 001, 4 = 0001...)"),
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=4,
                minValue=1,
                maxValue=10,
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr("Parcelles numérotées"),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        field_name = self.parameterAsString(parameters, self.FIELD_NAME, context)
        start_number = self.parameterAsInt(parameters, self.START_NUMBER, context)
        digits = self.parameterAsInt(parameters, self.DIGITS, context)

        if source is None:
            raise QgsProcessingException(self.tr("Couche d'entrée invalide."))

        # Construction des champs de sortie : champs existants + nouveau champ numéro
        out_fields = QgsFields(source.fields())
        if out_fields.indexFromName(field_name) != -1:
            out_fields.remove(out_fields.indexFromName(field_name))
        out_fields.append(QgsField(field_name, QVariant.String, len=10))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            out_fields,
            QgsWkbTypes.multiType(source.wkbType()),
            source.sourceCrs(),
        )

        total_features = source.featureCount()
        if total_features == 0:
            feedback.pushWarning(self.tr("La couche d'entrée ne contient aucune entité."))
            return {self.OUTPUT: dest_id}

        if total_features > 3000:
            feedback.pushWarning(
                self.tr(
                    "Attention : {0} entités détectées. Le calcul du plus proche "
                    "voisin est en O(n²) et peut être lent sur de grandes couches."
                ).format(total_features)
            )

        # 1. Charger toutes les entités et calculer leurs centroïdes
        feedback.pushInfo(self.tr("Lecture des entités et calcul des centroïdes..."))
        features = []
        centroids = []
        for feat in source.getFeatures():
            if feedback.isCanceled():
                return {}
            geom = feat.geometry()
            if geom is None or geom.isEmpty():
                continue
            c = geom.centroid().asPoint()
            features.append(feat)
            centroids.append((c.x(), c.y()))

        n = len(features)
        if n == 0:
            feedback.pushWarning(self.tr("Aucune géométrie valide trouvée."))
            return {self.OUTPUT: dest_id}

        order = self._order_nearest_neighbor(centroids, feedback)

        if order is None:
            return {}

        # 4. Attribution des numéros et écriture des entités de sortie
        feedback.pushInfo(self.tr("Écriture de la couche numérotée..."))
        numero = start_number
        for idx in order:
            if feedback.isCanceled():
                return {}
            src_feat = features[idx]
            new_feat = QgsFeature(out_fields)
            new_feat.setGeometry(src_feat.geometry())
            attrs = src_feat.attributes()
            attrs.append(str(numero).zfill(digits))
            new_feat.setAttributes(attrs)
            sink.addFeature(new_feat, QgsFeatureSink.FastInsert)
            numero += 1

        feedback.pushInfo(self.tr("Terminé : {0} parcelles numérotées.").format(n))

        return {self.OUTPUT: dest_id}

    def _order_nearest_neighbor(self, centroids, feedback):
        """Parcours glouton du plus proche voisin, départ nord-ouest."""
        n = len(centroids)
        visited = [False] * n

        # Point de départ : la parcelle la plus au nord-ouest
        # (y maximal, x minimal -> on minimise x - y)
        start_idx = min(range(n), key=lambda i: centroids[i][0] - centroids[i][1])

        order = [start_idx]
        visited[start_idx] = True
        current = start_idx

        feedback.pushInfo(self.tr("Calcul de l'ordre par plus proche voisin..."))

        for step in range(1, n):
            if feedback.isCanceled():
                return None
            cx, cy = centroids[current]
            best_idx = -1
            best_dist = None
            for j in range(n):
                if visited[j]:
                    continue
                jx, jy = centroids[j]
                dist = (jx - cx) ** 2 + (jy - cy) ** 2
                if best_dist is None or dist < best_dist:
                    best_dist = dist
                    best_idx = j
            order.append(best_idx)
            visited[best_idx] = True
            current = best_idx
            feedback.setProgress(int(100 * step / n))

        return order
