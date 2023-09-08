""" behavior module """
import csv
import logging
from io import StringIO
from plone.app.dexterity.behaviors.metadata import DCFieldProperty
from plone.app.dexterity.behaviors.metadata import MetadataBase
from plone.dexterity.interfaces import IDexterityContent
from plone.rfc822.interfaces import IPrimaryFieldInfo
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from eea.api.dataconnector.queryparser import computeDataQuery
from eea.api.dataconnector.queryfilter import filteredData
from .interfaces import IConnectorDataParameters
from .interfaces import IDataConnector
from .interfaces import IDataProvider
from .interfaces import IDataVisualization
from .interfaces import IMapVisualization
from .interfaces import ITableauVisualization
from .interfaces import IFileDataProvider
from .interfaces import IElasticConnector

logger = logging.getLogger(__name__)


@implementer(IDataConnector)
@adapter(IDexterityContent)
class DataConnector(MetadataBase):
    """Allow data connectivity to discodata

    See http://discomap.eea.europa.eu/App/SqlEndpoint/Browser.aspx
    """

    endpoint_url = DCFieldProperty(IDataConnector["endpoint_url"])
    sql_query = DCFieldProperty(IDataConnector["sql_query"])
    parameters = DCFieldProperty(IDataConnector["parameters"])
    required_parameters = DCFieldProperty(
        IDataConnector["required_parameters"]
    )
    collate = DCFieldProperty(IDataConnector["collate"])
    readme = DCFieldProperty(IDataConnector["readme"])


@implementer(IDataProvider)
@adapter(IFileDataProvider, IBrowserRequest)
class DataProviderForFiles(object):
    """Behavior implementation for content types with a File primary field"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def provided_data(self):
        """provided data"""
        field = IPrimaryFieldInfo(self.context)

        if not field.value:
            return []

        text = field.value.data
        f = StringIO(text.decode("utf-8"))
        try:
            reader = csv.reader(f)
        except Exception:
            return []

        rows = list(reader)

        if not rows:
            return []

        keys = rows[0]
        data = []

        for index, row in enumerate(rows[1:]):
            data.append({})
            for (i, k) in enumerate(keys):
                data[index][k] = row[i]

        data_query = computeDataQuery(self.request)

        return {
            "results": filteredData(data, data_query),
            "metadata": {},
        }


@implementer(IDataProvider)
@adapter(IElasticConnector, IBrowserRequest)
class DataProviderForElasticConnectors(object):
    """Behavior implementation for CT with elastic_csv_widget field"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def provided_data(self):
        """provided data"""
        
        # Fetch data from Elasticsearch (pseudo-code)
        es_data = self.fetch_data_from_elasticsearch()
        
        # Create table data
        table_data = self.create_table_data(es_data)
        
        return {
            "results": table_data,
            "metadata": {},  # Add metadata if needed
        }
        
    def fetch_data_from_elasticsearch(self):
        # Implement fetching logic here, returning raw data from ES
        pass
        
    def create_table_data(self, data):
        # Process the raw ES data as required and return it
        pass


class DataVisualization(MetadataBase):
    """Standard Fise Metadata adaptor"""

    visualization = DCFieldProperty(IDataVisualization["visualization"])


class MapViewVisualization(MetadataBase):
    """Standard ArcGIS Map View adaptor"""

    map_visualization_data = DCFieldProperty(
        IMapVisualization["map_visualization_data"]
    )


class TableauViewVisualization(MetadataBase):
    """Standard Tableau View adaptor"""

    tableau_visualization = DCFieldProperty(
        ITableauVisualization["tableau_visualization"]
    )


class ConnectorDataParameters(MetadataBase):
    """Provide predefined connector data for parameters"""

    # data_parameters = DCFieldProperty(
    #     IConnectorDataParameters['data_parameters'])
    data_query = DCFieldProperty(IConnectorDataParameters["data_query"])


class ElasticConnectorWidget(MetadataBase):
    """Build csv data from ES data"""

    elastic_csv_widget = DCFieldProperty(
        IElasticConnector["elastic_csv_widget"]
    )
