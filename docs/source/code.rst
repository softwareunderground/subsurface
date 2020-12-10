Code
====

.. toctree::
   :maxdepth: 3


Subsurface Base Structures
--------------------------
.. currentmodule:: subsurface
.. autosummary::
    :toctree: Base Structures
    :template: class.rst

    UnstructuredData
    StructuredData


.. currentmodule:: subsurface.structs.base_structures
.. autosummary::
    :toctree: Base Structures
    :template: class.rst

    CommonDataMethods

Unstructured Elements
---------------------
.. currentmodule:: subsurface
.. autosummary::
    :toctree: Unstructured Elements
    :template: class.rst

    PointSet
    LineSet
    TriSurf
    TetraMesh


Structured Elements
-------------------
.. currentmodule:: subsurface
.. autosummary::
    :toctree: Structured Elements
    :template: class.rst

    StructuredGrid
    StructuredSurface

Read Well Data
--------------
.. currentmodule:: subsurface.io
.. autosummary::
    :toctree: Read well data
    :template: base.rst

    read_wells_to_unstruct
    borehole_location_to_unstruct

Read Topographic Data
---------------------
.. currentmodule:: subsurface.io
.. autosummary::
    :toctree: Read topographic data
    :template: base.rst

    read_unstructured_topography
    read_structured_topography

Read Profiles
-------------

.. currentmodule:: subsurface.io
.. autosummary::
    :toctree: Read profiles
    :template: base.rst

    lineset_from_trace
    create_mesh_from_trace
    create_tri_surf_from_traces_texture

Read Surface
------------
.. currentmodule:: subsurface.io.mesh.surface_reader
.. autosummary::
    :toctree: Surface reader
    :template: base.rst

    csv_to_unstruct_args
    dxf_to_vertex_edges
    get_attributes_from_df
    get_cells_from_df

Plot
----
.. currentmodule:: subsurface.visualization
.. autosummary::
    :toctree: Visualization
    :template: base.rst

    pv_plot
    to_pyvista_points
    to_pyvista_line
    to_pyvista_mesh
    to_pyvista_mesh_and_texture
    to_pyvista_tetra
    update_grid_attribute