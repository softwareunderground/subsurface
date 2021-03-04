import pytest

import pandas as pd
import matplotlib.pyplot as plt

from subsurface.reader import WellyToSubsurface, read_to_welly, read_wells_to_unstruct
from subsurface.reader.wells.well_files_reader import read_collar, read_survey
from subsurface.structs import LineSet
import subsurface
import pathlib

welly = pytest.importorskip('welly')
xlrd = pytest.importorskip('xlrd')
pf = pathlib.Path(__file__).parent.absolute()
data_path = pf.joinpath('../data/borehole/')
from striplog import Striplog


def test_empty_project():
    wts = WellyToSubsurface()
    print(wts.p)


def test_read_wells_to_unstruct():
    unstructured_data = read_wells_to_unstruct(
        collar_file=data_path.joinpath('borehole_collar.xlsx'),
        read_collar_kwargs={'usecols': [0, 1, 2, 4]},
        survey_file=data_path.joinpath('borehole_survey.xlsx'),
        read_survey_kwargs={
            'columns_map': {'DEPTH': 'md', 'INCLINATION': 'inc',
                            'DIRECTION': 'azi'},
            'index_map': {'ELV-01': 'foo', 'ELV-02': 'bar'}
        },
        lith_file=data_path.joinpath('borehole_lith.xlsx'),
        read_lith_kwargs={
            'index_col': 'SITE_ID',
            'columns_map': {'DEPTH_FROM': 'top',
                            'DEPTH_TO': 'base',
                            'LITHOLOGY': 'component lith',
                            'SITE_ID': 'description'}
        },
        attrib_file=[data_path.joinpath('borehole_assays.xlsx'),
                     data_path.joinpath('borehole_density.xlsx')],
        read_attributes_kwargs={
            'drop_cols': ['TO', 'LITOLOGIA'],
            'columns_map': [
                {'FROM': 'basis'},
                {'DEPTH_TO': 'basis'}
            ]
        }
    )

    if False:
        to_netcdf(file='../data/wells.nc')

    element = LineSet(unstructured_data)
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element)
    # Plot default LITH
    subsurface.visualization.pv_plot([pyvista_mesh], image_2d=True)


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

    unstructured_data = wts.to_subsurface(n_points=1000)
    unstructured_data.to_xarray()
    element = LineSet(unstructured_data)
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element)
    # Plot default LITH
    subsurface.visualization.pv_plot([pyvista_mesh], image_2d=True)

    # Plot gold
    pyvista_mesh.set_active_scalars('Au (g/t)')
    subsurface.visualization.pv_plot([pyvista_mesh], image_2d=True)


def test_read_to_welly():
    wts = read_to_welly(collar_file=data_path.joinpath('borehole_collar.xlsx'),
                        read_collar_kwargs={'usecols': [0, 1, 2, 3]})
    print(wts)


def test_read_to_welly_json():
    """Read from dict is important for json"""

    # Convert xlsx into dict. Dict has to be already cleaned
    collar = read_collar(file_or_buffer=data_path.joinpath('borehole_collar.xlsx'),
                         usecols=[0, 1, 2, 4])
    survey = read_survey(file_or_buffer=data_path.joinpath('borehole_survey.xlsx'),
                         columns_map={'DEPTH': 'md', 'INCLINATION': 'inc',
                                      'DIRECTION': 'azi'},
                         index_map={'ELV-01': 'foo', 'ELV-02': 'bar'}
                         )

    dict_ = collar.to_json(orient='split')
    wts = read_to_welly(collar_file=dict_,
                        read_collar_kwargs={'is_json': True},
                        survey_file=survey.to_json(orient='split'),
                        read_survey_kwargs={'is_json': True}
                        )

    print('\n', wts)
    unstructured_data = wts.to_subsurface()
    print('\n', unstructured_data)
    element = LineSet(unstructured_data)
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element)

    # Plot default LITH
    subsurface.visualization.pv_plot([pyvista_mesh], image_2d=True)


def test_read_borehole_stateless():
    collar = read_collar(file_or_buffer=data_path.joinpath('borehole_collar.xlsx'),
                         usecols=[0, 1, 2, 4])
    survey = read_survey(file_or_buffer=data_path.joinpath('borehole_survey.xlsx'),
                         columns_map={'DEPTH': 'md', 'INCLINATION': 'inc',
                                      'DIRECTION': 'azi'},
                         index_map={'ELV-01': 'foo', 'ELV-02': 'bar'}
                         )
    dict_collar = collar.to_dict('split')
    dict_survey = survey.to_dict('split')
    c_df = pd.DataFrame(data= dict_collar['data'],
                        index=dict_collar['index'],
                        columns=dict_collar['columns'])
    s_df = pd.DataFrame(data= dict_survey['data'],
                        index=dict_survey['index'],
                        columns=dict_survey['columns'])

    wts = subsurface.reader.pandas_to_welly(
        collar_df=c_df,
        survey_df=s_df,
    )

    unstruct = wts.to_subsurface()
    print(unstruct)


def test_read_to_welly_dict():
    """Read from dict is important for json"""

    # Convert xlsx into dict. Dict has to be already cleaned
    collar = read_collar(file_or_buffer=data_path.joinpath('borehole_collar.xlsx'),
                         usecols=[0, 1, 2, 4])
    survey = read_survey(file_or_buffer=data_path.joinpath('borehole_survey.xlsx'),
                         columns_map={'DEPTH': 'md', 'INCLINATION': 'inc',
                                      'DIRECTION': 'azi'},
                         index_map={'ELV-01': 'foo', 'ELV-02': 'bar'}
                         )

    dict_ = collar.to_dict(orient='split')
    wts = read_to_welly(collar_file=dict_,
                        survey_file=survey.to_dict(orient='split'))

    print('\n', wts)
    unstructured_data = wts.to_subsurface()
    print('\n', unstructured_data)
    element = LineSet(unstructured_data)
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element)
    # Plot default LITH
    subsurface.visualization.pv_plot([pyvista_mesh], image_2d=True)


def test_read_to_welly_xlsx():
    wts = read_to_welly()
    print('\n', wts)

    wts = read_to_welly(collar_file=data_path.joinpath('borehole_collar.xlsx'))
    print('\n', wts)
    # with pytest.raises(AttributeError, match=r".*one of the wells.*"):
    #     unstructured_data = wts.to_subsurface()

    wts = read_to_welly(collar_file=data_path.joinpath('borehole_collar.xlsx'),
                        read_collar_kwargs={'usecols': [0, 1, 2, 4]},
                        survey_file=data_path.joinpath('borehole_survey.xlsx'),
                        read_survey_kwargs={
                            'columns_map': {'DEPTH': 'md', 'INCLINATION': 'inc',
                                            'DIRECTION': 'azi'},
                            'index_map': {'ELV-01': 'foo', 'ELV-02': 'bar'}
                        })
    print('\n', wts)
    unstructured_data = wts.to_subsurface()
    print('\n', unstructured_data)
    element = LineSet(unstructured_data)
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element)
    # Plot default LITH
    subsurface.visualization.pv_plot([pyvista_mesh], image_2d=True)

    wts = read_to_welly(lith_file=data_path.joinpath('borehole_lith.xlsx'),
                        read_lith_kwargs={
                            'index_col': 'SITE_ID',
                            'columns_map': {'DEPTH_FROM': 'top',
                                            'DEPTH_TO': 'base',
                                            'LITHOLOGY': 'component lith',
                                            'SITE_ID': 'description'}
                        },
                        wts=wts  # By passing a wts object we append the data
                        )
    unstructured_data = wts.to_subsurface()
    print('\n', unstructured_data)
    element = LineSet(unstructured_data)
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element)
    # Plot default LITH
    subsurface.visualization.pv_plot([pyvista_mesh], image_2d=True)

    # All in one
    wts = read_to_welly(collar_file=data_path.joinpath('borehole_collar.xlsx'),
                        read_collar_kwargs={'usecols': [0, 1, 2, 4]},
                        survey_file=data_path.joinpath('borehole_survey.xlsx'),
                        read_survey_kwargs={
                            'columns_map': {'DEPTH': 'md', 'INCLINATION': 'inc',
                                            'DIRECTION': 'azi'},
                            'index_map': {'ELV-01': 'foo', 'ELV-02': 'bar'}
                        },
                        lith_file=data_path.joinpath('borehole_lith.xlsx'),
                        read_lith_kwargs={
                            'index_col': 'SITE_ID',
                            'columns_map': {'DEPTH_FROM': 'top',
                                            'DEPTH_TO': 'base',
                                            'LITHOLOGY': 'component lith',
                                            'SITE_ID': 'description'}
                        },
                        attrib_file=[data_path.joinpath('borehole_assays.xlsx'),
                                     data_path.joinpath('borehole_density.xlsx')],
                        read_attributes_kwargs={
                            'drop_cols': ['TO', 'LITOLOGIA'],
                            'columns_map': [
                                {'FROM': 'basis'},
                                {'DEPTH_TO': 'basis'}
                            ]
                        }
                        )

    unstructured_data = wts.to_subsurface()
    print('\n', unstructured_data)
    element = LineSet(unstructured_data)
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element)
    pyvista_mesh.set_active_scalars('Au (g/t)')
    # Plot default LITH
    subsurface.visualization.pv_plot([pyvista_mesh], image_2d=True)


def test_excel_to_subsurface():
    data = pd.read_excel(data_path.joinpath('borehole_lith.xlsx'))
    survey = pd.read_excel(data_path.joinpath('borehole_survey.xlsx'))
    collar = pd.read_excel(data_path.joinpath('borehole_collar.xlsx'))

    well_name_column = 'SITE_ID'
    well_names = data[well_name_column].unique()

    foo = data.groupby(well_name_column).get_group(well_names[0])
    data_dict = foo.to_dict('list')

    # Load striplog
    s = Striplog.from_dict(data_dict, remap={'DEPTH_FROM': 'top',
                                             'DEPTH_TO': 'base',
                                             'LITHOLOGY': 'component lith',
                                             'SITE_ID': 'description'})

    s.plot()
    plt.show(block=False)


def test_striplog():
    s = Striplog.from_csv(data_path.joinpath('striplog_integration/alpha_strip.tops'))
    s.components[0] = {'lith': 'overburden',
                       "colour": 'blue'}

    s.plot()
    plt.show(block=False)
    print(s)
    return s


def test_striplog_to_log():
    from striplog import Component
    s = test_striplog()
    table_input = []
    for i in range(6):
        table_input.append(Component({'lith': i}))
    table_input.append(Component({"lith": "miguel",
                                  "colour": "red"}))
    s_log, basis, table = s.to_log(return_meta=True, table=table_input)
    c = welly.Curve(s_log)
    c.plot()

    plt.show(block=False)
    print(table)


def test_striplog_2():
    data = pd.read_excel(data_path.joinpath('borehole_lith.xlsx'))
    well_name_column = 'SITE_ID'
    well_names = data[well_name_column].unique()
    foo = data.groupby(well_name_column).get_group(well_names[0])
    data_dict = foo.to_dict('list')

    s = Striplog.from_dict(data_dict, remap={'DEPTH_FROM': 'top',
                                             'DEPTH_TO': 'base',
                                             'LITHOLOGY': 'component lith',
                                             'SITE_ID': 'description'})

    s.plot()
    plt.show(block=False)
    print(s)


def test_read_lith():
    d = pd.read_excel(data_path.joinpath('borehole_lith.xlsx'), index_col='SITE_ID')
    d.columns = d.columns.map({'DEPTH_FROM': 'top',
                               'DEPTH_TO': 'base',
                               'LITHOLOGY': 'component lith',
                               'SITE_ID': 'description'})
    #d.to_csv('lith.csv')
    print(d)
    return d


def test_read_survey():
    """TODO the reading function must return the df already on the right format"""
    d = pd.read_excel(data_path.joinpath('borehole_survey.xlsx'),
                      index_col=0)
    d.index = d.index.map({'ELV-01': 'foo', 'ELV-02': 'bar'})
    d.columns = d.columns.map({'DEPTH': 'md', 'INCLINATION': 'inc', 'DIRECTION': 'azi'})
    #d.to_csv('survey.csv')
    print(d)
    return d


def test_read_collars():
    cols = [0, 1, 2, 4]
    d = pd.read_excel(data_path.joinpath('borehole_collar.xlsx'), usecols=cols,
                      header=None, index_col=0)
    print(d)
    #d.to_csv('collars.csv')
    return d


def test_read_assay():
    d = pd.read_excel(data_path.joinpath('borehole_assays.xlsx'),
                      index_col=0)
    d.drop('TO', axis=1, inplace=True)
    #d.to_csv('assay.csv')
    return d


def test_read_density():
    d = pd.read_excel(data_path.joinpath('borehole_density.xlsx'),
                      index_col=0)
    d.drop('DEPTH_TO', axis=1, inplace=True)
    return d
