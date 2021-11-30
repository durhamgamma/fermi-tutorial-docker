# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import absolute_import, division, print_function
import os
import numpy as np
from astropy import units as u
from astropy.table import Table, Column, join
from astropy.coordinates import SkyCoord
from astropy.io import fits
import fermipy
from fermipy.spectrum import PowerLaw
from fermipy.model_utils import get_function_par_names


def add_columns(t0, t1):
    """Add columns of table t1 to table t0."""

    for colname in t1.colnames:
        col = t1.columns[colname]
        if colname in t0.columns:
            continue
        new_col = Column(name=col.name, length=len(t0), dtype=col.dtype)  # ,
        # shape=col.shape)
        t0.add_column(new_col)


def join_tables(left, right, key_left, key_right,
                cols_right=None):
    """Perform a join of two tables.

    Parameters
    ----------
    left : `~astropy.Table`
        Left table for join.

    right : `~astropy.Table`
        Right table for join.

    key_left : str
        Key used to match elements from ``left`` table.

    key_right : str
        Key used to match elements from ``right`` table.

    cols_right : list    
        Subset of columns from ``right`` table that will be appended
        to joined table.

    """
    right = right.copy()

    if cols_right is None:
        cols_right = right.colnames
    else:
        cols_right = [c for c in cols_right if c in right.colnames]

    if key_left != key_right:
        right[key_right].name = key_left

    if key_left not in cols_right:
        cols_right += [key_left]

    out = join(left, right[cols_right], keys=key_left,
               join_type='left')

    for col in out.colnames:
        if out[col].dtype.kind in ['S', 'U']:
            out[col].fill_value = ''
        elif out[col].dtype.kind in ['i']:
            out[col].fill_value = 0
        else:
            out[col].fill_value = np.nan

    return out.filled()


def strip_columns(tab):
    """Strip whitespace from string columns."""
    for colname in tab.colnames:
        if tab[colname].dtype.kind in ['S', 'U']:
            tab[colname] = np.core.defchararray.strip(tab[colname])


def row_to_dict(row):
    """Convert a table row to a dictionary."""
    o = {}
    for colname in row.colnames:

        if isinstance(row[colname], np.string_) and row[colname].dtype.kind in ['S', 'U']:
            o[colname] = str(row[colname])
        else:
            o[colname] = row[colname]

    return o


class Catalog(object):
    """Source catalog object.  This class provides a simple wrapper around
    FITS catalog tables."""

    def __init__(self, table, extdir=''):
        self._table = table
        self._extdir = extdir

        if self.table['RAJ2000'].unit is None:
            self._src_skydir = SkyCoord(ra=self.table['RAJ2000'] * u.deg,
                                        dec=self.table['DEJ2000'] * u.deg)
        else:
            self._src_skydir = SkyCoord(ra=self.table['RAJ2000'],
                                        dec=self.table['DEJ2000'])
        self._radec = np.vstack((self._src_skydir.ra.deg,
                                 self._src_skydir.dec.deg)).T
        self._glonlat = np.vstack((self._src_skydir.galactic.l.deg,
                                   self._src_skydir.galactic.b.deg)).T

        if 'Spatial_Filename' not in self.table.columns:
            self.table['Spatial_Filename'] = Column(
                dtype='S20', length=len(self.table))

        if 'Spatial_Function' not in self.table.columns:
            self.table['Spatial_Function'] = Column(
                dtype='S20', length=len(self.table))

        m = (self.table['Spatial_Filename'] != '') | (
            self.table['Spatial_Function'] != '')
        self.table['extended'] = False
        self.table['extended'][m] = True
        self.table['extdir'] = extdir

    @property
    def table(self):
        """Return the `~astropy.table.Table` representation of this
        catalog."""
        return self._table

    @property
    def skydir(self):
        return self._src_skydir

    @property
    def radec(self):
        return self._radec

    @property
    def glonlat(self):
        return self._glonlat

    @classmethod
    def create(cls, name):

        extname = os.path.splitext(name)[1]
        if extname == '.fits' or extname == '.fit':
            fitsfile = name
            if not os.path.isfile(fitsfile):
                fitsfile = os.path.join(fermipy.PACKAGE_DATA, 'catalogs',
                                        fitsfile)

            h = fits.open(fitsfile)
            name = ''
            if 'CDS-NAME' in h[1].header:
                name = h[1].header['CDS-NAME']

            # Try to guess the catalog type from its name
            if name == '3FGL':
                return Catalog3FGL(fitsfile)
            elif name == 'FL8Y':
                return CatalogFL8Y(fitsfile)
            elif name == '4FGL':
                return Catalog4FGL(fitsfile)
            elif 'gll_psch_v08' in fitsfile:
                return Catalog2FHL(fitsfile)

            tab = Table.read(fitsfile, hdu=1)

            if 'NickName' in tab.columns:
                return Catalog4FGLP(fitsfile)
            else:
                return CatalogFPY(fitsfile)

        elif name == '3FGL':
            return Catalog3FGL()
        elif name == '2FHL':
            return Catalog2FHL()
        elif name == 'FL8Y':
            return CatalogFL8Y()
        elif name == '4FGL':
            return Catalog4FGL()
        else:
            raise Exception('Unrecognized catalog {}.'.format(name))


class CatalogFPY(Catalog):
    """This class supports user-generated catalogs.
    """

    def __init__(self, fitsfile=None, extdir=None):

        if extdir is None:
            extdir = os.path.join('$FERMIPY_DATA_DIR', 'catalogs',
                                  'Extended_archive_v18')

        table = Table.read(fitsfile, hdu=1)
        strip_columns(table)
        table['Spatial_Filename'][table['Spatial_Filename'] == 'None'] = ''
        super(CatalogFPY, self).__init__(table, extdir)


class Catalog2FHL(Catalog):

    def __init__(self, fitsfile=None, extdir=None):

        if extdir is None:
            extdir = os.path.join('$FERMIPY_DATA_DIR', 'catalogs',
                                  'Extended_archive_2fhl_v00')

        if fitsfile is None:
            fitsfile = os.path.join(fermipy.PACKAGE_DATA, 'catalogs',
                                    'gll_psch_v08.fit')

        hdulist = fits.open(fitsfile)
        table = Table(hdulist['2FHL Source Catalog'].data)
        table_extsrc = Table(hdulist['Extended Sources'].data)
        table_extsrc.meta.clear()
        strip_columns(table)
        strip_columns(table_extsrc)
        if 'Spatial_Function' not in table_extsrc.colnames:
            table_extsrc.add_column(Column(name='Spatial_Function', dtype='U20',
                                           length=len(table_extsrc)))
            table_extsrc['Spatial_Function'] = 'SpatialMap'

        table = join_tables(table, table_extsrc, 'Source_Name', 'Source_Name',
                            ['Model_Form', 'Model_SemiMajor',
                             'Model_SemiMinor', 'Model_PosAng',
                             'Spatial_Filename', 'Spatial_Function'])

        table.sort('Source_Name')

        super(Catalog2FHL, self).__init__(table, extdir)

        self._table['Flux_Density'] = \
            PowerLaw.eval_norm(50E3, -np.array(self.table['Spectral_Index']),
                               50E3, 2000E3,
                               np.array(self.table['Flux50']))
        self._table['Pivot_Energy'] = 50E3
        self._table['SpectrumType'] = 'PowerLaw'
        self._fill_params(self.table)

    @staticmethod
    def _fill_params(tab):

        tab['param_values'] = np.nan * np.ones((len(tab), 10))

        # PowerLaw
        # Prefactor, Index, Scale
        m = tab['SpectrumType'] == 'PowerLaw'
        tab['param_values'][m, 0] = tab['Flux_Density'][m]
        tab['param_values'][m, 1] = -1.0 * tab['Spectral_Index'][m]
        tab['param_values'][m, 2] = tab['Pivot_Energy'][m]


class Catalog3FGL(Catalog):

    def __init__(self, fitsfile=None, extdir=None):

        if extdir is None:
            extdir = os.path.join('$FERMIPY_DATA_DIR', 'catalogs',
                                  'Extended_archive_v15')

        if fitsfile is None:
            fitsfile = os.path.join(fermipy.PACKAGE_DATA, 'catalogs',
                                    'gll_psc_v16.fit')

        table = Table.read(fitsfile, 'LAT_Point_Source_Catalog')
        table_extsrc = Table.read(fitsfile, 'ExtendedSources')
        table_extsrc.meta.clear()
        if 'Flux_History' in table.columns:
            table.remove_column('Flux_History')
        if 'Unc_Flux_History' in table.columns:
            table.remove_column('Unc_Flux_History')
        strip_columns(table)
        strip_columns(table_extsrc)
        if 'Spatial_Function' not in table_extsrc.colnames:
            table_extsrc.add_column(Column(name='Spatial_Function', dtype='U20',
                                           length=len(table_extsrc)))
            table_extsrc['Spatial_Function'] = 'SpatialMap'

        table = join_tables(table, table_extsrc,
                            'Extended_Source_Name', 'Source_Name',
                            ['Model_Form', 'Model_SemiMajor',
                             'Model_SemiMinor', 'Model_PosAng',
                             'Spatial_Filename', 'Spatial_Function'])

        table.sort('Source_Name')

        super(Catalog3FGL, self).__init__(table, extdir)

        m = self.table['SpectrumType'] == 'PLExpCutoff'
        self.table['SpectrumType'][m] = 'PLSuperExpCutoff'

        self.table['Spatial_Function'] = Column(name='Spatial_Function', dtype='U20',
                                                data=self.table['Spatial_Function'].data)
        m = self.table['Spatial_Function'] == 'RadialGauss'
        self.table['Spatial_Function'][m] = 'RadialGaussian'

        self.table['TS_value'] = 0.0
        self.table['TS'] = 0.0

        ts_keys = ['Sqrt_TS30_100', 'Sqrt_TS100_300',
                   'Sqrt_TS300_1000', 'Sqrt_TS1000_3000',
                   'Sqrt_TS3000_10000', 'Sqrt_TS10000_100000']

        for k in ts_keys:

            if not k in self.table.columns:
                continue

            m = np.isfinite(self.table[k])
            self._table['TS_value'][m] += self.table[k][m] ** 2
            self._table['TS'][m] += self.table[k][m] ** 2

        self._fill_params(self.table)

    @staticmethod
    def _fill_params(tab):

        tab['param_values'] = np.nan * np.ones((len(tab), 10))

        # PowerLaw
        # Prefactor, Index, Scale
        m = tab['SpectrumType'] == 'PowerLaw'
        idxs = {k: i for i, k in
                enumerate(get_function_par_names('PowerLaw'))}
        tab['param_values'][m, idxs['Prefactor']] = tab['Flux_Density'][m]
        tab['param_values'][m, idxs['Index']] = -1.0 * tab['Spectral_Index'][m]
        tab['param_values'][m, idxs['Scale']] = tab['Pivot_Energy'][m]

        # PLSuperExpCutoff
        # Prefactor, Index1, Scale, Cutoff, Index2
        m = tab['SpectrumType'] == 'PLSuperExpCutoff'
        idxs = {k: i for i, k in
                enumerate(get_function_par_names('PLSuperExpCutoff'))}
        print(idxs)
        tab['param_values'][m, idxs['Prefactor']] = (tab['Flux_Density'][m] *
                                                     np.exp((tab['Pivot_Energy'][m] / tab['Cutoff'][m]) **
                                                            tab['Exp_Index'][m]))
        tab['param_values'][m, idxs['Index1']] = - \
            1.0 * tab['Spectral_Index'][m]
        tab['param_values'][m, idxs['Scale']] = tab['Pivot_Energy'][m]
        tab['param_values'][m, idxs['Cutoff']] = tab['Cutoff'][m]
        tab['param_values'][m, idxs['Index2']] = tab['Exp_Index'][m]

        # LogParabola
        # norm, alpha, beta, Eb
        m = tab['SpectrumType'] == 'LogParabola'
        idxs = {k: i for i, k in
                enumerate(get_function_par_names('LogParabola'))}
        tab['param_values'][m, idxs['norm']] = tab['Flux_Density'][m]
        tab['param_values'][m, idxs['alpha']] = tab['Spectral_Index'][m]
        tab['param_values'][m, idxs['beta']] = tab['beta'][m]
        tab['param_values'][m, idxs['Eb']] = tab['Pivot_Energy'][m]


class Catalog4FGLP(Catalog):
    """This class supports preliminary releases of the 4FGL catalog.
    Because there is currently no dedicated extended source library
    for 4FGL this class reuses the extended source library from the
    3FGL."""

    def __init__(self, fitsfile=None, extdir=None):

        if extdir is None:
            extdir = os.path.join('$FERMIPY_DATA_DIR', 'catalogs',
                                  'Extended_archive_v15')

        #hdulist = fits.open(fitsfile)
        table = Table.read(fitsfile, hdu=1)

        strip_columns(table)

        table['Source_Name'] = table['NickName']
        try:
            table['beta'] = table['Beta']
        except KeyError:
            pass

        m = table['Extended'] == True

        table['Spatial_Filename'] = Column(dtype='S20', length=len(table))

        spatial_filenames = []
        for i, row in enumerate(table[m]):
            spatial_filenames += [table[m][i]
                                  ['Source_Name'].replace(' ', '') + '.fits']
        table['Spatial_Filename'][m] = np.array(spatial_filenames)

        super(Catalog4FGLP, self).__init__(table, extdir)

        m = self.table['SpectrumType'] == 'PLExpCutoff'
        self.table['SpectrumType'][m] = 'PLSuperExpCutoff'

        table['TS'] = table['Test_Statistic']
        table['Cutoff'] = table['Cutoff_Energy']
        

class Catalog4FGL(Catalog):
    """This class supports releases the preliminary 4FGL.  See
    .
    """

    def __init__(self, fitsfile=None, extdir=None):

        if extdir is None:
            extdir = os.path.join('$FERMIPY_DATA_DIR', 'catalogs',
                                  'Extended_8years')

        if fitsfile is None:
            fitsfile = os.path.join(fermipy.PACKAGE_DATA, 'catalogs',
                                    'gll_psc_v27.fit')

        #hdulist = fits.open(fitsfile)
        table = Table.read(fitsfile, hdu=1)
        table_extsrc = Table.read(fitsfile, 'ExtendedSources')
        table_extsrc.meta.clear()
        hdulist = fits.open(fitsfile)

        strip_columns(table)
        strip_columns(table_extsrc)
        if 'Spatial_Function' not in table_extsrc.colnames:
            table_extsrc.add_column(Column(name='Spatial_Function', dtype='U20',
                                           length=len(table_extsrc)))
            table_extsrc['Spatial_Function'] = 'SpatialMap'

        #'Extended_Source_Name', 'Source_Name',
        table = join_tables(table, table_extsrc,
                            'Extended_Source_Name', 'Source_Name',
                            ['Model_Form', 'Model_SemiMajor',
                             'Model_SemiMinor', 'Model_PosAng',
                             'Spatial_Filename', 'Spatial_Function'])
        table.sort('Source_Name')
        super(Catalog4FGL, self).__init__(table, extdir)

        excol = np.zeros((len(table)), 'bool')
        for i, exname in enumerate(table['Extended_Source_Name']):
            if len(exname.strip()) > 0:
                excol[i] = True

        self.table['extended'] = excol
        self.table['Extended'] = excol

        scol = Column(name='Spatial_Function', dtype='U20',
                      data=self.table['Spatial_Function'].data)
        self.table.remove_column('Spatial_Function')
        self.table['Spatial_Function'] = scol

        m = self.table['Spatial_Function'] == 'RadialGauss'
        self.table['Spatial_Function'][m] = 'RadialGaussian'
        self.table['TS'] = self.table['Signif_Avg'] * self.table['Signif_Avg']


        m = self.table['SpectrumType'] == 'PLSuperExpCutoff'
        self.table['SpectrumType'][m] = 'PLSuperExpCutoff2'

        self._fill_params(self.table)

    @staticmethod
    def _fill_params(tab):

        print("here")

        tab['param_values'] = np.nan * np.ones((len(tab), 10))

        # PowerLaw
        # Prefactor, Index, Scale
        m = tab['SpectrumType'] == 'PowerLaw'
        idxs = {k: i for i, k in
                enumerate(get_function_par_names('PowerLaw'))}
        tab['param_values'][m, idxs['Prefactor']] = tab['PL_Flux_Density'][m]
        tab['param_values'][m, idxs['Index']] = -1.0 * tab['PL_Index'][m]
        tab['param_values'][m, idxs['Scale']] = tab['Pivot_Energy'][m]

        # PLSuperExpCutoff2 or PLSuperExpCutoff
        # Prefactor, Index1, Scale, Expfactor, Index2
        m = tab['SpectrumType'] == 'PLSuperExpCutoff2'
        idxs = {k: i for i, k in
                enumerate(get_function_par_names('PLSuperExpCutoff2'))}
        tab['param_values'][m, idxs['Prefactor']] = (tab['PLEC_Flux_Density'][m] *
                                                     np.exp(tab['PLEC_Expfactor'][m] *
                                                            tab['Pivot_Energy'][m] **
                                                            tab['PLEC_Exp_Index'][m]))
        tab['param_values'][m, idxs['Index1']] = -1.0 * tab['PLEC_Index'][m]
        tab['param_values'][m, idxs['Scale']] = tab['Pivot_Energy'][m]
        tab['param_values'][m, idxs['Expfactor']] = tab['PLEC_Expfactor'][m]
        tab['param_values'][m, idxs['Index2']] = tab['PLEC_Exp_Index'][m]

        # LogParabola
        # norm, alpha, beta, Eb
        m = tab['SpectrumType'] == 'LogParabola'
        idxs = {k: i for i, k in
                enumerate(get_function_par_names('LogParabola'))}
        tab['param_values'][m, idxs['norm']] = tab['LP_Flux_Density'][m]
        tab['param_values'][m, idxs['alpha']] = tab['LP_Index'][m]
        tab['param_values'][m, idxs['beta']] = tab['LP_beta'][m]
        tab['param_values'][m, idxs['Eb']] = tab['Pivot_Energy'][m]


class CatalogFL8Y(Catalog):
    """This class supports releases the preliminary 8-yr point-source
    list (FL8Y).  See
    https://fermi.gsfc.nasa.gov/ssc/data/access/lat/fl8y/.
    """

    def __init__(self, fitsfile=None, extdir=None):

        if extdir is None:
            extdir = os.path.join('$FERMIPY_DATA_DIR', 'catalogs',
                                  'Extended_archive_v18')

        if fitsfile is None:
            fitsfile = os.path.join(fermipy.PACKAGE_DATA, 'catalogs',
                                    'gll_psc_8year_v5.fit')

        #hdulist = fits.open(fitsfile)
        table = Table.read(fitsfile, hdu=1)
        table_extsrc = Table.read(fitsfile, 'ExtendedSources')
        table_extsrc.meta.clear()

        strip_columns(table)
        strip_columns(table_extsrc)
        if 'Spatial_Function' not in table_extsrc.colnames:
            table_extsrc.add_column(Column(name='Spatial_Function', dtype='U20',
                                           length=len(table_extsrc)))
            table_extsrc['Spatial_Function'] = 'SpatialMap'

        table = join_tables(table, table_extsrc,
                            'Extended_Source_Name', 'Source_Name',
                            ['Model_Form', 'Model_SemiMajor',
                             'Model_SemiMinor', 'Model_PosAng',
                             'Spatial_Filename', 'Spatial_Function'])
        table.sort('Source_Name')
        super(CatalogFL8Y, self).__init__(table, extdir)

        excol = np.zeros((len(table)), 'bool')
        for i, exname in enumerate(table['Extended_Source_Name']):
            if len(exname.strip()) > 0:
                excol[i] = True

        self.table['extended'] = excol
        self.table['Extended'] = excol

        scol = Column(name='Spatial_Function', dtype='U20',
                      data=self.table['Spatial_Function'].data)
        self.table.remove_column('Spatial_Function')
        self.table['Spatial_Function'] = scol

        m = self.table['Spatial_Function'] == 'RadialGauss'
        self.table['Spatial_Function'][m] = 'RadialGaussian'
        self.table['TS'] = self.table['Signif_Avg'] * self.table['Signif_Avg']
        self._fill_params(self.table)

    @staticmethod
    def _fill_params(tab):

        tab['param_values'] = np.nan * np.ones((len(tab), 10))

        # PowerLaw
        # Prefactor, Index, Scale
        m = tab['SpectrumType'] == 'PowerLaw'
        idxs = {k: i for i, k in
                enumerate(get_function_par_names('PowerLaw'))}
        tab['param_values'][m, idxs['Prefactor']] = tab['Flux_Density'][m]
        tab['param_values'][m, idxs['Index']] = -1.0 * tab['PL_Index'][m]
        tab['param_values'][m, idxs['Scale']] = tab['Pivot_Energy'][m]

        # PLSuperExpCutoff2
        # Prefactor, Index1, Scale, Expfactor, Index2
        m = tab['SpectrumType'] == 'PLSuperExpCutoff2'
        idxs = {k: i for i, k in
                enumerate(get_function_par_names('PLSuperExpCutoff2'))}
        tab['param_values'][m, idxs['Prefactor']] = (tab['Flux_Density'][m] *
                                                     np.exp(tab['PLEC_Expfactor'][m] *
                                                            tab['Pivot_Energy'][m] **
                                                            tab['PLEC_Exp_Index'][m]))
        tab['param_values'][m, idxs['Index1']] = -1.0 * tab['PLEC_Index'][m]
        tab['param_values'][m, idxs['Scale']] = tab['Pivot_Energy'][m]
        tab['param_values'][m, idxs['Expfactor']] = tab['PLEC_Expfactor'][m]
        tab['param_values'][m, idxs['Index2']] = tab['PLEC_Exp_Index'][m]

        # LogParabola
        # norm, alpha, beta, Eb
        m = tab['SpectrumType'] == 'LogParabola'
        idxs = {k: i for i, k in
                enumerate(get_function_par_names('LogParabola'))}
        tab['param_values'][m, idxs['norm']] = tab['Flux_Density'][m]
        tab['param_values'][m, idxs['alpha']] = tab['LP_Index'][m]
        tab['param_values'][m, idxs['beta']] = tab['LP_beta'][m]
        tab['param_values'][m, idxs['Eb']] = tab['Pivot_Energy'][m]
