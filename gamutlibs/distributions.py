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
    Organize the candiate distribution objects for probability plotting.

    The main attribute of CandidateDistributions is the list 'dists'.  User-
    specified distributions for consideration are added to and removed from
    this list.  This list also serves as an iterable item when data and/or
    quantile calculation method are changed.
    """
    
    def __init__(self):
        """initialize the emtpy list for 'dists'"""

        self.dists = list()

        
    def add_distribution(self,
                         dist_name,
                         shape_fac_count,
                         shape_factors,
                         samples):
                         
        """Store samples to dist_obj, compute values, and append to 'dists' """
        dist_obj = SciPyContDist(dist_name, shape_fac_count)
        dist_obj.set_shapes(*shape_factors)
        self._calc_results(dist_obj, samples)
        self.dists.append(dist_obj)


    def _calc_results(self, dist_obj, samples):
        """Store samples; calc. quantiles, perform regression for dist_obj."""
        results = scipy.stats.probplot(samples,
                                       dist=dist_obj.get_label(),
                                       sparams=(dist_obj.get_shapes() ))
        dist_obj.feed_pplot_data(results[0], results[1])
        dist_obj.MLE_fit()


    def calc_all(self, samples, qmethod_str):
        """Perform prob. plot calcs for all distributions in self.dists."""
        for dist_obj in self.dists:
            self._calc_results(dist_obj, samples)


    def get_count(self):
        """Return the number of candidate distributions in self.dists"""

        return len(self.dists)


    def get_obj(self,index):
        """Get distribution object using its index in the list."""

        return self.dists[index]


    def remove_all(self):
        """Empty the list of candidate distributions."""

        self.dists = list()

        
    def remove_dist(self, dist_index):
        """Remove candidate distribution by its index in self.dists."""
        
        self.dists.pop(dist_index)



class SciPyContDist():
    """
    Register, instantiate, and define methods for supported distributions.
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
        return self.label
    
    def get_shape_count(self):
        return self.shape_count

    
    def get_loc(self):
        return self.loc

    def set_loc(self, value):
        self.loc = value

        
    def get_scale(self):
        return self.scale


    def set_scale(self, value):
        self.scale = value


    def set_shapes(self, *values):
        _ =[self._set_shape(value, ii) for ii, value in enumerate(values)]


    def _set_shape(self, value, index):
        if (self.shape_count != 0) and (index >= self.shape_count):
            print("Error, specified index exceeds shape count")
            sys.exit()
        name = "shape" + str(index + 1)
        self.shapes.update({name : value})       


    def get_shapes(self):
        shape_vals = [v for k,v in self.shapes.items()]
        return shape_vals


    def get_r2(self):
        return self.r2

    def feed_pplot_data(self,
                        plot_data,
                        lin_regress_data):
        self.x     = plot_data[0]               # quantiles
        self.y     = plot_data[1]               # ordered samples
        self.scale = lin_regress_data[0]        # slope
        self.loc   = lin_regress_data[1]        # intercept
        self.r2    = (lin_regress_data[2])**2.0 # coeff of determination


    def _calc_pdf_cdf(self, num_points=1000):
        """Populate a pdf-cdf data from scipy object."""

        # Note: do not include 1st or last points, which may correspond to 
        # +/- infinite
        self.cdf_vals = np.linspace(1.0/num_points,
                                    (num_points-1)/num_points,
                                    num_points-2)
        self.scipy_vals = self.scipy_obj.ppf(self.cdf_vals)
        self.pdf_vals = self.scipy_obj.pdf(self.scipy_vals)


    def MLE_fit(self):
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
        
        self.scipy_obj = eval(self.scipy_command)

    def get_scipy_command(self):
        return self.scipy_command

    def _create_scipy_obj(self):
        self.scipy_obj = eval(self.get_scipy_command())

    def create_pplot(self, axes):
        """Draw probabaility plot of data on 'axes'"""

        # slope    <=> scale
        # interept <=> location
        liny = lambda x: self.scale * x + self.loc
        xmin, xmax = np.min(self.x), np.max(self.x)
        ymin, ymax = liny(xmin), liny(xmax)
        axes.plot(self.x,
                  self.y,
                  'ro',
                  label="Samples")
        axes.plot([xmin, xmax],
                  [liny(xmin), liny(xmax)],
                  '-k',
                  label="Regression")
        eq = "f(t) = %6.4E*t +  %6.4E\n$R^2$=%.4f" \
            % (self.scale, self.loc, self.r2)
        axes.text(0.1*xmax + 0.9*xmin,
                 0.1*ymin + 0.9*ymax,
                 eq)
        axes.set_xlabel("Theoretical quantiles")
        axes.set_ylabel("Ordered Values")
        axes.set_title(self.label)
        axes.legend(loc=4)
        axes.grid(which='major')


    def plot_pdfcdf(self, axes, samples=True):
        """Draw pdf and cdfs of resulting scipy distribution object"""
        
        self._create_scipy_obj()
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
        quantiles = scipy.stats.morestats._calc_uniform_order_statistic_medians(len(self.x))
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
