###############################################################################
#
#    gamut
#    Copyright (C) 2017,  Nicholas A. Reynolds
#
#    Full License Available in LICENSE file at
#    https://github.com/nicholasareynolds/gamut
#
###############################################################################
import scipy.stats
import numpy as np
import sys

class CandidateDistributions:
    """
    Organize the candidate distribution objects for prob. plotting and MLE fitting.

    CandidateDistributions is the backend of 'gamut'. The main attribute of
    CandidateDistributions is the list 'dists'.  User- specified distributions
    for consideration are added to and removed from this list.  This list also
    serves as an iterable item when data or outlier information is changed.
    """
    
    def __init__(self):
        """
        Initialize the emtpy list for 'dists'
        """
        self.dists = list()

        
    def add_distribution(self,
                         dist_name,
                         shape_fac_count,
                         shape_factors,
                         samples):
        """
        Initialize distr. object, compute regress. values, and append obj 'dists'
        """
        dist_obj = SciPyContDist(dist_name, shape_fac_count)
        dist_obj.set_shapes(*shape_factors)
        self._calc_results(dist_obj, samples)
        self.dists.append(dist_obj)


    def _calc_results(self, dist_obj, samples):
        """
        Perform prob. plot regression and max. likelihood est. fit for dist_obj.
        """
        results = scipy.stats.probplot(samples,
                                       dist=dist_obj.get_label(),
                                       sparams=(dist_obj.get_shapes() ))
        dist_obj.feed_pplot_data(results[0], results[1])
        dist_obj.MLE_fit()


    def calc_all(self, samples):
        """
        Perform regression calcs for all distributions in self.dists.
        """
        for dist_obj in self.dists:
            self._calc_results(dist_obj, samples)


    def get_count(self):
        """
        Return the current number of candidate distributions in self.dists
        """
        return len(self.dists)


    def get_obj(self,index):
        """
        Return distribution object using its rank in the list.
        """

        return self.dists[index]


    def remove_all(self):
        """
        Empty the list of candidate distributions.
        """

        self.dists = list()

        
    def remove_dist(self, dist_index):
        """
        Remove candidate distribution by its index in self.dists.
        """
        
        self.dists.pop(dist_index)



class SciPyContDist():
    """
    Register, instantiate, and define methods for supported distributions.


    SciPyContDist is the distribution object for the distributions that make up
    the CandidateDistributions.dists list attribute.  SciPyConstDist is called
    from within the CandidateDistributions method 'add_distribution'.
    
    SciPyContDist also contains methods which call the scipy.stats.probplot
    and scipy.stats.label.fit (MLE) functions that are used to fit the
    distribution to the data.
    
    Usage:

    distribution_instance = SciPyContDist(label, **kwargs)
        
    where:
        - label is the SciPy moniker for a continuous distribution
        - shape_count is the number of shape parameters present in the
          distribution (Default=0)
        - loc is the value of the distribution's location parameter.
          (Default = None)
        - scale is the value of the distribution's scale parameter.
        
    Currently, 'gamut' has database of SciPy continuous distributions and
    associated values for shape_count;  these values are simulatenous populated
    when SciPyContDist is instantiated within
    CandidateDistributions.add_distribution using an dict.iteritems() loop.
    """
    
    def __init__(self,
                 label,
                 shape_count=0,
                 loc=None,
                 scale=None):

        self.label       = label
        self.shape_count = shape_count
        self.loc         = None
        self.scale       = None
        self.shapes      = dict()


    def get_label(self):
        """
        Return the SciPy moniker of this instance of SciPyContDist
        """
        return self.label
    
    def get_shape_count(self):
        """
        Return the number of shape parameters belonging to this SciPyContDist instance.
        """
        return self.shape_count

    
    def get_loc(self):
        """
        Return the value of the location parameter
        """
        return self.loc

    def set_loc(self, value):
        """
        Assign a value to the location parameter attribute, self.loc
        """
        self.loc = value
        
    def get_scale(self):
        """
        Return the value of the scale parameter
        """
        return self.scale

    def set_scale(self, value):
        """
        Assign a value to the scale parameter attribute, self.scale
        """
        self.scale = value

    def set_shapes(self, *values):
        """
        Assign values to the shape parameters dict attribute, self.shapes
        """
        _ =[self._set_shape(value, ii) for ii, value in enumerate(values)]

    def _set_shape(self, value, index):
        """
        Update the shape parameter dictionary attribute with a new value for
        shape parameter of rank index
        """
        if (self.shape_count != 0) and (index >= self.shape_count):
            print("Error, specified index exceeds shape count")
            sys.exit()
        name = "shape" + str(index + 1)
        self.shapes.update({name : value})       

    def get_shapes(self):
        """
        Return a sequential list of the shape parameter values
        """
        shape_vals = [v for k,v in self.shapes.items()]
        return shape_vals


    def get_r2(self):
        """
        Return the coefficient of determination for the probability plot
        """
        return self.r2

    def feed_pplot_data(self,
                        plot_data,
                        lin_regress_data):
        """
        Store results from prob. plot regression as attributes
        """
        self.x     = plot_data[0]               # quantiles
        self.y     = plot_data[1]               # ordered samples
        self.scale = lin_regress_data[0]        # slope
        self.loc   = lin_regress_data[1]        # intercept
        self.r2    = (lin_regress_data[2])**2.0 # coeff of determination


    def _calc_pdf_cdf(self, num_points=1000):
        """
        Construct PDF and CDF curves of fit the SciPy distribution
        """

        # Note: do not include 1st or last points, which may correspond to 
        # +/- infinite
        self.cdf_vals = np.linspace(1.0/num_points,
                                    (num_points-1)/num_points,
                                    num_points-2)
        self.scipy_vals = self.scipy_obj.ppf(self.cdf_vals)
        self.pdf_vals = self.scipy_obj.pdf(self.scipy_vals)


    def MLE_fit(self):
        """
        Fit dist. parameters to data using maximum likelihood estimate method
        """
        samples=self.y
        fit_params = \
            eval("scipy.stats.%s.fit(samples)" % self.get_label())
        scale = fit_params[-1]
        loc = fit_params[-2]
        shapes = fit_params[:-2]
        self.fit_obj = SciPyContDist(self.get_label(),
                                     loc=loc,
                                     scale=scale,
                                     shape_count=len(shapes))
        self.fit_obj.set_shapes(*shapes)
        
        # Assemble scipy call string
        self.scipy_command = "scipy.stats.%s(" % self.get_label()
        for shape in shapes:
            self.scipy_command += "%10.6e, " % shape
        self.scipy_command += "loc=%10.6e, scale=%10.6e)" % (loc, scale)
        
        # Instantiate a frozen SciPy distribution using MLE fit param. values
        self.scipy_obj = self.scipy_obj = eval(self.get_scipy_command())

    def get_scipy_command(self):
        """
        Return the python command to instantiate a frozen SciPy distribution,
        using the values the the MLE fitting
        """
        return self.scipy_command

    def create_pplot(self, axes):
        """
        Draw probabaility plot of data on 'axes'
        """
        # slope    <=> scale
        # interept <=> location
        
        # Linear regression line
        liny = lambda x: self.scale * x + self.loc
        xmin, xmax = np.min(self.x), np.max(self.x)
        ymin, ymax = liny(xmin), liny(xmax)
        axes.plot([xmin, xmax],
                  [liny(xmin), liny(xmax)],
                  '-k',
                  label="Regression")

        axes.plot(self.x,
                  self.y,
                  'ro',
                  label="Samples")

        eq = "OV(TQ) = %6.4E*TQ +  %6.4E\n$R^2$=%.4f" \
            % (self.scale, self.loc, self.r2)
        axes.text(0.1*xmax + 0.9*xmin,
                 0.1*ymin + 0.9*ymax,
                 eq)
        axes.set_xlabel("Theoretical Quantiles (TQ)")
        axes.set_ylabel("Ordered Values (OV)")
        axes.set_title(self.label)
        axes.legend(loc=4)
        axes.grid(which='major')


    def plot_pdfcdf(self, axes, samples=True):
        """
        Draw PDF and CDF fitted SciPy distribution on the provides axes
        """
        self._calc_pdf_cdf()
        
        # PDF Plot
        axes.plot(self.scipy_vals,
                  self.pdf_vals,
                  '-b',
                  label="PDF")
        axes.set_xlabel("Parameter Values")
        axes.set_ylabel("PDF Value")
        axes.set_title(self.label)
        axes.legend(loc=2)
        
        ax2 = axes.twinx()
        ax2.plot(self.scipy_vals,
                 self.cdf_vals,
                 '-r',
                 label="CDF")
        ax2.set_ylabel("CDF Value")
        
        # Filliben's estimate of the ordered statistic medians
        #     Filliben, J. J. (February 1975), The Probability Plot Correlation
        #     Coefficient Test for Normality, Technometrics, pp. 111-117.
        quantiles = \
            scipy.stats.morestats._calc_uniform_order_statistic_medians(len(self.x))

        ax2.plot(self.y,
                 quantiles,
                 'ro')
        ax2.legend(loc=1)
    
# Substantial portions of this file were taken from:
# 
#     https://github.com/nicholasareynolds/pplotpy
#
# Below is the MIT license file from that program
#
# ---
#
# pplotpy
# Copyright (c) 2017 Nicholas A. Reynolds
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
