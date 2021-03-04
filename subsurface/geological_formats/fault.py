import pyvista as pv
import pandas as pd


class FaultSticks:
    def __init__(self, df: pd.DataFrame):
        self.df = df

        self.pointcloud = None
        self.sticks = None

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self.df, attr)

    def __getitem__(self, item):
        return self.df[item]

    def plot(self, notebook=False, color="black"):
        if not self.pointcloud:
            self._make_pointcloud()
            self._make_sticks()

        p = pv.Plotter(notebook=notebook)
        p.add_mesh(self.pointcloud, color=color)
        for stick in self.sticks:
            p.add_mesh(stick, color=color)
        p.show()

    def _make_pointcloud(self):
        self.pointcloud = pv.PolyData(self.df[["X", "Y", "Z"]].values)

    def _make_sticks(self):

        lines = []
        for stick, indices in self.df.groupby("stick id").groups.items():
            stickdf = self.df.loc[indices]
            for (r1, row1), (r2, row2) in zip(stickdf[:-1].iterrows(), stickdf[1:].iterrows()):
                line = pv.Line(
                    pointa=(row1.X, row1.Y, row1.Z),
                    pointb=(row2.X, row2.Y, row2.Z),
                )
                lines.append(line)
        self.sticks = lines