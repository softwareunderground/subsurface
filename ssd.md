# Subsurface

DataHub for geoscientific data in Python. Two main purposes:

+ Unify geometric data into data objects (using numpy arrays as memory representation) that all the packages of the stack understand

+ Basic interactions with those data objects:
    + Write/Read
    + Categorized/Meta data
    + Visualization

## Requirements

+ The core of the package has to be light
+ Many optional libraries:
    + Visualization
    + I/O
    + Standard formats

## Data Structures definitions:

### Unstructured: NumPy, Pandas
Basic components:

- vertex:  NDArray[(Any, 3), FloatX]: XYZ point data
- edges: NDArray[(Any, ...), IntX]: Combination of vertex that create different geometric elements
- attributes: NDArray[(Any, ...), FloatX]: Number associated to an element

Depending on the shape of `edge` the following unstructured elements can be create:
- edges NDArray[(Any, 0), IntX] or NDArray[(Any, 1), IntX] -> *Point cloud*. E.g. Outcrop scan with lidar 
- edges NDArray[(Any, 2), IntX] -> *Lines*. E.g. Borehole
- edges NDArray[(Any, 3), IntX] -> *Triangle*. E.g surface-DEM Topography
- edges NDArray[(Any, 4), IntX] -> *quadrilateral (or tetragon)*
- edges NDArray[(Any, 12), IntX] -> *tetrahedron*
- edges NDArray[(Any, 32), IntX] -> *Unstructured grid/Prisms*


### Structured: NumPy, XArray

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