###############################################################################
#
#    pplotpy - a probability plotting tool for Python
#
#    Copyright (C) 2017,  Nicholas A. Reynolds
#
#    Full License Available in LICENSE file at
#    https://github.com/nicholasareynolds/pplotpy
#
###############################################################################

from scipy import stats
from scipy.special import erfinv
from . import quantiles

import numpy as np

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

        
    def add_distribution(self, dist_obj, samples, qmethod_str):
        """Store samples to dist_obj, compute values, and append to 'dists' """

        self._calc_results(dist_obj, samples, qmethod_str)
        self.dists.append(dist_obj)


    def _calc_results(self, dist_obj, samples, qmethod_str):
        """Store samples; calc. quantiles, perform regression for dist_obj."""

        dist_obj.feed_samples(samples)
        dist_obj.calc_quantiles(qmethod_str)
        dist_obj.eval_data()


    def calc_all(self, samples, qmethod_str):
        """Perform prob. plot calcs for all distributions in self.dists."""
        for dist_obj in self.dists:
            self._calc_results(dist_obj, samples, qmethod_str)


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



class SupportedDistributions():
    """
    Register, instantiate, and define methods for supported distributions.
    """

    # SupportedDistributions is a parent class, is never used on data

    subclasses = {}  # Empty container for distributions to be registered at

    
    def __init__(self, label):
        """Preserve tag/label of distribution as attribute self.label"""

        self.label = label
        self.loc = 0.0    # Default


    # Decorator to store distrib. subclass and its label to self.sublasses
    @classmethod
    def register_distribution(cls, dist_str):
        def decorator(subclass):
            cls.subclasses[dist_str] = subclass
            return subclass
        return decorator
    

    # Decorator to instantiate a distribution object from its label.
    @classmethod
    def create_subclass_instance(cls, dist_str):
        if dist_str not in cls.subclasses:
            raise ValueError("Invalid distribution: %s" %dist_str)
        return cls.subclasses[dist_str](dist_str)


    # Decorator to return the value of the location parameter, if it exists
    @classmethod
    def has_optional_loc_param(cls, dist_str):
        if dist_str not in cls.subclasses:
            raise ValueError("Invalid distribution: %s" %dist_str)
        return cls.subclasses[dist_str](dist_str).loc_optional  


    def feed_samples(self, samples):
        """Store samples and num. of samples in the object as attributes."""

        self.samples = np.sort(samples)
        self.nsamples = np.size(samples)


    def get_label(self):
        """Get the label associated with this distribution"""

        return self.label


    def set_location(self, loc):
        """Store the location parameter value as an attribute."""

        if self.has_loc:
            self.loc = loc


    def get_scale_str(self):
        """Return the scale parameter value as a string, if applicable."""

        if self.has_scale:
            return str(self.scale)
        else:
            return "NA"

    
    def get_loc_str(self):
        """Return the location parameter value as a string, if applicable."""
        if self.has_loc:
            return str(self.loc)
        else:
            return "NA"
        

    def get_shape_str(self):
        """Return shape parameter value as a string, if applicable."""
 
        if self.has_shape:
            return str(self.shape)
        else:
            return "NA"

        
    def get_coeff_of_determ_str(self):
        """Return the coefficient of determination of prob. plot as a string."""

        return str(self.r2)


    def eval_data(self):
        """Perform the prob. plotting calcs; determine distr. parameter values."""

        self._pplot_transform_data()
        self._linear_regression()
        self.extract_pplot_regress_quantities()


    def _linear_regression(self):
        """Perform a linear regression on the transformed samples/quantiles."""

        self.slope, self.intercept, r_value, pvalue, stderr = \
            stats.linregress(self.x, self.y)
        self.r2 = r_value**2.0


    def create_pplot(self, axes):
        """Draw probabaility plot of data on 'axes'"""

        liny = lambda x: self.slope * x + self.intercept
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
            % (self.slope, self.intercept, self.r2)
        axes.text(0.1*xmax + 0.9*xmin,
                 0.1*ymin + 0.9*ymax,
                 eq)
        axes.set_xlabel("t = " + self.xlabel)
        axes.set_ylabel("f(t) = " + self.ylabel)
        axes.set_title(self.label)
        axes.legend(loc=4)
        axes.grid(which='major')
        

    def calc_quantiles(self, qmethod):
        """Calculate the values of the quantiles according to 'qmethod'"""

        n = self.nsamples
        self.quantiles = \
            quantiles.Quantiles.create_subclass_instance(qmethod)().get_quantiles(n)

    def get_scipy_command(self):
        """Return the SciPy command to instantiate distr. object using results of pplotpy"""
       
        text = "myRV = scipy.stats.%s(" % self.scipy_name
        indent = ' ' * len(text)
        if self.has_shape == True:
            text += self.get_shape_str() + ',\n'
            text += indent + "loc=%s,\n" % self.get_loc_str()
        else:
            text += "loc=%s,\n" % self.get_loc_str()
        text += indent + "scale=%s)" % self.get_scale_str()
        return text


    def _calc_pdf_cdf(self, num_points=1000):
        """Populate a pdf-cdf data from scipy object."""

        # Note: do not include 1st or last points, which may correspond to 
        # +/- infinite
        self.cdf_vals = np.linspace(1.0/num_points,
                                    (num_points-1)/num_points,
                                    num_points-2)
        self.scipy_vals = self.scipy_obj.ppf(self.cdf_vals)
        self.pdf_vals = self.scipy_obj.pdf(self.scipy_vals)


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
        ax2.plot(self.samples,
                 self.quantiles,
                 'ro')
        ax2.legend(loc=1)


@SupportedDistributions.register_distribution("Normal")    
class Normal(SupportedDistributions):
    """Normal/Gaussian Probability plotting object"""

#   Information on probability plotting with normal distribution:
#   [a] NIST  - http://www.itl.nist.gov/div898/handbook/eda/section3/normprpl.htm
#   [b] SciPy - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html
#   [c] Wolfram Mathworld - http://mathworld.wolfram.com/NormalDistribution.html
    
    pdf_eq = r"$f_{X}(x) = \frac{1}{\sqrt{2\pi\sigma}}e^{-\frac{\left(x-\mu\right)^2}{2\sigma^2}}$"
    scipy_name = "norm"
    has_shape = False
    has_loc = True
    has_scale = True
    loc_optional = False
    xlabel = r"$erf^{-1}\left[2F_X(x)-1\right]$"
    ylabel = r"$x$"

        
    def _pplot_transform_data(self):
        """Transform samples/quantiles based on prob. plotting of normal distr."""

        self.x = erfinv((2.0 * self.quantiles) - 1.0)
        self.y = self.samples


    def extract_pplot_regress_quantities(self):
        """Calculate scale and location values from prob. plot slope/intercept."""

        self.scale = self.slope   # stdev
        self.loc = self.intercept # mean
        
    def _create_scipy_obj(self):
        """Instantiate a frozen scipy object for the normal distribution"""        

        from scipy.stats import norm
        self.scipy_obj = norm(loc=self.loc, scale=self.scale)
    
    
@SupportedDistributions.register_distribution("Lognormal")    
class Lognormal(SupportedDistributions):
    """Lognormal distribution probability plotting object"""

#   Information on probability plotting with lognormal distribution:
#   [a] NIST  - http://www.itl.nist.gov/div898/handbook/apr/section2/apr221.htm
#   [b] NIST  - http://www.itl.nist.gov/div898/handbook/apr/section1/apr164.htm#Formula's
#   [c] Wolfram Mathworld - http://mathworld.wolfram.com/LogNormalDistribution.html
#   [d] SciPy - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.lognorm.html
 
    scipy_name = "lognorm"
    has_shape = True
    has_loc = True  # can be specified, default 0
    has_scale = True
    loc_optional = True
    xlabel = r"$erf^{-1}\left[F_X(x-loc)\right]$"
    ylabel = r"$\ln(x-loc)$"
    

    def _pplot_transform_data(self):
        """Transf. samples/quantiles based on prob. plotting of lognormal distr."""

        self.x = erfinv(self.quantiles)
        self.y = np.log(self.samples - self.loc)


    def extract_pplot_regress_quantities(self):
        """Calculate scale and shape values from prob. plot slope/intercept."""

        self.shape = self.slope * np.log(10)
        self.scale = self.intercept # mean

    def _create_scipy_obj(self):
        """Instantiate a frozen scipy object for the lognormal distribution"""
        
        from scipy.stats import lognorm
        self.scipy_obj = lognorm(self.shape, loc=self.loc, scale=self.scale)

@SupportedDistributions.register_distribution("Exponential") 
class Exponential(SupportedDistributions):
    """Exponential distribution probability plotting object"""

#   Information on probability plotting with exponential distribution:
#   [a] NIST  - http://www.itl.nist.gov/div898/handbook/apr/section2/apr221.htm
#   [b] NIST  - http://www.itl.nist.gov/div898/handbook/eda/section3/eda3667.htm
#   [c] Wolfram Mathworld - http://mathworld.wolfram.com/ExponentialDistribution.html
#   [d] SciPy - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.expon.html
 
    scipy_name = "expon"
    has_scale = True
    has_loc = True # can be specified, default 0
    has_shape = False
    loc_optional = True
    xlabel = r"$x-loc$"
    ylabel = r"$\ln\left(\frac{1}{1-F_X(x-loc)}\right)$"
 

    def _pplot_transform_data(self):
        """Transf. samples/quantiles based on prob. plotting of exponential distr."""

        self.x = self.samples - self.loc
        self.y = np.log(1.0 / (1.0 - self.quantiles))


    def extract_pplot_regress_quantities(self):
        """Calculate scale value from prob. plot slope/intercept."""

        self.scale = 1.0 / self.slope
        
        
    def _create_scipy_obj(self):
        """Instantiate a frozen scipy object for the exponential distribution""" 
        
        from scipy.stats import expon
        self.scipy_obj = expon(loc=self.loc, scale=self.scale)

        
@SupportedDistributions.register_distribution("Weibull") 
class Weibull(SupportedDistributions):
    """Weibull distribution probability plotting object"""

#   Information on probability plotting with Weibull distribution:
#   [a] NIST  - http://www.itl.nist.gov/div898/handbook/apr/section2/apr221.htm
#   [b] NIST  - http://www.itl.nist.gov/div898/handbook/apr/section1/apr162.htm#Formula'sand
#   [c] Wolfram Mathworld - http://mathworld.wolfram.com/WeibullDistribution.html
#   [d] SciPy - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.frechet_r.html
 
    scipy_name = "frechet_r"
    has_scale = True
    has_shape = True 
    has_loc = True # can be specified, default = 0
    loc_optional = True
    xlabel = r"$\ln(x-loc)$"
    ylabel = r"$\ln\left[\ln\left(\frac{1}{1-F_X(x-loc)}\right)\right]$"
        
    def _pplot_transform_data(self):
        """Transf. samples/quantiles based on prob. plotting of Weibull distr."""

        self.x = np.log(self.samples - self.loc)
        self.y = np.log(np.log(1.0 / (1.0 - self.quantiles)))


    def extract_pplot_regress_quantities(self):
        """Calculate scale and shape values from prob. plot slope/intercept."""

        self.shape = self.slope
        self.scale = np.exp(-1.0 * self.intercept/ self.slope)

    def _create_scipy_obj(self):
        """Instantiate a frozen scipy object for the weibull distribution"""        
        
        from scipy.stats import frechet_r
        self.scipy_obj = frechet_r(self.shape, loc=self.loc, scale=self.scale)

        
@SupportedDistributions.register_distribution("Extreme Value, Type I")
class ExtremeValueTypeI(SupportedDistributions):
    """Extreme Value, Type I (EV-I) probability plotting object"""

#   Information on probability plotting with EV-I distribution:
#   [a] NIST  - http://www.itl.nist.gov/div898/handbook/apr/section2/apr221.htm
#   [b] NIST  - http://www.itl.nist.gov/div898/handbook/eda/section3/eda366g.htm
#   [c] Wolfram Mathworld - http://mathworld.wolfram.com/ExtremeValueDistribution.html
#   [d] SciPy - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gumbel_l.html
 
    scipy_name = "gumbel_l"
    has_shape = False
    has_loc = True
    has_scale = True
    loc_optional = False
    xlabel = r"$x$"
    ylabel = r"$\ln\left[-\ln\left(1-F_X(x)\right)\right]$"

    def _pplot_transform_data(self):
        """Transf. samples/quantiles based on prob. plotting of EV-I distr."""

        self.x = self.samples
        self.y = np.log(-1.0 * np.log(1.0 - self.quantiles))


    def extract_pplot_regress_quantities(self):      
        """Calculate scale and shape values from prob. plot slope/intercept."""

        self.scale = 1.0 / self.slope
        self.loc = 1.0 * self.intercept * self.slope


    def _create_scipy_obj(self):
        """Instantiate a frozen scipy object for the EV-I distribution"""        

        from scipy.stats import gumbel_l
        self.scipy_obj = gumbel_l(loc=self.loc, scale=self.scale)



@SupportedDistributions.register_distribution("Logistic")
class Logistic(SupportedDistributions):
    """Logistic probability plotting object"""

#   Information on probability plotting with Logistic distribution:
#   [a] SciPy  - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.logistic.html
#   [b] Wolfram Mathworld - http://mathworld.wolfram.com/LogisticDistribution.html
 
    name = "Logistic"
    scipy_name = "logistic"
    has_shape = False
    has_loc = True
    has_scale = True
    loc_optional = False
    xlabel = r"$\tanh^{-1}\left(2*F_X{x}-1\right)$"
    ylabel = r"$x$"


    def _pplot_transform_data(self):
        """Transf. samples/quantiles based on prob. plotting of Logistic distr."""

        self.x = np.arctanh(2.0*self.quantiles - 1)
        self.y = self.samples


    def extract_pplot_regress_quantities(self):      
        """Calculate scale and location values from prob. plot slope/intercept."""

        self.scale = 0.5 * self.slope
        self.loc = self.intercept


    def _create_scipy_obj(self):
        """Instantiate a frozen scipy object for the logistic distribution"""
        
        from scipy.stats import logistic
        self.scipy_obj = logistic(loc=self.loc, scale=self.scale)
        
        
@SupportedDistributions.register_distribution("Uniform")
class Uniform(SupportedDistributions):
    """Uniform probability plotting object"""

#   Information on probability plotting with Uniform distribution:
#   [a] NIST  - http://www.itl.nist.gov/div898/handbook/eda/section3/eda3662.htm
#   [b] Wolfram Mathworld - http://mathworld.wolfram.com/UniformDistribution.html
#   [c] SciPy - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.uniform.html
 
    scipy_name = "uniform"
    has_shape = False
    has_loc = True
    has_scale = True
    loc_optional = False
    xlabel = r"$F_X{x}$"
    ylabel = r"$x$"


    def _pplot_transform_data(self):
        """Transf. samples/quantiles based on prob. plotting of Uniform distr."""

        self.x = self.quantiles
        self.y = self.samples


    def extract_pplot_regress_quantities(self):      
        """Calculate scale and locations values from prob. plot slope/intercept."""

        self.scale = self.slope
        self.loc = self.intercept        


    def _create_scipy_obj(self):
        """Instantiate a frozen scipy object for the uniform distribution"""
        from scipy.stats import uniform
        self.scipy_obj = uniform(loc=self.loc, scale=self.scale)

@SupportedDistributions.register_distribution("Cauchy")
class Cauchy(SupportedDistributions):
    """Cauchy probability plotting object"""

#   Information on probability plotting with Uniform distribution:
#   [a] NIST  - http://www.itl.nist.gov/div898/handbook/eda/section3/eda3663.htm
#   [b] Wolfram Mathworld - http://mathworld.wolfram.com/CauchyDistribution.html
#   [c] SciPy -https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.cauchy.html
 
    scipy_name = "cauchy"
    has_shape = False
    has_loc = True
    has_scale = True
    loc_optional = False
    xlabel = r"$tan\left(\pi(F_X{x}-0.5)\right)$"
    ylabel = r"$x$"


    def _pplot_transform_data(self):
        """Transf. samples/quantiles based on prob. plotting of Cauchy distr."""

        self.x = np.tan(np.pi * (self.quantiles - 0.5))
        self.y = self.samples


    def extract_pplot_regress_quantities(self):      
        """Calculate scale and locations values from prob. plot slope/intercept."""

        self.scale = self.slope
        self.loc = self.intercept        


    def _create_scipy_obj(self):
        """Instantiate a frozen scipy object for the cauchy distribution"""
        
        from scipy.stats import cauchy
        self.scipy_obj = cauchy(loc=self.loc, scale=self.scale)

@SupportedDistributions.register_distribution("Rayleigh")
class Rayleigh(SupportedDistributions):
    """Rayleigh probability plotting object"""

#   Information on probability plotting with Uniform distribution:
#   [a] Wolfram Mathworld - http://mathworld.wolfram.com/RayleighDistribution.html
#   [b] SciPy - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rayleigh.html
 
    scipy_name = "rayleigh"
    has_shape = False
    has_loc = True
    has_scale = True
    loc_optional = True
    xlabel = r"$\sqrt{-2 \ln\left(F_X{x-loc}\right)}$"
    ylabel = r"$x-loc$"


    def _pplot_transform_data(self):
        """Transf. samples/quantiles based on prob. plotting of Rayleigh distr."""

        self.x = np.sqrt(-2.0 * np.log(1.0 - self.quantiles) )
        self.y = self.samples


    def extract_pplot_regress_quantities(self):      
        """Calculate scale and locations values from prob. plot slope/intercept."""

        self.scale = self.slope
        self.loc = self.intercept        


    def _create_scipy_obj(self):
        """Instantiate a frozen scipy object for the rayleigh distribution"""
        
        from scipy.stats import rayleigh
        self.scipy_obj = rayleigh(loc=self.loc, scale=self.scale)
