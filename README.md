# *gamut*
*gamut* is a GUI tool that helps users determine fit a distribution to their univariate datasets, leveraging the full gamut of continuous distributions in [SciPy's statistics toolbox](https://docs.scipy.org/doc/scipy/reference/stats.html).  *gamut* accepts a user-supplied set of samples (optionally removing outliers).  The user specifies candidate continuous distributions, for which [probability plot](http://www.itl.nist.gov/div898/handbook/eda/section3/probplot.htm) regression are performed to identify an ideal distribution with which to model the random variable.  Lastly, *gamut* calculates the optimally computes the values of a distribution's parameters for the given data using a [maximum likelihood estimate](http://www.itl.nist.gov/div898/handbook/apr/section4/apr412.htm).  Lastly, the syntax for initiating a [SciPy frozen instance](https://docs.scipy.org/doc/scipy/reference/tutorial/stats.html#freezing-a-distribution) of the chosen  distrubtion.

## Introduction

### Background

[Probability plotting](http://www.itl.nist.gov/div898/handbook/eda/section3/probplot.htm) is a powerful method for quantifying goodness-of-fit with several advantages over other goodness-of-fit tests.  Unlike with the [Chi-Square goodness-of-fit test](http://www.itl.nist.gov/div898/handbook/eda/section3/eda35f.htm), probability plotting does not require that the samples be grouped into bins, whose size may impact the goodness-of-fit.  Unlike with [Kolmogerov-Smirnov goodness-of-fit test](http://www.itl.nist.gov/div898/handbook/eda/section3/eda35g.htm), wherein the values of a candidate distribution's parameter must be known a priori, the samples can be used to estimate the values of those parameters in probability plotting.  Lastly, unlike with [Anderson-Darling goodness-of-fit test](http://www.itl.nist.gov/div898/handbook/eda/section3/eda35e.htm), probability plotting does not depend on pre-tabulated values specific to each distribution and significance level.  

Instead, probability plotting relies on the cumulative distribution function (CDF) of a distribution, with quantile values computed from the sample's order being used as the CDF values.  The ordered samples are plotted against the ordered statistic medians, which are calculated from the quantile estimate pairs of values are transformed through the sample algebraic operations necessary to transform the CDF equation into a linear equation.  The values are the distribution parameters are then estimated through a simple linear regression.


## Getting Started

### Prerequisities:

In order to use *gamut*, the Python 3 interpreter is needed.  This can be installed directly from python.org, or more conveniently, as part of a bundled package (e.g. [Enthought Canopy](https://www.enthought.com/product/canopy/), [Anaconda](https://www.anaconda.com/download/), etc...)  Furthermore, several supporting libraries are required:

- [SciPy](https://www.scipy.org/)

- [NumPy](http://www.numpy.org/)

- [matplotlib](https://matplotlib.org/)

- [PyQT5](https://pypi.python.org/pypi/PyQt5)

### Setting up *gamut*

From the [*gamut* GitHub repository](https://github.com/nicholasareynolds/gamut/) either Clone or download the repository.

Add the destination directory path (destpath) to the PYTHONPATH:

For Unix Systems:

```
export PYTHON=$PYTHONPATH:destpath
```

For Windows systems, add the directory using the set command.
```
set PYTHONPATH=%PYTHONPATH%;destpath
```

### Usage

From the command line, enter the command

```
python gamut.py
```

## Basic Workflow

A user provides a set of samples to *gamut* and selects which distributions he/she would like considered as candidate distributions for modeling the data.  *gamut* performs a probability plot linear regression of the data, and includes a coefficient of determination (R^2) to .  

### Importing Samples

A user import his/her data set by clicking on the *Select File* button in the *gamut* window, followed by navigating to the file location.  The data must be organized in a comma-separated values (.csv) format.  Samples can be listed on one or more rows and in one or more columns in the file; *gamut* will flatten all values into an array.

### Removal of Outliers
*gamut* optionally removes outliers using the [generalized extreme Studentized deviate (ESD) test](http://www.itl.nist.gov/div898/handbook/eda/section3/eda35h3.htm) (an iterative version of the Grubb's, or maximum normed residual, test).  In order to remove outliers, a user clicks on the *Outliers Settings* button, and checks the *Remove Outliers* checkbox.  He/she is then prompted to enter the significance level to be used in detecting and eliminating the outliers from the data set.  As a note, generalized ESD test is a two-sided test assumes the data can be approximated by the normal distribution.

Changing the outlier settings after candidate distributions have already been selected will result in the the probability plot and MLE fit calculations being re-performed for all of them.

### Identifying the (Probability Plotting)
A user selects distributions in the *SciPy Distributions* portion of the window to be candidate distribution. *gamut* supports all the continuous distributions in [SciPy](https://docs.scipy.org/doc/scipy/reference/stats.html). Every distribution has an associated scale factor and location factor; however, the number of shape factors varies from distribution to distribution.  *gamut* will enable shape factor entry boxes for each of the shape factors corresponding to the highlighted distribuiton; the user is responsible for filling in these values.  

Note: for distributions with only one shape factor (e.g. [lognorm](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.lognorm.html#scipy.stats.lognorm) or [frechet_r (i.e. weibull)](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.frechet_r.html#scipy.stats.frechet_r)), user's have the option of specifying the bounds of the shape factor by clicking on the *Calculate PPCC* button.  The optimal shape factor will then be calculateded using the [scipy.stats.ppcc_max]( https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ppcc_max.html) function, which performs an analysis with a probability plot correlation coefficient on a given data set.

A user adds a selected candidate distribution to the list of considered distributions by either double-clicking the distribution (if all the shape factors are entered), or by clicking the *Add* distribution.  This will add a row in the *Probability Plotting* section of the window.  Similarly, one or all of the distributions can be removed from this section by clicking on its entry in the *Probability Plotting* section and clicking *Remove* or *Removal All*, respectively.

In the *Probability Plotting* section of the window, the values computed from the probability plot linear regression are displayed.  *gamut* employs the probability plotting function [scipy.stats.probplot](https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.stats.probplot.html)  to perform the linear regression.  This method employ's Filliben's estimate [1] of order statistic medians (i.e. quantiles). The values computed from this function include the R^2 value, the scale factor, and the location factor.  The shape factors correspond to values entered by the user.  The closer the R^2 value is to 1.00, the more reasonable that distribution is in modeling the data set.  To see the probability plot (ordered samples vs. ordered statistical medians) of a distribution, double click on the that distribution's entry in the table.  The user can optionally save this probability plot as a portable network graphics (PNG) image.  

### Fitting the Data (Maximum Likelihood Estimate)

Lastly, the shape, location, and scale parameters are calculated using a [maximum likelihood estimate (MLE)](http://www.itl.nist.gov/div898/handbook/apr/section4/apr412.htm), as implemented by the [fit method](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rv_continuous.fit.html) of the continuous distributions in SciPy.  These values are what are used in displaying the probability density function (PDF) and cumulitive density function (CDF) when clicking the *PDF/CDF* button and in the syntax to instantiate a frozen distribution in SciPy by clicking on the *SciPy Call* button.


## Administrative

### License

*gamut* is licensed under the MIT License - see the [LICENSE file](https://github.com/nicholasareynolds/gamut/LICENSE.md).

### Citing/acknowledgement

As a courtesy, please acknowledge *gamut* in papers, reports, or publications, for which *gamut* was used.

### Contributions

*gamut* is by no means a completed project, or limited to contributions by the author.  If you wish to suggest changes (or even collaborate) please contact me at ([nicholas.a.reynolds@gmail.com](mailto:nicholas.a.reynolds@gmail.com)).

## Acknowledgements
*gamut* has not implemented any new scientific concepts; it has merely a methomethodology, that I learned in grad school and is openly available, in what I consider to be a convenient workflow to scientists/engineers who are not regularly involved in uncertainty quantification.

That said, [NIST's Engineering Statistics Handbook](http://www.itl.nist.gov/div898/handbook/index.htm) was an excellent resource in preparing *gamut*.  The infrastructure laid out by Travis Oliphant and the SciPy Developers in SciPy's statistics toolbox made this tool a very straightfoward endeavor.   

## References
- [1] Filliben, J. J. (February 1975), The Probability Plot Correlation Coefficient Test for Normality, Technometrics, pp. 111-117.
