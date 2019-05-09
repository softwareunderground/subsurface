# -*- coding: utf 8 -*-
"""
Python installation file.
"""
class Curve(object):

    def __init__(self, data, params=None):

        obj = np.asarray(data).view(cls).copy()

        params = params or {}

        for k, v in params.items():
            setattr(obj, k, v)

        return

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def _repr_html_(self):
        """
        Jupyter Notebook magic repr function.
        """
        if self.size < 10:
            return np.ndarray.__repr__(self)
        attribs = self.__dict__.copy()

        # Header.
        row1 = '<tr><th style="text-align:center;" colspan="2">{} [{{}}]</th></tr>'
        rows = row1.format(attribs.pop('mnemonic'))
        rows = rows.format(attribs.pop('units', '&ndash;'))
        row2 = '<tr><td style="text-align:center;" colspan="2">{:.4f} : {:.4f} : {:.4f}</td></tr>'
        rows += row2.format(attribs.pop('start'), self.stop, attribs.pop('step'))

        # Curve attributes.
        s = '<tr><td><strong>{k}</strong></td><td>{v}</td></tr>'
        for k, v in attribs.items():
            rows += s.format(k=k, v=v)

        # Curve stats.
        rows += '<tr><th style="border-top: 2px solid #000; text-align:center;" colspan="2"><strong>Stats</strong></th></tr>'
        stats = self.get_stats()
        s = '<tr><td><strong>samples (NaNs)</strong></td><td>{samples} ({nulls})</td></tr>'
        s += '<tr><td><strong><sub>min</sub> mean <sup>max</sup></strong></td>'
        s += '<td><sub>{min:.2f}</sub> {mean:.3f} <sup>{max:.2f}</sup></td></tr>'
        rows += s.format(**stats)

        # Curve preview.
        s = '<tr><th style="border-top: 2px solid #000;">Depth</th><th style="border-top: 2px solid #000;">Value</th></tr>'
        rows += s.format(self.start, self[0])
        s = '<tr><td>{:.4f}</td><td>{:.4f}</td></tr>'
        for depth, value in zip(self.basis[:3], self[:3]):
            rows += s.format(depth, value)
        rows += '<tr><td>⋮</td><td>⋮</td></tr>'
        for depth, value in zip(self.basis[-3:], self[-3:]):
            rows += s.format(depth, value)

        # Footer.
        # ...

        # End.
        html = '<table>{}</table>'.format(rows)
        return html

    @property
    def values(self):
        return np.array(self)

    @property
    def stop(self):
        """
        The stop depth. Computed on the fly from the start,
        the step, and the length of the curve.
        """
        return self.start + (self.shape[0] - 1) * self.step

    @property
    def basis(self):
        """
        The depth or time basis of the curve's points. Computed
        on the fly from the start, stop and step.

        Returns
            ndarray. The array, the same length as the curve.
        """
        return np.linspace(self.start, self.stop, self.shape[0], endpoint=True)

    def describe(self):
        """
        Return basic statistics about the curve.
        """
        stats = {}
        stats['samples'] = self.shape[0]
        stats['nulls'] = self[np.isnan(self)].shape[0]
        stats['mean'] = float(np.nanmean(self.real))
        stats['min'] = float(np.nanmin(self.real))
        stats['max'] = float(np.nanmax(self.real))
        return stats

    def get_alias(self, alias):
        """
        Given a mnemonic, get the alias name(s) it falls under. If there aren't
        any, you get an empty list.
        """
        alias = alias or {}
        return [k for k, v in alias.items() if self.mnemonic in v]

    def plot(self, ax=None, **kwargs):
        """
        Plot a curve.

        Args:
            ax (ax): A matplotlib axis.
            return_fig (bool): whether to return the matplotlib figure.
                Default False.
            kwargs: Arguments for ``ax.set()``

        Returns:
            ax. If you passed in an ax, otherwise None.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(2, 10))
            return_ax = False
        else:
            return_ax = True

        ax.plot(self, self.basis, **kwargs)
        ax.set_title(self.mnemonic)  # no longer needed
        ax.set_xlabel(self.units)

        labels = ax.get_xticklabels()
        for label in labels:
            label.set_rotation(90)

        ax.set_ylim([self.stop, self.start])
        ax.grid('on', color='k', alpha=0.33, lw=0.33, linestyle='-')

        if return_ax:
            return ax
        else:
            return None

    def _read_at(self, d,
                 interpolation='linear',
                 index=False,
                 return_basis=False):
        """
        Private function. Implements read_at() for a single depth.

        Args:
            d (float)
            interpolation (str)
            index(bool)
            return_basis (bool)

        Returns:
            float
        """
        method = {'linear': utils.linear,
                  'none': None}

        i, d = utils.find_previous(self.basis,
                                   d,
                                   index=True,
                                   return_distance=True)

        if index:
            return i
        else:
            return method[interpolation](self[i], self[i+1], d)

    def read_at(self, d, **kwargs):
        """
        Read the log at a specific depth or an array of depths.

        Args:
            d (float or array-like)
            interpolation (str)
            index(bool)
            return_basis (bool)

        Returns:
            float or ndarray.
        """
        try:
            return np.array([self._read_at(depth, **kwargs) for depth in d])
        except:
            return self._read_at(d, **kwargs)

    def block(self,
              cutoffs=None,
              values=None,
              n_bins=0,
              right=False,
              function=None):
        """
        Block a log based on number of bins, or on cutoffs.

        Args:
            cutoffs (array)
            values (array): the values to map to. Defaults to [0, 1, 2,...]
            n_bins (int)
            right (bool)
            function (function): transform the log if you want.

        Returns:
            Curve.
        """
        # We'll return a copy.
        params = self.__dict__.copy()

        if (values is not None) and (cutoffs is None):
            cutoffs = values[1:]

        if (cutoffs is None) and (n_bins == 0):
            cutoffs = np.mean(self)

        if (n_bins != 0) and (cutoffs is None):
            mi, ma = np.amin(self), np.amax(self)
            cutoffs = np.linspace(mi, ma, n_bins+1)
            cutoffs = cutoffs[:-1]

        try:  # To use cutoff as a list.
            data = np.digitize(self, cutoffs, right)
        except ValueError:  # It's just a number.
            data = np.digitize(self, [cutoffs], right)

        if (function is None) and (values is None):
            return Curve(data, params=params)

        data = data.astype(float)

        # Set the function for reducing.
        f = function or utils.null

        # Find the tops of the 'zones'.
        tops, vals = utils.find_edges(data)

        # End of array trick... adding this should remove the
        # need for the marked lines below. But it doesn't.
        # np.append(tops, None)
        # np.append(vals, None)

        if values is None:
            # Transform each segment in turn, then deal with the last segment.
            for top, base in zip(tops[:-1], tops[1:]):
                data[top:base] = f(np.copy(self[top:base]))
            data[base:] = f(np.copy(self[base:]))  # See above
        else:
            for top, base, val in zip(tops[:-1], tops[1:], vals[:-1]):
                data[top:base] = values[int(val)]
            data[base:] = values[int(vals[-1])]  # See above

        return Curve(data, params=params)

    def _rolling_window(self, window_length, func1d, step=1, return_rolled=False):
        """
        Private function. Smoother for other smoothing/conditioning functions.

        Args:
            window_length (int): the window length.
            func1d (function): a function that takes a 1D array and returns a
                scalar.
            step (int): if you want to skip samples in the shifted versions.
                Don't use this for smoothing, you will get strange results.

        Returns:
            ndarray: the resulting array.
        """
        # Force odd.
        if window_length % 2 == 0:
            window_length += 1

        shape = self.shape[:-1] + (self.shape[-1], window_length)
        strides = self.strides + (step*self.strides[-1],)
        data = np.nan_to_num(self)
        data = np.pad(data, int(step*window_length//2), mode='edge')
        rolled = np.lib.stride_tricks.as_strided(data,
                                                 shape=shape,
                                                 strides=strides)
        result = np.apply_along_axis(func1d, -1, rolled)
        result[np.isnan(self)] = np.nan

        if return_rolled:
            return result, rolled
        else:
            return result

    def despike(self, window_length=33, samples=True, z=2):
        """
        Args:
            window (int): window length in samples. Default 33 (or 5 m for
                most curves sampled at 0.1524 m intervals).
            samples (bool): window length is in samples. Use False for a window
                length given in metres.
            z (float): Z score

        Returns:
            Curve.
        """
        window_length //= 1 if samples else self.step
        z *= np.nanstd(self)  # Transform to curve's units
        curve_sm = self._rolling_window(window_length, np.median)
        spikes = np.where(np.nan_to_num(self - curve_sm) > z)[0]
        spukes = np.where(np.nan_to_num(curve_sm - self) > z)[0]
        out = np.copy(self)
        params = self.__dict__.copy()
        out[spikes] = curve_sm[spikes] + z
        out[spukes] = curve_sm[spukes] - z
        return Curve(out, params=params)

    def apply(self, window_length, samples=True, func1d=None):
        """
        Runs any kind of function over a window.

        Args:
            window_length (int): the window length. Required.
            samples (bool): window length is in samples. Use False for a window
                length given in metres.
            func1d (function): a function that takes a 1D array and returns a
                scalar. Default: ``np.mean()``.

        Returns:
            Curve.
        """
        window_length /= 1 if samples else self.step
        if func1d is None:
            func1d = np.mean
        params = self.__dict__.copy()
        out = self._rolling_window(int(window_length), func1d)
        return Curve(out, params=params)

    smooth = apply


def from_las():
    """
    Instantiate a Curve object from a SEG-Y file.
    """

def from_lasio_curve(cls, curve,
                        depth=None,
                        basis=None,
                        start=None,
                        stop=None,
                        step=0.1524,
                        run=-1,
                        null=-999.25,
                        service_company=None,
                        date=None):
    """
    Makes a curve object from a lasio curve object and either a depth
    basis or start and step information.

    Args:
        curve (ndarray)
        depth (ndarray)
        basis (ndarray)
        start (float)
        stop (float)
        step (float): default: 0.1524
        run (int): default: -1
        null (float): default: -999.25
        service_company (str): Optional.
        data (str): Optional.

    Returns:
        Curve. An instance of the class.
    """
    data = curve.data
    unit = curve.unit

    # See if we have uneven sampling.
    if depth is not None:
        d = np.diff(depth)
        if not np.allclose(d - np.mean(d), np.zeros_like(d)):
            # Sampling is uneven.
            m = "Irregular sampling in depth is not supported. "
            m += "Interpolating to regular basis."
            warnings.warn(m)
            step = np.nanmedian(d)
            start, stop = depth[0], depth[-1]+0.00001  # adjustment
            basis = np.arange(start, stop, step)
            data = np.interp(basis, depth, data)
        else:
            step = np.nanmedian(d)
            start = depth[0]

    # Carry on with easier situations.
    if start is None:
        if basis is not None:
            start = basis[0]
            step = basis[1] - basis[0]
        else:
            raise CurveError("You must provide a basis or a start depth.")

    if step == 0:
        if stop is None:
            raise CurveError("You must provide a step or a stop depth.")
        else:
            step = (stop - start) / (curve.data.shape[0] - 1)

    # Interpolate into this.

    params = {}
    params['mnemonic'] = curve.mnemonic
    params['description'] = curve.descr
    params['start'] = start
    params['step'] = step
    params['units'] = unit
    params['run'] = run
    params['null'] = null
    params['service_company'] = service_company
    params['date'] = date
    params['code'] = curve.API_code

    return cls(data, params=params)

