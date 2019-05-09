import xarray as xr


class Seismic(object):
    def __init__(self, data):
        self._obj = xr.DataArray(data)
        
    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self._obj, attr)
    
    def __getitem__(self, item):
        return self._obj[item]
    
    def __repr__(self):
        return self._obj.__repr__()
    
    def __str__(self):
        return "Seismic"