import pytest

import pandas as pd
import matplotlib.pyplot as plt

from subsurface.reader.readers_data import ReaderWellsHelper, ReaderFilesHelper
from subsurface.reader.wells import add_tops_from_base_and_altitude_in_place
from subsurface.reader.wells.pandas_to_welly import WellyToSubsurfaceHelper
from subsurface.reader.wells.well_files_reader import read_collar, read_survey, read_lith, read_attributes
from subsurface.reader.wells.wells_api import read_wells_to_unstruct
from subsurface.reader.wells.wells_utils import pivot_wells_df_into_segment_per_row, map_attr_to_segments, \
    fix_wells_higher_base_than_top_inplace
from subsurface.reader.wells.welly_reader import welly_to_subsurface
from subsurface.structs import LineSet
import subsurface
import pathlib

welly = pytest.importorskip('welly')
xlrd = pytest.importorskip('xlrd')
pf = pathlib.Path(__file__).parent.absolute()
data_path = pf.joinpath('../data/borehole/')
from striplog import Striplog, Component


def test_empty_project():
    wts = WellyToSubsurfaceHelper()
    print(wts.p)


def test_read_borehole_stateless():
    collar = read_collar(ReaderFilesHelper(
        file_or_buffer=data_path.joinpath('borehole_collar.xlsx'),
        header=None,
        usecols=[0, 1, 2, 4]))
    survey = read_survey(ReaderFilesHelper(
        file_or_buffer=data_path.joinpath('borehole_survey.xlsx'),
        columns_map={'DEPTH': 'md', 'INCLINATION': 'inc', 'DIRECTION': 'azi'},
        index_map={'ELV-01': 'foo', 'ELV-02': 'bar'}
    ))

    dict_collar = collar.to_dict('split')
    dict_survey = survey.to_dict('split')
    c_df = pd.DataFrame(data=dict_collar['data'],
                        index=dict_collar['index'],
                        columns=dict_collar['columns'])
    s_df = pd.DataFrame(data=dict_survey['data'],
                        index=dict_survey['index'],
                        columns=dict_survey['columns'])

    wts = WellyToSubsurfaceHelper(collar_df=c_df, survey_df=s_df)
    unstruct = welly_to_subsurface(wts)
    print(unstruct)

    if True:
        element = LineSet(unstruct)
        pyvista_mesh = subsurface.visualization.to_pyvista_line(element)
        # Plot default LITH
        subsurface.visualization.pv_plot([pyvista_mesh], image_2d=True)


def test_read_borehole_manual_api():
    collar = read_collar(ReaderFilesHelper(
        file_or_buffer=data_path.joinpath('borehole_collar.xlsx'),
        header=None,
        usecols=[0, 1, 2, 4]))
    survey = read_survey(ReaderFilesHelper(
        file_or_buffer=data_path.joinpath('borehole_survey.xlsx'),
        columns_map={'DEPTH': 'md', 'INCLINATION': 'inc', 'DIRECTION': 'azi'},
        index_map={'ELV-01': 'foo', 'ELV-02': 'bar'}
    ))

    lith = read_lith(
        ReaderFilesHelper(
            file_or_buffer=data_path.joinpath('borehole_lith.xlsx'),
            index_col="SITE_ID",
            columns_map={'DEPTH_FROM': 'top', 'DEPTH_TO': 'base',
                         'LITHOLOGY': 'component lith', 'SITE_ID': 'description'}
        )
    )

    attr = read_attributes(
        ReaderFilesHelper(
            data_path.joinpath('borehole_assays.xlsx'),
            drop_cols=['TO'],
            columns_map={'FROM': 'basis'}
        )
    )
    wts = WellyToSubsurfaceHelper(collar_df=collar, survey_df=survey, lith_df=lith, attrib_dfs=[attr])
    unstruct = welly_to_subsurface(wts)
    print(unstruct)

    if True:
        element = LineSet(unstruct)
        pyvista_mesh = subsurface.visualization.to_pyvista_line(element)
        # Plot default LITH
        subsurface.visualization.pv_plot([pyvista_mesh], image_2d=True)


def test_read_wells_to_unstruct():
    reader_helper = ReaderWellsHelper(
        reader_collars_args=ReaderFilesHelper(
            file_or_buffer=data_path.joinpath('borehole_collar.xlsx'),
            header=None,
            usecols=[0, 1, 2, 4]),
        reader_survey_args=ReaderFilesHelper(
            file_or_buffer=data_path.joinpath('borehole_survey.xlsx'),
            columns_map={'DEPTH': 'md', 'INCLINATION': 'inc', 'DIRECTION': 'azi'},
            index_map={'ELV-01': 'foo', 'ELV-02': 'bar'}
        ),
        reader_lith_args=ReaderFilesHelper(
            file_or_buffer=data_path.joinpath('borehole_lith.xlsx'),
            index_col="SITE_ID",
            columns_map={'DEPTH_FROM': 'top', 'DEPTH_TO': 'base',
                         'LITHOLOGY': 'component lith', 'SITE_ID': 'description'}
        ),
        reader_attr_args=[
            ReaderFilesHelper(
                data_path.joinpath('borehole_assays.xlsx'),
                drop_cols=['TO'],
                columns_map={'FROM': 'basis'}
            ),
            ReaderFilesHelper(
                data_path.joinpath('borehole_density.xlsx'),
                drop_cols=['LITOLOGIA'],
                columns_map={'DEPTH_TO': 'basis'}
            )
        ]
    )
    unstructured_data = read_wells_to_unstruct(reader_helper)

    if False:
        to_netcdf(file='../data/wells.nc')

    element = LineSet(unstructured_data)
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element)
    # Plot default LITH
    subsurface.visualization.pv_plot([pyvista_mesh], image_2d=True)


def test_create_welly_to_subsurface():
    wts = WellyToSubsurfaceHelper()
    collars = test_read_collars()
    survey = test_read_survey()
    lith = test_read_lith()
    assays = test_read_assay()

    wts.add_datum(collars)
    wts.add_deviation(survey)
    wts.add_striplog(lith)
    wts.add_assays(assays, basis='FROM')

    unstructured_data = welly_to_subsurface(wts, n_vertex_per_well=1000)
    unstructured_data.to_xarray()
    element = LineSet(unstructured_data)
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element)
    # Plot default LITH
    subsurface.visualization.pv_plot([pyvista_mesh], image_2d=True)

    # Plot gold
    pyvista_mesh.set_active_scalars('Au (g/t)')
    subsurface.visualization.pv_plot([pyvista_mesh], image_2d=True)


def test_read_to_welly_json():
    collar = read_collar(ReaderFilesHelper(
        file_or_buffer=data_path.joinpath('borehole_collar.xlsx'),
        header=None,
        usecols=[0, 1, 2, 4]))
    survey = read_survey(ReaderFilesHelper(
        file_or_buffer=data_path.joinpath('borehole_survey.xlsx'),
        columns_map={'DEPTH': 'md', 'INCLINATION': 'inc', 'DIRECTION': 'azi'},
        index_map={'ELV-01': 'foo', 'ELV-02': 'bar'}
    ))

    json_ = collar.to_json(orient='split')

    unstructured_data = read_wells_to_unstruct(
        ReaderWellsHelper(
            reader_collars_args=ReaderFilesHelper(json_, format='.json'),
            reader_survey_args=ReaderFilesHelper(survey.to_json(orient='split'),
                                                 format='.json')
        )
    )
    print('\n', unstructured_data)
    element = LineSet(unstructured_data)
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element)

    # Plot default LITH
    subsurface.visualization.pv_plot([pyvista_mesh], image_2d=True)


def test_read_to_welly_dict():
    """Read from dict is important for json"""

    # Convert xlsx into dict. Dict has to be already cleaned
    collar = read_collar(ReaderFilesHelper(
        file_or_buffer=data_path.joinpath('borehole_collar.xlsx'),
        header=None,
        usecols=[0, 1, 2, 4]))
    survey = read_survey(ReaderFilesHelper(
        file_or_buffer=data_path.joinpath('borehole_survey.xlsx'),
        columns_map={'DEPTH': 'md', 'INCLINATION': 'inc', 'DIRECTION': 'azi'},
        index_map={'ELV-01': 'foo', 'ELV-02': 'bar'}
    ))

    dict_ = collar.to_dict(orient='split')

    unstructured_data = read_wells_to_unstruct(
        ReaderWellsHelper(
            reader_collars_args=ReaderFilesHelper(dict_),
            reader_survey_args=ReaderFilesHelper(survey.to_dict(orient='split'))
        )
    )
    print('\n', unstructured_data)
    element = LineSet(unstructured_data)
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element)

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
    # d.to_csv('lith.csv')
    print(d)
    return d


def test_read_survey():
    """TODO the reading function must return the df already on the right format"""
    d = pd.read_excel(data_path.joinpath('borehole_survey.xlsx'),
                      index_col=0)
    d.index = d.index.map({'ELV-01': 'foo', 'ELV-02': 'bar'})
    d.columns = d.columns.map({'DEPTH': 'md', 'INCLINATION': 'inc', 'DIRECTION': 'azi'})
    # d.to_csv('survey.csv')
    print(d)
    return d


def test_read_collars():
    cols = [0, 1, 2, 4]
    d = pd.read_excel(data_path.joinpath('borehole_collar.xlsx'), usecols=cols,
                      header=None, index_col=0)
    print(d)
    # d.to_csv('collars.csv')
    return d


def test_read_assay():
    d = pd.read_excel(data_path.joinpath('borehole_assays.xlsx'),
                      index_col=0)
    d.drop('TO', axis=1, inplace=True)
    # d.to_csv('assay.csv')
    return d


def test_read_density():
    d = pd.read_excel(data_path.joinpath('borehole_density.xlsx'),
                      index_col=0)
    d.drop('DEPTH_TO', axis=1, inplace=True)
    return d


formations = ["topo", "etchegoin", "macoma", "chanac", "mclure",
              "santa_margarita", "fruitvale",
              "round_mountain", "olcese", "freeman_jewett", "vedder", "eocene",
              "cretaceous",
              "basement", "null"]


def test_read_kim():
    collar = read_collar(
        ReaderFilesHelper(
            file_or_buffer=data_path.joinpath('kim_ready.csv'),
            index_col="name",
            usecols=['x', 'y', 'altitude', "name"]
        )
    )

    print(collar)

    survey = read_survey(
        ReaderFilesHelper(
            file_or_buffer=data_path.joinpath('kim_ready.csv'),
            index_col="name",
            usecols=["name", "md"]
        )
    )

    lith = read_lith(
        ReaderFilesHelper(
            file_or_buffer=data_path.joinpath('kim_ready.csv'),
            usecols=['name', 'top', 'base', 'formation'],
            columns_map={'top': 'top',
                         'base': 'base',
                         'formation': 'component lith',
                         }
        )
    )

    wts = WellyToSubsurfaceHelper(collar_df=collar, survey_df=survey, lith_df=lith)
    unstruct = welly_to_subsurface(wts,
                                   table=[Component({'lith': l}) for l in formations]
                                   )
    element = LineSet(unstruct)
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element, radius=50)

    # Plot default LITH
    subsurface.visualization.pv_plot([pyvista_mesh], image_2d=True)


def test_read_kim_default_component_table():
    collar = read_collar(
        ReaderFilesHelper(
            file_or_buffer=data_path.joinpath('kim_ready.csv'),
            index_col="name",
            usecols=['x', 'y', 'altitude', "name"]
        )
    )

    print(collar)

    survey = read_survey(
        ReaderFilesHelper(
            file_or_buffer=data_path.joinpath('kim_ready.csv'),
            index_col="name",
            usecols=["name", "md"]
        )
    )

    lith = read_lith(
        ReaderFilesHelper(
            file_or_buffer=data_path.joinpath('kim_ready.csv'),
            usecols=['name', 'top', 'base', 'formation'],
            columns_map={'top': 'top',
                         'base': 'base',
                         'formation': 'component lith',
                         }
        )
    )

    wts = WellyToSubsurfaceHelper(collar_df=collar, survey_df=survey, lith_df=lith)
    unstruct = welly_to_subsurface(wts)
    element = LineSet(unstruct)
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element, radius=50)

    # Plot default LITH
    subsurface.visualization.pv_plot([pyvista_mesh], image_2d=True)


def test_aux_operations():
    df = pd.read_table(data_path.joinpath('doggr_jlw_vedder_final.utm.dat'),
                       skiprows=41,
                       header=None,
                       sep='\t',
                       )

    df.rename(columns={1: 'x', 2: 'y', 3: 'name',
                       4: 'num', 5: 'z', 6: 'year', 10: 'altitude'},
              inplace=True)
    df['name'] = df['name'] + df['num']

    df_pivoted = pivot_wells_df_into_segment_per_row(df, 11, 15)
    df_mapped = map_attr_to_segments(df_pivoted,
                                     attr_per_segment=formations,
                                     n_wells=df.shape[0]
                                     )
    print(df_pivoted)
    df_with_tops_base = add_tops_from_base_and_altitude_in_place(df_mapped, 'name', "base", 'altitude')
    df_fixed = fix_wells_higher_base_than_top_inplace(df_with_tops_base)
    print(df_fixed)
    df_fixed.to_csv(data_path.joinpath("kim_ready.csv"))
