###############################################################################
#
#    gamut
#    Copyright (C) 2017,  Nicholas A. Reynolds
#
#    Full License Available in LICENSE file at
#    https://github.com/nicholasareynolds/gamut
#
###############################################################################


from scipy.stats import t
import numpy as np

class GeneralizedExtremeStudentizedDeviate:
    """
    Analyze/remove outliers from samples according to the Generalized ESD Test.
    
    Usage:
        genESD_object = \
            GeneralizedExtremeStudentizedDeviate(data,
                                                 significance_level=0.05)
        data_no_outliers = genESD_object.get_remaining_samples()
        
    The generalized extreme Studentized deviate is essentially the Grubbs test,
    or maximum normed residual test, applied sequentially.  This object accepts
    a sample set of size N, along with a significance level (2-sided.).
    It iteratively removes outliers and computes the test statistics and 
    critical values of the reduced sample set; this continues until the test
    statistics fall below the critcal value of the t distribution for that 
    sample size.
    
    The Generalized ESD test detects for outliers of a univariate data set that
    follows an approximately normal distribution.
    
    References:
        [1]   "Generalized ESD Test for Outliers", Engineer Statistics Handbook,
              NIST.  Date Accessed: September 23, 2017.
              http://www.itl.nist.gov/div898/handbook/eda/section3/eda35h3.htm
        [2]   Rosner, Bernard (May 1983), "Percentage Points for a Generalized
              ESD Many-Outlier Procedure", Technometrics, 25(2), pp. 165-172.
        [3]   "Grubbs' Test for Outliers", Engineer Statistics Handbook,
              NIST.  Date Accessed: September 23, 2017.
              http://www.itl.nist.gov/div898/handbook/eda/section3/eda35h1.htm
        [4]   Grubbs, Frank (February 1969), Procedures for Detecting Outlying 
              Observations in Samples, Technometrics, 11(1), pp. 1-21.
    """
    
    def __init__(self,
                 samples,
                 significance_level=0.05):
        
        # Initialize
        self.outliers = list()
        
        # Set inputs as attributes
        self.samples = np.sort(samples)
        self.N = np.size(samples)
        self.significance_level= significance_level
        
        # Get to business
        self._compute_outliers()

    def _compute_outliers(self):
        """
        Remove outliers according to the Generalized extreme Studentized
        deviate test; store outliers, and remaining samples as attributes.
        
        Reference:
        Generalized extreme Studentized deviate test
        http://www.itl.nist.gov/div898/handbook/eda/section3/eda35h3.htm
        """

        # maximum normed residuals (MNR) statistic (for descreasing data set)
        max_norm_residuals = np.zeros(self.N)
        
        # True table for (MNR > critical value), initialized
        statistic_exceeds_crit = np.zeros(self.N, dtype=int)
        
        # maximum normed residuals (for descreasing data set)
        max_norm_residuals = np.zeros(self.N)

        for ii, ((sample, R), lamb) \
            in enumerate(zip(self._compute_all_test_statistics(),
                             self._compute_critical_values())):
            max_norm_residuals[ii] = sample
            if R > lamb:
                statistic_exceeds_crit[ii] = 1
        self.num_outliers = np.nonzero(statistic_exceeds_crit)[0][-1] + 1
        self.outliers = max_norm_residuals[:self.num_outliers]
        mask = [1 if sample in self.outliers else 0 for sample in self.samples]
        self.remainders = np.delete(self.samples,np.nonzero(mask)[0])
        
    def _compute_all_test_statistics(self):
        """
        Yield the maximum normed residuals for samples as outliers are removed
        """
        samples = self.samples
        n = self.N
        while n > 1:
            mean = np.mean(samples)
            std = np.std(samples, ddof=1)
            nr_minval = np.abs(samples[0]-mean)/std
            nr_maxval = np.abs(samples[-1]-mean)/std
            if nr_minval > nr_maxval:
                yield samples[0], nr_minval
                samples = samples[1:]
            else:
                yield samples[-1], nr_maxval
                samples = samples[:-1]
            n -= 1

    def _compute_critical_values(self):
        """
        Yield the critical t-values based on samples sizes N to 1. 
        """
        
        N = self.N
        i = 1
        while N-2 > i:
            q = 1.0 - self.significance_level/(2.0*(N-i+1))  # quantile
            v = N - i - 1
            tval = t.ppf(q, df=v)
            
            # Critical Value
            lamb = (N-i) * tval / np.sqrt((N-i-1.0 + tval**2.0)*(N-i+1.0))
            yield lamb
            
            # Update for next iteration
            i += 1
            

    def get_num_outliers(self):
        """
        Return the number of outliers in the data set
        """
        return self.num_outliers
    
    def get_outliers(self):
        """
        Return a list of outliers from the data set
        """
        return self.outliers
    
    def get_remainders(self):
        """
        Return the data set with outliers removed
        """
        return self.remainders
         

# UNIT TEST
#    (from http://www.itl.nist.gov/div898/handbook/eda/section3/eda35h3.htm)
if __name__ == "__main__":
    data = [-0.25, 0.68, 0.94, 1.15, 1.20, 1.26, 1.26,
             1.34, 1.38, 1.43, 1.49, 1.49, 1.55, 1.56,
             1.58, 1.65, 1.69, 1.70, 1.76, 1.77, 1.81,
             1.91, 1.94, 1.96, 1.99, 2.06, 2.09, 2.10,
             2.14, 2.15, 2.23, 2.24, 2.26, 2.35, 2.37,
             2.40, 2.47, 2.54, 2.62, 2.64, 2.90, 2.92,
             2.92, 2.93, 3.21, 3.26, 3.30, 3.59, 3.68,
             4.30, 4.64, 5.34, 5.42, 6.01]
                                                        # Should be
    print(len(data))                                    # 54
    test = GeneralizedExtremeStudentizedDeviate(data)   
    print(test.get_num_outliers())                      # 3
    print(test.get_outliers())                          # 6.01  5.42  5.34
    print(test.get_remainders())                        # -0.25 ... 4.64                       
    print(len(test.remainders))                         # 51
    print(len(data))                                    # 54
