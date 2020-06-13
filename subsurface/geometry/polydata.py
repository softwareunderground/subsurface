import pandas as pd


class PolyData:
    def __init__(self):
        """
        TODO: @Bane Do we need to make a separate edges dataframe

        """

        # They should have XYZ and any properties

        # TODO: @all should we use geopandas instead? It seems that in 3D does
        #  not add too much value
        self.points = pd.DataFrame(columns=['X', 'Y', 'Z'])

        self.edges = pd.DataFrame()

    # Add pyvista methods ...
