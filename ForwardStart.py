from OptionValuation import *
from scipy.stats import *
from math import *

class ForwardStart(OptionValuation):
    """ ForwardStart option class

    Inherits all methods and properties of Optionvalueation class.
    """

    def calc_px(self, T_s=1, method='BS', nsteps=None, npaths=None, keep_hist=False):
        """ Wrapper function that calls appropriate valuation method.

        User passes parameters to calc_px, which saves them to local PriceSpec object
        and calls specific pricing function (_calc_BS,...).
        This makes significantly less docstrings to write, since user is not interfacing pricing functions,
        but a wrapper function calc_px().

        Parameters
        ----------
        method : str
                Required. Indicates a valuation method to be used: 'BS', 'LT', 'MC', 'FD'
        nsteps : int
                LT, MC, FD methods require number of times steps
        npaths : int
                MC, FD methods require number of simulation paths
        keep_hist : bool
                If True, historical information (trees, simulations, grid) are saved in self.px_spec object.
        T1 : float
             Required. Indicates the time that the option starts.
        Returns
        -------
        self : ForwardStart

        Notes
        -----
        [1] https://en.wikipedia.org/wiki/Forward_start_option  -- WikiPedia: Forward start option
        [2] http://www.stat.nus.edu.sg/~stalimtw/MFE5010/PDF/L2forward.pdf -- How to pricing forward start opions, resource for Example 1
        [3] http://www.globalriskguard.com/resources/deriv/fwd_4.pdf -- How to pricing forward start opions, resource for Example 2

        .. sectionauthor:: Runmin Zhang


        Examples
        --------
        #http://www.stat.nus.edu.sg/~stalimtw/MFE5010/PDF/L2forward.pdf
        >>> s = Stock(S0=50, vol=.15,q=0.05)
        >>> ForwardStart(ref=s, right='call', T=0.5, rf_r=.1).calc_px(T_s=0.5) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        ForwardStart
        T: 0.5
        _right: call
        _signCP: 1
        frf_r: 0
        px_spec: PriceSpec
          T_s: 0.5
          keep_hist: false
          method: BS
          px: 2.6287772667343705
        ref: Stock
          S0: 50
          curr: -
          desc: -
          q: 0.05
          tkr: -
          vol: 0.15
        rf_r: 0.1
        seed0: -
        <BLANKLINE>




        >>> s = Stock(S0=60, vol=.30,q=0.04)
        >>> ForwardStart(ref=s, K=66,right='call', T=0.75, rf_r=.08).calc_px(T_s=0.25) #http://www.globalriskguard.com/resources/deriv/fwd_4.pdf
        ForwardStart
        K: 66
        T: 0.75
        _right: call
        _signCP: 1
        frf_r: 0
        px_spec: PriceSpec
          T_s: 0.25
          keep_hist: false
          method: BS
          px: 4.406454339365007
        ref: Stock
          S0: 60
          curr: -
          desc: -
          q: 0.04
          tkr: -
          vol: 0.3
        rf_r: 0.08
        seed0: -
        <BLANKLINE>

        >>> from pandas import Series
        >>> expiries = range(1,11)
        >>> O = Series([ForwardStart(ref=s, K=66,right='call', T=0.75, rf_r=.08).update(T=t).calc_px(method='BS',T_s=0.25).px_spec.px for t in expiries], expiries)
        >>> O.plot(grid=1, title='ForwardStart option Price vs expiry (in years)') # doctest: +ELLIPSIS
        <matplotlib.axes._subplots.AxesSubplot object at ...>


        """


        self.px_spec = PriceSpec(T_s=T_s, method=method, nsteps=nsteps, npaths=npaths, keep_hist=keep_hist)
        return getattr(self, '_calc_' + method.upper())()


    def _calc_BS(self):
        """ Internal function for option valuation.

        Returns
        -------
        self: ForwardStart

        .. sectionauthor:: Runmin Zhang

        """

        _ = self

        # Verify the input
        try:
            right   =   _.right.lower()[0]
        except:
            print('Input error. right should be string')
            return False

        try:

            S0   =   float(_.ref.S0)
            T   =   float(_.T)
            T_s  =   float(_.px_spec.T_s)
            vol =   float(_.ref.vol)
            r   =   float(_.rf_r)
            q   =   float(_.ref.q)
        except:
            print('Input error. S, T, T1, vol, r, q should be floats.')
            return False

        try:
            K = float(_.K)
        except:
            K = S0

        assert right in ['c','p'], 'right should be either "call" or "put" '
        assert vol >= 0, 'vol >=0'
        assert T > 0, 'T > 0'
        assert T_s >=0, 'T_s >= 0'
        assert S0 >= 0, 'S >= 0'
        assert K >= 0, 'K >= 0'
        assert r >= 0, 'r >= 0'
        assert q >= 0, 'q >= 0'

        # Import external functions


        # Parameters in BSM
        d1 = (log(S0/K)+(r-q+vol**2/2)*T)/(vol*sqrt(T))
        d2 = d1 - vol*sqrt(T)


        # Calculate the option price
        if right == 'c':
            px = (S0*exp(-q*T)*norm.cdf(d1)-K*exp(-r*T)*norm.cdf(d2))*exp(-q*T_s)
        elif right == 'p':
            px = (K*exp(-r*T)*norm.cdf(-d2)-S0*exp(-q*T)*norm.cdf(-d1))*exp(-q*T_s)

        self.px_spec.add(px=float(Util.demote(px)), method='BS', sub_method=None)
        return self


    def _calc_LT(self):
        """ Internal function for option valuation.

        Returns
        -------
        self: PerpetualAmerican

        .. sectionauthor::

        """

        return self

    def _calc_MC(self):
        """ Internal function for option valuation.

        Returns
        -------
        self: PerpetualAmerican

        .. sectionauthor::

        Note
        ----

        """
        return self

    def _calc_FD(self):
        """ Internal function for option valuation.

        Returns
        -------
        self: PerpetualAmerican

        .. sectionauthor::

        Note
        ----

        """

        return self




