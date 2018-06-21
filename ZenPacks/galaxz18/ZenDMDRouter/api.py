import json
from OFS.Application import Application
from transaction import commit
from Products.ZenModel.DataRoot import DataRoot
from Products.ZenModel.ZentinelPortal import ZentinelPortal
from Products.ZenUtils.Ext import DirectRouter, DirectResponse
from Products.ZenUtils.Utils import setLogLevel
from Products.Zuul import getFacade, listFacades
from Products.Zuul import info, marshal


class ZenDMDRouter(DirectRouter):
    def executeScript(self, script, commit=False):
        try:
            results = {}
            exec(script, get_zendmd_globals(self.context), results)
        except Exception as e:
            return DirectResponse.fail(msg=str(e))

        results.pop("_", None)

        try:
            return DirectResponse.succeed(**marshal(info(results)))
        except Exception as e:
            return DirectResponse.fail(msg=str(e))


def get_zendmd_globals(context):
    zendmd_globals = {
        "context": context,
        "commit": commit,
        "sync": context._p_jar.sync,
        "setLogLevel": setLogLevel,
        "listFacades": listFacades,
        "getFacade": getFacade,
    }

    app, zport, dmd = None, None, None

    if isinstance(context, Application):
        app = context
        zport = app.zport
        dmd = zport.dmd
    elif isinstance(context, ZentinelPortal):
        zport = context
        dmd = zport.dmd
    elif isinstance(context, DataRoot):
        dmd = context
    else:
        dmd = context.dmd.primaryAq()

    if dmd:
        zendmd_globals.update({
            "app": app,
            "zport": zport,
            "dmd": dmd,
            "devices": dmd.Devices,
            "find": dmd.Devices.findDevice})

    return zendmd_globals
