from ..seismic import Seismic
import segyio

def from_segy(filepath:str) -> Seismic:
    """Create a Seismic data object from a SEGY file.
    
    Args:
        filepath (str): Filepath to the SEGY file.
    
    Returns:
        Seismic: Seismic data object based on xarray.DataArray.
    """
    with segyio.open(filepath) as sf:
        sf.mmap()  # memory mapping
        xlines = sf.xlines
        ilines = sf.ilines
        samples = sf.samples
        header = sf.bin
    
    coords = [ 
        ("ilines", ilines), 
        ("xlines", xlines),
        ("samples", samples)
    ]

    cube = segyio.tools.cube(filepath)
    return Seismic(cube, coords=coords)