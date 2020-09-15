import pytest

from subsurface.geometry.base_structures import UnstructuredData
import numpy as np
import pandas as pd


def test_unstructured_data():
    # Normal constructor
    foo = UnstructuredData(np.ones((5, 3)), np.ones((4, 3)),
                           pd.DataFrame({'foo': np.arange(4)}))
    print(foo)

    # No attributes
    foo = UnstructuredData(np.ones((5, 3)), np.ones((4, 3)))
    print(foo)

    #Failed validation
    with pytest.raises(AttributeError, match=r".*edges must.*"):
        foo = UnstructuredData(np.ones((5, 3)), np.ones((4, 3)),
                               pd.DataFrame({'foo': np.arange(1)}))
        print(foo)