<!-- TITLE: REX Data Format -->
<!-- SUBTITLE: Specification -->

# REX data format v1

The Robotic Eyes eXplorer data format (rex) is designed to store REX-relevant information efficiently in order to
optimize the data transfer between a mobile client and a server.  The suffix of the rex file is chosen to be **.rex**.

The rex format can store up to 2^16 different data blocks (65535), where one specific data block stores a certain type
of data. This data can vary from geospatial data to 3D meshes or any binary-typed data.

The rex format stores all the information in binary representation (big endian). This allows for optimized data storage
and performant read/write operations. For instance, reading an OBJ file takes 20x more time than reading the same data
as rex.

Although the coordinates which are user facing have Z in upward direction, the REX stores the coordinates in
a form that Y is facing towards up.

## Related formats

A file format which is related to the rex format is the
[glTF](https://github.com/KhronosGroup/glTF/blob/master/specification/README.md) format.

Another similar file format is the [OpenCTM](http://openctm.sourceforge.net) specification. This is pretty much
tailored to 3D meshes only but proposes a nice compression algorithm.

## Coordinate system

Coordinate systems are the most crucial parts in computer graphics and computer vision. Every application may have its
own definition of the coordinate system, so does REX.

The geometry in REX is defined by a right-handed 3D
[Cartesian coordinate system](https://en.wikipedia.org/wiki/Cartesian_coordinate_system) as shown in the figure below.

![Right handed coordinates](/doc/right-handed.png?raw=true "REX coordinate system")

Please make sure that your input geometry is transformed according to our coordinate system specification. As an example,
if you export FBX from Revit directly, no transformation is required because all the coordinates are already in the
required right-handed system. Other systems may require a transformation (see the transformation option in `rex-importer`).

Please note, that the y-coordinate is pointing upwards, which means that the "height" in CAD is encoded as `y` in the
REX file format. However, if you position the REX model in the real world, the `y` coordinate is pointing to the sky.

The triangle orientation is required to be counter-clockwise (CCW), see the example in the data directory. Here is a
simple example which shows the `coordsys.obj` file from the `data` directory in the viewer, and in real world with the
REX Go app.

![Coordinate example](/doc/coordinate_example.png?raw=true "Coordinate example")

### SketchUp

[SketchUp](https://www.sketchup.com/) has a right-handed coordinate system with a 90 degrees rotation around the `x` axis.
This means that `z` is pointing upwards and `y` is pointing backwards. We have created a cube in SketchUp where the green
face is pointing towards the user and the red face is pointing to the right side (see screenshot below).

We have developed a SketchUp plugin which automatically converts a SketchUp model into a REX file. You can download the
plugin [here](https://extensions.sketchup.com/en/content/rex-exporter).

## File layout

### General file structure

The rex format starts with a fixed header block, followed by a coordinate system block.
A list of different data blocks can follow. The rex can store multiple different data blocks in
one file.

| **name**                | **description**                       |
|-------------------------|---------------------------------------|
| File header block       | header information (meta-data)        |
| Coordinate system block | coordinate system for all stored data |
| Data block 1            | data                                  |
| Data block 2            | data                                  |
| ...                     | ...                                   |
| Data block n            | data                                  |


### File header block

| **size [bytes]** | **name**       | **type** | **description**           |
|------------------|----------------|----------|---------------------------|
| 4                | magic          | string   | REX1                      |
| 2                | version        | uint16   | file version              |
| 4                | CRC32          | uint32   | crc32 (auto calculated)   |
| 2                | nrOfDataBlocks | uint16   | number of data blocks     |
| 2                | startData      | uint16   | start of first data block |
| 8                | sizeDataBlocks | uint64   | size of all data blocks   |
| 42               | reserved       | -        | reserved                  |

### Coordinate system block

| **size [bytes]** | **name** | **type** | **description**                     |
|------------------|----------|----------|-------------------------------------|
| 4                | srid     | uint32   | spatial reference system identifier |
| 2+sz             | authName | string   | name of the used system             |
| 4                | offsetX  | float    | global x-offset                     |
| 4                | offsetY  | float    | global y-offset                     |
| 4                | offsetZ  | float    | global z-offset                     |

### Data block

Every data block has a general data header block which stores general information.
The specific data block can still contain further header information, depending on the data block itself.

| **name**          | **description**    |
|-------------------|--------------------|
| Data header block | header information |
| Data block        | data               |

#### Data header block

| **size [bytes]** | **name** | **type** | **description**                  |
|------------------|----------|----------|----------------------------------|
| 2                | type     | uint16   | data type                        |
| 2                | version  | uint16   | version for this data block      |
| 4                | size     | uint32   | data block size (without header) |
| 8                | dataId   | uint64   | id which is used in the database |

The currently supported data block types are as follows. Please make sure that the IDs are not reordered.

Total size of the header is **16 bytes**.

| **Id**   | **Type**           | **Description**                                                     | **C**                | **Go**               | **C#**             |
| -------- | ------------------ | ------------------------------------------------------------------- | -------------------- | -------------------- | --------           |
| 0        | LineSet            | A list of vertices which get connected by line segments             | :heavy_check_mark:   | :heavy_check_mark:   | :heavy_check_mark: |
| 1        | Text               | A position information and the actual text                          | :heavy_check_mark:   | :heavy_check_mark:   | :heavy_check_mark: |
| 2        | PointList          | A list of 3D points with color information (e.g. point cloud)       | :heavy_check_mark:   | :heavy_check_mark:   | :heavy_check_mark: |
| 3        | Mesh               | A triangle mesh datastructure                                       | :heavy_check_mark:   | :heavy_check_mark:   | :heavy_check_mark: |
| 4        | Image              | A single of arbitrary format can be stored in this block            | :heavy_check_mark:   | :heavy_check_mark:   | :heavy_check_mark: |
| 5        | MaterialStandard   | A standard (mesh) material definition                               | :heavy_check_mark:   | :heavy_check_mark:   | :heavy_check_mark: |
| 6        | SceneNode          | A wrapper around a data block which can be used in the scenegraph   | :x:                  | :heavy_check_mark:   | :x:                |
| 7        | Track              | A track is a tracked position and orientation of an AR device       | :x:                  | :heavy_check_mark:   | :x:                |

Please note that some of the data types offer a LOD (level-of-detail) information. This value
can be interpreted as 0 being the highest level. As data type we use 32bit for better memory alignment.

#### DataType LineSet (0)

| **size [bytes]** | **name**     | **type** | **description**               |
|------------------|--------------|----------|-------------------------------|
| 4                | red          | float    | red channel                   |
| 4                | green        | float    | green channel                 |
| 4                | blue         | float    | blue channel                  |
| 4                | alpha        | float    | alpha channel                 |
| 4                | nrOfVertices | uint32   | number of vertices            |
| 4                | x0           | float    | x-coordinate of first vertex  |
| 4                | y0           | float    | y-coordinate of first vertex  |
| 4                | z0           | float    | z-coordinate of first vertex  |
| 4                | x1           | float    | x-coordinate of second vertex |
| ...              |              |          |                               |

Alpha value of `1.0` means fully opaque.

#### DataType Text (1)

This data type allows to position a (colored) text somewhere in space. The unit
is again meters.

| **size [bytes]** | **name**  | **type** | **description**                   |
|------------------|-----------|----------|-----------------------------------|
| 4                | red       | float    | red channel                       |
| 4                | green     | float    | green channel                     |
| 4                | blue      | float    | blue channel                      |
| 4                | alpha     | float    | alpha channel                     |
| 4                | positionX | float    | x-coordinate of the position      |
| 4                | positionY | float    | y-coordinate of the position      |
| 4                | positionZ | float    | z-coordinate of the position      |
| 4                | fontSize  | float    | font size in font units (e.g. 24) |
| 2+sz             | text      | string   | text for the label                |

Alpha value of `1.0` means fully opaque.

#### DataType PointList (2)

This data type can be used to store a set of points (e.g. colored point clouds).
The number of colors can be zero. If this is the case the
points are rendered with a pre-defined color (e.g. white). If color is provided
the number of color entries must fit the number of vertices (i.e. every point needs
to have an RGB color).

| **size [bytes]** | **name**     | **type** | **description**                     |
|------------------|--------------|----------|-------------------------------------|
| 4                | nrOfVertices | uint32   | number of vertices                  |
| 4                | nrOfColors   | uint32   | number of colors                    |
| 4                | x            | float    | x-coordinate of first vertex        |
| 4                | y            | float    | y-coordinate of first vertex        |
| 4                | z            | float    | z-coordinate of first vertex        |
| 4                | x            | float    | x-coordinate of second vertex       |
| ...              |              |          |                                     |
| 4                | red          | float    | red component of the first vertex   |
| 4                | green        | float    | green component of the first vertex |
| 4                | blue         | float    | blue component of the first vertex  |
| 4                | red          | float    | red component of the second vertex  |
| ...              |              |          |                                     |


#### DataType Mesh (3)

##### Mesh header

The offsets in this block refer to the index of the beginning of this data block (this means the position of the lod
field, not the general data block header!). If one needs to access from the global REX stream, the offset of the
mesh block must be added.

| **size [bytes]** | **name**       | **type** | **description**                                                  |
|------------------|----------------|----------|------------------------------------------------------------------|
| 2                | lod            | uint16   | level of detail for the given geometry                           |
| 2                | maxLod         | uint16   | maximal level of detail for given geometry                       |
| 4                | nrOfVtxCoords  | uint32   | number of vertex coordinates                                     |
| 4                | nrOfNorCoords  | uint32   | number of normal coordinates (can be zero)                       |
| 4                | nrOfTexCoords  | uint32   | number of texture coordinates (can be zero)                      |
| 4                | nrOfVtxColors  | uint32   | number of vertex colors (can be zero)                            |
| 4                | nrTriangles    | uint32   | number of triangles                                              |
| 4                | startVtxCoords | uint32   | start vertex coordinate block (relative to mesh block start)     |
| 4                | startNorCoords | uint32   | start vertex normals block (relative to mesh block start)        |
| 4                | startTexCoords | uint32   | start of texture coordinate block (relative to mesh block start) |
| 4                | startVtxColors | uint32   | start of colors block (relative to mesh block start)             |
| 4                | startTriangles | uint32   | start triangle block for vertices (relative to mesh block start) |
| 8                | materialId     | uint64   | id which refers to the corresponding material block in this file |
| 2                | string size    | uint16   | size of the following string name                                |
| 74               | name           | string   | name of the mesh (this is user-readable)                         |

It is assumed that the mesh data is vertex-oriented, so that additional properties such as color, normals, or
texture information is equally sized to the nrOfVtxCoords. If not available the number should/can be 0.

The mesh references a separate material block which is identified by the materialId (dataId of the material block).
Each DataMesh can only have one material block. This is similar to the `usemtl` in the OBJ file format. **If the
materialId is `0x7fffffffffffffffL`, then no material is available.**

The mesh header size is fixed with **128** bytes.

##### Vertex coordinates block

| **size [bytes]** | **name** | **type** | **description**               |
|------------------|----------|----------|-------------------------------|
| 4                | x        | float    | x-coordinate of first vertex  |
| 4                | y        | float    | y-coordinate of first vertex  |
| 4                | z        | float    | z-coordinate of first vertex  |
| 4                | x        | float    | x-coordinate of second vertex |
| ...              |          |          |                               |

##### Normals coordinates block (optional)

| **size [bytes]** | **name** | **type** | **description**                   |
|------------------|----------|----------|-----------------------------------|
| 4                | nx       | float    | x-coordinate of the first normal  |
| 4                | ny       | float    | y-coordinate of the first normal  |
| 4                | nz       | float    | z-coordinate of the first normal  |
| 4                | nx       | float    | x-coordinate of the second normal |
| ...              |          |          |                                   |

##### Texture coordinates block (optional)

| **size [bytes]** | **name** | **type** | **description**                          |
|------------------|----------|----------|------------------------------------------|
| 4                | u        | float    | u-component of first texture coordinate  |
| 4                | v        | float    | v-component of first texture coordinate  |
| 4                | u        | float    | u-component of second texture coordinate |
|                  |          |          |                                          |

##### Colors block (optional)

| **size [bytes]** | **name** | **type** | **description**                     |
|------------------|----------|----------|-------------------------------------|
| 4                | red      | float    | red component of the first vertex   |
| 4                | green    | float    | green component of the first vertex |
| 4                | blue     | float    | blue component of the first vertex  |
| 4                | red      | float    | red component of the second vertex  |
| ...              |          |          |                                     |

##### Triangle block

This is a list of integers which form one triangle. Please make sure that normal and texture
coordinates are inline with the vertex coordinates. One index refers to the same normal and texture position.
**The triangle orientation is required to be counter-clockwise (CCW)**

| **size [bytes]** | **name** | **type** | **description**                     |
|------------------|----------|----------|-------------------------------------|
| 4                | v0       | uint32   | first index of the first triangle   |
| 4                | v1       | uint32   | second index of the  first triangle |
| 4                | v2       | uint32   | third index of the first triangle   |
| 4                | v0       | uint32   | first index of the second triangle  |
| ...              |          |          |                                     |

#### DataType Image (4)

The Image data block can either contain an arbitrary image or a texture for a given 3D mesh. If a texture
is stored, the 3D mesh will refer to it by the `dataId`.  The data block size in the header refers to the total size of
this block (compression + data_size).

| **size [bytes]** | **name**    | **type** | **description**                        |
|------------------|-------------|----------|----------------------------------------|
| 4                | compression | uint32   | id for supported compression algorithm |
|                  | data        | bytes    | data of the file content               |

##### Supported compression

| **ID** | **Name**           |
|--------|--------------------|
| 0      | Raw24 (RGB 24 bit) |
| 1      | Jpeg               |
| 2      | Png                |

#### DataType DataMaterialStandard (5)

The standard material block is used to set the material for the geometry specified in the mesh data block.

| **size [bytes]** | **name**     | **type** | **description**                                         |
|------------------|--------------|----------|---------------------------------------------------------|
| 4                | Ka red       | float    | RED component for ambient color                         |
| 4                | Ka green     | float    | GREEN component for ambient color                       |
| 4                | Ka blue      | float    | BLUE component for ambient color                        |
| 8                | Ka textureId | uint64   | dataId of the referenced texture for ambient component  |
| 4                | Kd red       | float    | RED component for diffuse color                         |
| 4                | Kd green     | float    | GREEN component for diffuse color                       |
| 4                | Kd blue      | float    | BLUE component for diffuse color                        |
| 8                | Kd textureId | uint64   | dataId of the referenced texture for diffuse component  |
| 4                | Ks red       | float    | RED component for specular color                        |
| 4                | Ks green     | float    | GREEN component for specular color                      |
| 4                | Ks blue      | float    | BLUE component for specular color                       |
| 8                | Ks textureId | uint64   | dataId of the referenced texture for specular component |
| 4                | Ns           | float    | specular exponent                                       |
| 4                | alpha        | float    | alpha between 0..1, 1 means full opaque                 |

If no texture is available/set, then the `textureId` is set to `0x7fffffffffffffffL` value.
The Ns value specifies the specular exponent for the current material. A high exponent
results in a tight, concentrated highlight.  Ns values normally range from 0 to 1000.

The material values can be used in combination with different shaders, and therefore the render result may vary. Most
shaders and software packages treat the diffuse color information as most dominating.

#### DataType SceneNode (6)

This data block can be used to describe scene node which is embedded into a scene graph.
The scene node wraps a specific data block and puts its information into the specified
scenegraph.

The constant total size of a scenenode block is 80 bytes. This nodes can be used to simply instance
geometry data, e.g. have the geometry of one object defined in a mesh block and have 500 scenenodes
refering to the same geometry information.

| **size [bytes]**   | **name**     | **type**   | **description**                                      |
| ------------------ | ------------ | ---------- | -----------------------------------                  |
| 8                  | geometryId   | uint64     | Id of a data block containing geometry (can be zero) |
| 32                 | name         | string     | name of the node (can be empty)                      |
| 4                  | tx           | float      | translation X                                        |
| 4                  | ty           | float      | translation Y                                        |
| 4                  | tz           | float      | translation Z                                        |
| 4                  | rx           | float      | rotation X                                           |
| 4                  | ry           | float      | rotation Y                                           |
| 4                  | rz           | float      | rotation Z                                           |
| 4                  | rw           | float      | rotation W                                           |
| 4                  | sx           | float      | scale X                                              |
| 4                  | sy           | float      | scale Y                                              |
| 4                  | sz           | float      | scale Z                                              |

The transformation is based on a local coordinate system. The transformation matrix is built by `T *
R * S`; first the scale is applied to the vertices, then the rotation, and then the translation.

The translation is given in unit meters. The rotation is given in quaternion (x,y,z,w), where w is
the scalar. The scale vector contains the scale values in each direction given in unit meters.

The `geometryId` can be zero which means that no geometry should be displayed. This indicates that
the scenenode is an intermediate node in the scenegraph. All leafnodes in the scenegraph have to
contain geometry information.

#### Data Type Track (7)

This data block can be used to describe a 3D track. A track is a sequence of a 3D position and orientation of
an AR device. The orientation is stored as a normalized normal vector of the device's LookAt vector.
The LookAt vector is pointing from the center of the device in the direction of the camera
(outward). The timestamp is using the UNIX time, the number of seconds elapsed since January 1, 1970 UTC.

| **size [bytes]** | **name**   | **type** | **description**                    |
|------------------|------------|----------|------------------------------------|
| 4                | nrOfPoints | uint32   | number of points                   |
| 8                | timestamp  | int64    | timestamp (UNIX time)              |
| 4                | x          | float    | x-coordinate of first point        |
| 4                | y          | float    | y-coordinate of first point        |
| 4                | z          | float    | z-coordinate of first point        |
| 4                | nx         | float    | x-coordinate of the first normal   |
| 4                | ny         | float    | y-coordinate of the first normal   |
| 4                | nz         | float    | z-coordinate of the first normal   |
| 4                | confidence | float    | tracking confidence of first point |
| 4                | x          | float    | x-coordinate of second point       |
| ...              |            |          |                                    |
