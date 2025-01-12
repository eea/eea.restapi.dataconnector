import transaction
from zope.lifecycleevent import modified
from Products.ZCatalog.ProgressHandler import ZLogHandler
from plone.app.uuid.utils import uuidToObject
from urllib.parse import urlparse
from plone.uuid.interfaces import IUUID
from plone.restapi.deserializer.utils import path2uid

def getLink(path):
    """
      Get link
      """

    URL = urlparse(path)

    if URL.netloc.startswith('localhost') and URL.scheme:
        return path.replace(URL.scheme + "://" + URL.netloc, "")
    return path

def upgrade_visualizations(portal):
    """Upgrade step to handle provider_url in visualizations"""

    i = 0
    brains = portal.portal_catalog(portal_type="viz")
    pghandler = ZLogHandler(100)
    pghandler.init("Upgrade visualizations", len(brains))

    for idx, brain in enumerate(brains):
        pghandler.report(idx)
        try:
            obj = brain.getObject()
        except Exception as e:
            continue  # Skip objects that cannot be retrieved

        viz = getattr(obj, 'visualization', None)

        if not viz or not isinstance(viz, dict):
            continue

        provider_url = viz.get('provider_url', None)

        if provider_url and 'resolve_uid' not in provider_url: 
            uuid =path2uid(
            context=obj, link=getLink(provider_url))
            viz['provider_url'] = uuid;
            obj.visualization=viz;
            modified(obj)
            i=i+1;

        if not i % 100:
            transaction.commit()

    pghandler.finish()
    transaction.commit()
