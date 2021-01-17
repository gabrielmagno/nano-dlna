from gi.repository import GLib, GUPnP


def device_available(cp, proxy):
    print("Found " + proxy.get_friendly_name())


#ctx = GUPnP.Context.new(None, "wlp3s0", 0)
ctx = GUPnP.Context.new("wlp3s0", 0)
cp = GUPnP.ControlPoint.new(ctx, "upnp:rootdevice")
cp.set_active(True)
cp.connect("device-proxy-available", device_available)

GLib.MainLoop().run()
