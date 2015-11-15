from qfrm import *

class LowExercisePrice(OptionValuation):
    """ LowExercisePrice option class.


    Inherits all methods and properties of OptionValuation class.
    """
    def calc_px(self, method='BS', nsteps=None, npaths=None, keep_hist=False):
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

        Examples
        --------
        >>> s = Stock(S0=19.6, vol=.21)
        >>> o = LowExercisePrice(ref=s,T=5, rf_r=.05)
        >>> o.calc_px(method='LT',nsteps=4)
        LowExercisePrice
        T: 5
        frf_r: 0
        px_spec: qfrm.PriceSpec
          LT_specs:
            a: 1.0644944589178593
            d: 0.7907391503193345
            df_T: 0.7788007830714049
            df_dt: 0.9394130628134758
            dt: 1.25
            p: 0.5776642331186062
            u: 1.264639545918723
          keep_hist: false
          method: LT
          nsteps: 4
          px: 19.592211992169272
          sub_method: Binomial tree with the strike price is $0.01; Hull Ch.135
        ref: qfrm.Stock
          S0: 19.6
          curr: null
          desc: null
          q: 0
          tkr: null
          vol: 0.21
        rf_r: 0.05
        seed0: null

        >>> s = Stock(S0=19.6, vol=.30)
        >>> o = LowExercisePrice(ref=s,T=5, rf_r=.10)
        >>> o.calc_px(method='LT',nsteps=2,keep_hist=True).px_spec.ref_tree  # prints reference tree
        ((19.600000000000005,),
         (12.196974354006297, 31.496335800182806),
         (7.59011139756568, 19.6, 50.613222899891674))

        >>> s = Stock(S0=19.6, vol=.30)
        >>> o = LowExercisePrice(ref=s,T=5, rf_r=.10)
        >>> o.plot_px_convergence(nsteps_max=30)  # Not working until qfrm.OptionValuation.plot_px_convergence is updated

        Returns
        -------
        self : LowExercisePrice

        .. sectionauthor:: Runmin Zhang


        See Also
        --------
        [1] Wikipedia: Low Exercise Price Option - https://en.wikipedia.org/wiki/Low_Exercise_Price_Option
        [2] LEPOs Explanatory Booklet http://www.asx.com.au/documents/resources/UnderstandingLEPOs.pdf
       """


        self.px_spec = PriceSpec(method=method, nsteps=nsteps, npaths=npaths, keep_hist=keep_hist)
        return getattr(self, '_calc_' + method.upper())()

    def _calc_BS(self):
        """ Internal function for option valuation.

        Returns
        -------
        self: LowExercisePrice

        .. sectionauthor::

        """

        return self

    def _calc_LT(self):
        """ Internal function for option valuation.
        Modified from European Call Option.

        Returns
        -------
        self: LowExercisePrice.

        .. sectionauthor:: Runmin Zhang

        .. note::



        Examples
        -------
        """

        from numpy import cumsum, log, arange, insert, exp, sqrt, sum, maximum

        n = getattr(self.px_spec, 'nsteps', 3)
        _ = self.LT_specs(n)

        S = self.ref.S0 * _['d'] ** arange(n, -1, -1) * _['u'] ** arange(0, n + 1)

        O = maximum((S - 0.01), 0)          # terminal option payouts
        S_tree, O_tree = None, None

        if getattr(self.px_spec, 'keep_hist', False):
            S_tree = (tuple([float(s) for s in S]),)
            O_tree = (tuple([float(o) for o in O]),)

            for i in range(n, 0, -1):
                O = _['df_dt'] * ((1 - _['p']) * O[:i] + ( _['p']) * O[1:])  #prior option prices (@time step=i-1)
                S = _['d'] * S[1:i+1]                   # prior stock prices (@time step=i-1)

                S_tree = (tuple([float(s) for s in S]),) + S_tree
                O_tree = (tuple([float(o) for o in O]),) + O_tree

            out = O_tree[0][0]
        else:
            csl = insert(cumsum(log(arange(n) + 1)), 0, 0)         # logs avoid overflow & truncation
            tmp = csl[n] - csl - csl[::-1] + log(_['p']) * arange(n + 1) + log(1 - _['p']) * arange(n + 1)[::-1]
            out = (_['df_T'] * sum(exp(tmp) * tuple(O)))

        self.px_spec.add(px=float(out), sub_method='Binomial tree with the strike price is $0.01; Hull Ch.135',
                         LT_specs=_, ref_tree=S_tree, opt_tree=O_tree)

        return self


    def _calc_MC(self, nsteps=3, npaths=4, keep_hist=False):
        """ Internal function for option valuation.

        Returns
        -------
        self: Basket
        .. sectionauthor::

        Notes
        -----


        """
        return self

    def _calc_FD(self, nsteps=3, npaths=4, keep_hist=False):
        """ Internal function for option valuation.

        Returns
        -------
        self: Barrier

        .. sectionauthor::

        """
        return self



