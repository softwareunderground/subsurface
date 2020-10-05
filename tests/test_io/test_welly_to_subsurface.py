import pytest

import subsurface as ss
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from subsurface.io import WellyToSubsurface
from subsurface.structs import LineSet
from subsurface.visualization.to_pyvista import to_pyvista_line, pv_plot

welly = pytest.importorskip('welly')
data_path = '../data/borehole/'
from welly import Curve
from striplog import Legend, Striplog


def test_empty_project():
    wts = WellyToSubsurface()
    print(wts.p)


def test_create_welly_to_subsurface():
    wts = WellyToSubsurface()
    collars = test_read_collars()
    survey = test_read_survey()
    lith = test_read_lith()
    assays = test_read_assay()

    wts.add_datum(collars)
    wts.add_deviation(survey)
    wts.add_striplog(lith)
    wts.add_assays(assays, basis='FROM')

    unstructured_data = wts.to_subsurface(n_points=1000, attributes=None)
    element = LineSet(unstructured_data)
    pyvista_mesh = to_pyvista_line(element)
    # Plot default LITH
    pv_plot([pyvista_mesh], image_2d=True)

    # Plot gold
    pyvista_mesh.set_active_scalar('Au (g/t)')
    pv_plot([pyvista_mesh])


def test_excel_to_subsurface():
    data = pd.read_excel(data_path + 'borehole_lith.xlsx')
    survey = pd.read_excel(data_path + 'borehole_survey.xlsx')
    collar = pd.read_excel(data_path + 'borehole_collar.xlsx')

    well_name_column = 'SITE_ID'
    depth_name = 'DEPTH_FROM'
    well_names = data[well_name_column].unique()

    foo = data.groupby(well_name_column).get_group(well_names[0])
    data_dict = foo.to_dict('list')

    # Load striplog
    s = Striplog.from_dict(data_dict, remap={'DEPTH_FROM': 'top',
                                             'DEPTH_TO': 'base',
                                             'LITHOLOGY': 'component lith',
                                             'SITE_ID': 'description'})

    s.plot()
    plt.show()

    # Striplog.from_descriptions()
    # c = Curve(a['LITHOLOGY'], basis=a[depth_name])
    # print(a)
    # print(c)
    # c.plot(marker='o')
    # f = plt.gcf()
    # plt.show()


def test_striplog():
    s = Striplog.from_csv(data_path + 'striplog_integration/alpha_strip.tops')
    s.plot()
    plt.show()
    print(s)


def test_striplog_2():
    data = pd.read_excel(data_path + 'borehole_lith.xlsx')
    well_name_column = 'SITE_ID'
    depth_name = 'DEPTH_FROM'
    well_names = data[well_name_column].unique()
    foo = data.groupby(well_name_column).get_group(well_names[0])
    data_dict = foo.to_dict('list')

    s = Striplog.from_dict(data_dict, remap={'DEPTH_FROM': 'top',
                                             'DEPTH_TO': 'base',
                                             'LITHOLOGY': 'component lith',
                                             'SITE_ID': 'description'})

    s.plot()
    plt.show()
    print(s)


def test_read_lith():
    d = pd.read_excel(data_path + 'borehole_lith.xlsx', index_col='SITE_ID')
    d.columns = d.columns.map({'DEPTH_FROM': 'top',
                               'DEPTH_TO': 'base',
                               'LITHOLOGY': 'component lith',
                               'SITE_ID': 'description'})

    print(d)
    return d


def test_read_survey():
    """TODO the reading function must return the df already on the right format"""
    d = pd.read_excel(data_path + 'borehole_survey.xlsx',
                      index_col=0)
    d.index = d.index.map({'ELV-01': 'foo', 'ELV-02': 'bar'})
    d.columns = d.columns.map({'DEPTH': 'md', 'INCLINATION': 'inc', 'DIRECTION': 'azi'})

    print(d)
    return d


def test_read_collars():
    cols = [0, 1, 2, 4]
    d = pd.read_excel(data_path + 'borehole_collar.xlsx', usecols=cols,
                      header=None, index_col=0)
    print(d)
    return d


def test_read_assay():
    d = pd.read_excel(data_path + 'borehole_assays.xlsx',
                      index_col=0)
    d.drop('TO', axis=1, inplace=True)
    return d
    # wts = ss.io.WellyToSubsurface('test_well')
    # c = Curve(d['Potencia'], basis=d['FROM'])
    # c.plot()
    # plt.show()


def test_read_data_loc():
    collars = test_read_collars()
    datum = collars.loc[['foo'], [1, 2, 3]].values
    print(datum)
    survey = test_read_survey()
    dev = survey.loc['foo', ['DEPTH', 'INCLINATION', 'DIRECTION']]
    wts = ss.io.WellyToSubsurface('test_well')
    wts.add_deviation(dev)
    wts.well.location.td = dev['DEPTH'].max()

    data = pd.read_excel(data_path + 'borehole_lith.xlsx')
    well_name_column = 'SITE_ID'
    depth_name = 'DEPTH_FROM'
    well_names = data[well_name_column].unique()
    foo = data.groupby(well_name_column).get_group(well_names[0])
    data_dict = foo.to_dict('list')

    s = Striplog.from_dict(data_dict, remap={'DEPTH_FROM': 'top',
                                             'DEPTH_TO': 'base',
                                             'LITHOLOGY': 'component lith',
                                             'SITE_ID': 'description'}, points=True)

    step_size = (dev['DEPTH'].max() - dev['DEPTH'].min()) / 1000
    attri = s.to_log(step_size, dev['DEPTH'].min() + step_size / 2,
                     dev['DEPTH'].max() - step_size / 2)

    s.plot()
    plt.show()

    d = test_read_assay()
    c = Curve(d['Potencia'], basis=d['FROM'])
    c.to_basis_like(attri)

    wts.well.data['lith'] = s
    wts.well.data['Potencia'] = c
    wts.well.plot()
    plt.show()
    c = c.to_basis(start=dev['DEPTH'].min() + step_size / 2,
                   stop=dev['DEPTH'].max() - step_size / 2,
                   step=step_size,
                   undefined=0)
    # s.read_at(dev['DEPTH'])
    unstructured_data = wts.to_subsurface(n_points=1000, attributes=c)
    element = LineSet(unstructured_data)
    pyvista_mesh = to_pyvista_line(element)
    pv_plot([pyvista_mesh])


def test_read_data():
    collars = test_read_collars()
    datum = collars.loc[['foo'], [1, 2, 3]].values
    print(datum)
    survey = test_read_survey()
    dev = survey.loc['foo', ['DEPTH', 'INCLINATION', 'DIRECTION']]
    wts = ss.io.WellyToSubsurface('test_well')
    # wts.add_deviation(dev)
    wts.well.location.td = dev['DEPTH'].max()

    data = pd.read_excel(data_path + 'borehole_lith.xlsx')
    well_name_column = 'SITE_ID'
    depth_name = 'DEPTH_FROM'
    well_names = data[well_name_column].unique()
    foo = data.groupby(well_name_column).get_group(well_names[0])
    data_dict = foo.to_dict('list')

    s = Striplog.from_dict(data_dict, remap={'DEPTH_FROM': 'top',
                                             'DEPTH_TO': 'base',
                                             'LITHOLOGY': 'component lith',
                                             'SITE_ID': 'description'})
    s.plot()
    plt.show()

    wts.well.data['lith'] = s
    wts.well.plot()
    plt.show()


def test_read_location():
    collars = test_read_collars()
    datum = collars.loc[['foo'], [1, 2, 3]].values
    print(datum)
    survey = test_read_survey()
    dev = survey.loc['foo', ['DEPTH', 'INCLINATION', 'DIRECTION']]
    wts = ss.io.WellyToSubsurface('test_well')
    wts.add_deviation(dev)
    unstructured_data = wts.to_subsurface(datum=datum)
    element = LineSet(unstructured_data)
    pyvista_mesh = to_pyvista_line(element)
    pv_plot([pyvista_mesh])


def test_welly_to_subsurface():
    wts = ss.io.WellyToSubsurface('test_well')

    dev = pd.DataFrame(np.array([[0, 0, 0],
                                 [2133, 0, 0]]),
                       columns=['Depth', 'Dip', 'Azimuth'])

    # In a well we can have deviation
    wts.add_deviation(dev[['Depth', 'Dip', 'Azimuth']].values)
    XYZ = wts.trajectory()
    np.testing.assert_almost_equal(XYZ[355:357],
                                   np.array([[0., 0., -757.97297297],
                                             [0., 0., -760.10810811]]))
    XYZ2 = wts.trajectory(datum=[5, 15, 25])
    print(XYZ2)

    # Datum (XYZ location)

    # Lithology

    # Logs

    # Everything would be a LineSet with a bunch of properties
    unstructured_data = wts.to_subsurface()
    element = LineSet(unstructured_data)
    pyvista_mesh = to_pyvista_line(element)
    pv_plot([pyvista_mesh])
