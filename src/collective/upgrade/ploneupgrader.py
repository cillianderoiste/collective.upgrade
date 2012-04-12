from zope import component

from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import interfaces as plone_ifaces

from collective.upgrade import upgrader

_marker = object()


class PloneUpgrader(upgrader.PortalUpgrader):
    component.adapts(plone_ifaces.IPloneSiteRoot)

    def upgrade(self, **kw):
        # May fix the profile version
        migration = getToolByName(self.context, 'portal_migration')
        migration.getInstanceVersion()

        return super(PloneUpgrader, self).upgrade(**kw)

    def upgradeProfile(self, profile_id,
                       enable_link_integrity_checks=_marker, **kw):
        upgradeProfile = super(PloneUpgrader, self).upgradeProfile

        properties = getToolByName(self.context, 'portal_properties')
        orig = properties.site_properties.getProperty(
            'enable_link_integrity_checks', _marker)
        if enable_link_integrity_checks is not _marker:
            properties.site_properties.manage_changeProperties(
                enable_link_integrity_checks=enable_link_integrity_checks)
        try:
            upgradeProfile(profile_id, **kw)
        finally:
            if enable_link_integrity_checks is not _marker:
                if orig is _marker:
                    properties.site_properties._delPropValue(
                        enable_link_integrity_checks)
                else:
                    properties.site_properties.manage_changeProperties(
                        enable_link_integrity_checks=orig)

    def isProfileInstalled(self, profile_id):
        installed = super(PloneUpgrader, self).isProfileInstalled(profile_id)
        if installed:
            return installed

        product, profile = profile_id.split(':', 1)
        qi = getToolByName(self.context, 'portal_quickinstaller')
        return qi.isProductInstalled(product)
