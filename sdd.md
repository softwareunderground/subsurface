# Subsurface

DataHub for geoscientific data in Python. Two main purposes:

+ Unify geometric data into data objects (using numpy arrays as memory representation) that all the packages of the stack understand

+ Basic interactions with those data objects:
    + Write/Read
    + Categorized/Meta data
    + Visualization

## Requirements

+ The core of the package has to be **light**
+ I/O **has** to happen at the level of **primary structures**. Once the primary structure has been exported/imported we can keep going up the pile (i.e. elements, geological objects, etc)

## Optional libraries:
+ I/O 
    + segyio
    + welly
    + rasterio
    + ...
+ Visualization
    + Matplotlib
    + pyvista
+ Standard formats
    + OMF
    + geoh5py

## Data Levels:

**Human**

    geological_format -> Additional context/meta information about the data

    +-----------+

    geological_object -> Elements that represent some geological concept. E.g: faults, seismic

    +-----------+

    +-----------+

    element -> type of geometric object: PointSet, TriSurf, LineSet, Tetramesh

    +-----------+

    primary_structures -> Set of arrays that define a geometric object

    +-----------+

    +-----------+

    Dataframe/Xarray -> Label numpy.arrays

    +-----------+

    numpy.array -> Memory allocation

**Computer**

## Primary Structures definitions:

### Unstructured: NumPy, Pandas
Basic components:

- vertex:  NDArray[(Any, 3), FloatX]: XYZ point data
- cells: NDArray[(Any, ...), IntX]: Combination of vertex that create different geometric elements
- attributes: NDArray[(Any, ...), FloatX]: Number associated to an element

Depending on the shape of `edge` the following unstructured elements can be create:
- cells NDArray[(Any, 0), IntX] or NDArray[(Any, 1), IntX] -> *Point cloud*. E.g. Outcrop scan with lidar 
- cells NDArray[(Any, 2), IntX] -> *Lines*. E.g. Borehole
- cells NDArray[(Any, 3), IntX] -> *Mesh*. E.g surface-DEM Topography
- cells NDArray[(Any, 4), IntX] 
    - -> *tetrahedron*
    - -> *quadrilateral (or tetragon)* UNSUPPORTED?
- cells NDArray[(Any, 8), IntX] -> *Hexahedron: Unstructured grid/Prisms*


### Structured: NumPy, XArray
The main distinction from unstructures is that we do not need to provide cells since that can be determined by the order of the points (vertex) and the description of the coordinate


Basic components (XArray lingo):
- DataSets: Number associated to an structured element
- Coordinates: Define the **center** of the element


Depending on the number of coordinates of the XArray

- 2D: *structured surface*
    - defined by 1 array per axis (two axis in 2D). Usually axis are parallel to XY  but technically the don't have to. Also they can be rotated
    
    - Z is function of XY. I.e could be seen as simply another attribute (DataArray)


- 3D: *Structured grid*:
    - defined by 1 array per axis (two axis in 2D). Usually axis are perpendicular to Cartesian but technically the don't have to
    - Optional: Rotation

- **Special case:** *Uniform grid*. It is a structured grid with all spacing constant. Defined by::
    
    - Extent, resolution or
    - origin and spacing
    - Rotation?