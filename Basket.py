from OptionValuation import *
from numpy.random import multivariate_normal, seed
from numpy import sqrt, mean, matrix, transpose, diag, dot, repeat, exp

class Basket(OptionValuation):
    """ European option class.

    Inherits all methods and properties of OptionValuation class.
    """

    def calc_px(self, method='BS', mu = (0.1,0.2,0.5), weight = (0.5,0.3,0.2),
                corr = [[1,0,0],[0,1,0],[0,0,1]], nsteps=None, npaths=None, keep_hist=False):
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
        mu : tuple
                Expected return of assets in a basket
        weight: tuple
                 Weights of assets in a basket
        Corr: list
                 Correlation Matrix of assets in a basket

        Returns
        -------
        self : Basket

        :Authors:
          Hanting Li <hl45@rice.edu>

        Notes
        -----
        The examples can be verified at:
          http://www.infres.enst.fr/~decreuse/pricer/en/index.php?page=panier.html
        The results might differ a little due to the simulations.
        Since it takes time to run more paths and steps, the number of simulations is not very large in examples.
        To improve accuracy, please improve the npaths and nsteps.

        Examples
        -------

        >>> s = Stock(S0=(42,55,75), vol=(.20,.30,.50))
        >>> o = Basket(ref=s, right='call', K=40, T=.5, rf_r=.1, desc='Hull p.612')

        >>> o.calc_px(method='MC',mu=(0.05,0.1,0.05),weight=(0.3,0.5,0.2),corr=[[1,0,0],[0,1,0],[0,0,1]],\
        npaths=10,nsteps=100).px_spec # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        PriceSpec...px: 15.317306061...

        >>> s = Stock(S0=(50,85,65,80,75), vol=(.20,.10,.05,.20,.30))
        >>> o = Basket(ref=s, right='put', K=80, T=1, rf_r=.05, desc='Hull p.612')

        >>> o.calc_px(method='MC',mu=(0.05,0,0.1,0,0),weight=(0.2,0.2,0.2,0.2,0.2),corr=[[1,0,0,0.9,0],\
        [0,1,0,0,0],[0,0,1,-0.1,0],[0.9,0,-0.1,1,0],[0,0,0,0,1]],\
        npaths=100,nsteps=100).px_spec.px   # save interim results to self.px_spec. Equivalent to repr(o)
        6.120469912146624

        >>> s = Stock(S0=(30,50), vol=(.20,.15))
        >>> o = Basket(ref=s, right='put', K=55, T=3, rf_r=.05, desc='Hull p.612')

        >>> o.calc_px(method='MC',mu=(0.06,0.05),weight=(0.4,0.6),corr=[[1,0.7],[0.7,1]],\
        npaths=10,nsteps=1000).px_spec.px
        7.236146325452368

        >>> from pandas import Series
        >>> expiries = range(1,11)
        >>> O = Series([o.update(T=t).calc_px(method='MC',mu=(0.06,0.05),weight=(0.4,0.6),\
        corr=[[1,0.7],[0.7,1]],npaths=2,nsteps=3).px_spec.px for t in expiries], expiries)
        >>> O.plot(grid=1, title='Price vs expiry (in years)') # doctest: +ELLIPSIS
        <matplotlib.axes._subplots.AxesSubplot object at ...>
        >>> import matplotlib.pyplot as plt
        >>> plt.show()


        """
        self.px_spec = PriceSpec(method=method, nsteps=nsteps, npaths=npaths, keep_hist=keep_hist)
        self.mu = mu
        self.weight = weight
        self.corr = corr
        self.npaths = npaths
        self.nsteps = nsteps
        return getattr(self, '_calc_' + method.upper())()

    def _calc_BS(self):
        """ Internal function for option valuation.

        Returns
        -------
        self: European

        .. sectionauthor:: Oleg Melnikov

        """

        return self

    def _calc_LT(self):
        """ Internal function for option valuation.

        Returns
        -------
        self: European

        .. sectionauthor:: Oleg Melnikov

        .. note::
        Implementing Binomial Trees:   http://papers.ssrn.com/sol3/papers.cfm?abstract_id=1341181

        """

        return self

    def _calc_MC(self, keep_hist=False):
        """ Internal function for option valuation.

        Returns
        -------
        self: European

        :Authors:
            Hanting Li <hl45@rice.edu>

        Notes
        -----
        Implementing Binomial Trees:   http://papers.ssrn.com/sol3/papers.cfm?abstract_id=1341181

        """


        _ = self

        # Define the parameters
        S0 = _.ref.S0
        vol = _.ref.vol
        mu = _.mu
        corrM = _.corr
        nsteps = _.nsteps
        npaths = _.npaths

        # Compute Deltat and number of assets
        deltat = _.T/nsteps
        Nasset = len(vol)

        # Compute the stock price at t
        def calS(St,mu,sigma,param):
            deltaS = mu*St*deltat + sigma*St*param*sqrt(deltat)
            S_update = St+deltaS
            return(S_update.item())

        # Generate one path
        def one_path(S0,mu,vol,param):
            S0 = (S0,)
            for i in range(nsteps):
                parami = param[i]
                S0 = S0 + (calS(S0[len(S0)-1],mu,vol,parami),)
            return(S0)

        # Define n paths matrix
        priceNpath = ()

        # Compute covariance matrix from correlation matrix
        covM = dot(dot(diag(vol),(corrM)),diag(vol))

        # Set seed
        seed(10987)
        # Generate random numbers
        param = multivariate_normal(repeat(0,Nasset),covM,nsteps)
        param = tuple(zip(*param))

        # Generate N paths
        for i in range(npaths):
            price = list(map(one_path,S0,mu,vol,param))
            wprice = transpose(matrix(price))*transpose(matrix(_.weight))
            wprice = tuple(wprice.ravel().tolist()[0])
            priceNpath = priceNpath + (wprice,)

        # Terminal Payoff
        payoff = max(0,_.signCP*(mean(tuple(zip(*priceNpath))[nsteps])-_.K))

        self.px_spec.add(px=float(payoff*exp(-_.rf_r*_.T)), sub_method='standard; Hull p.612')

        return self


    def _calc_FD(self, nsteps=3, npaths=4, keep_hist=False):
        """ Internal function for option valuation.

        Returns
        -------
        self: European

        .. sectionauthor::

        """
        return self
