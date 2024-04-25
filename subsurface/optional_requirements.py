def require_omf():
    try:
        import omfvista
    except ImportError:
        raise ImportError("The omfvista package is required to run this function.")
    return omfvista


def require_rasterio():
    try:
        import rasterio
    except ImportError:
        raise ImportError("The rasterio package is required to run this function.")
    return rasterio


def require_pyvista():
    try:
        import pyvista
    except ImportError:
        raise ImportError("The pyvista package is required to run this function.")
    return pyvista


def require_imageio():
    try:
        import imageio
    except ImportError:
        raise ImportError("The imageio package is required to run this function.")
    return imageio


def require_geopandas():
    try:
        import geopandas as gpd
    except ImportError:
        raise ImportError("The geopandas package is required to run this function.")
    return gpd
