"""
A Direct Search Strategy for optimizing GP hyperparameters
"""
import scipydirect 
import scipy.optimize as so
from GPy.inference.optimization import Optimizer
import GPy
import numpy as np
import matplotlib.pyplot as plt

class DirectOpt(Optimizer):
    """Combined global and local optimization"""
    def __init__(self, bounds, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bounds = bounds
        
    def opt(self, x_init, f_fp=None, f=None, fp=None):
        
        #Global optimization
        res1 = scipydirect.minimize(f, self.bounds)
        
        #Local gradient optimization
        res2 = so.minimize(f, res1.x)
        
        self.x_opt = res2.x
        
        
def plot_3d(f, m):
    """Plot model and objective function in 3d"""
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    gridX, gridY = np.meshgrid(np.arange(-2, 2, 0.1), np.arange(-1, 1, 0.1))
    Z = np.zeros_like(gridX)
    Zpredict = np.zeros_like(gridX)
    flattened = np.array([gridX.flatten(), gridY.flatten()]).T
    values = f(flattened)
    mean, var = m.predict(flattened)
    for i in range(values.shape[0]):
        Z.ravel()[i] = values[i, 0]
        Zpredict.ravel()[i] = mean[i]
    
    ax.plot_wireframe(gridX, gridY, Z, rstride=1, cstride=1, label='Data')
    ax.plot_wireframe(gridX, gridY, Zpredict, rstride=2, cstride=2, color='y', label='Model')
    ax.legend()
    
def loo_error(x, y, optimizer=None, kernel=None):
    """Calculate the the leave-one-out cross-validation errror"""
    n = x.shape[0]
    sq_errors = np.zeros(n)
    kern = kernel if kernel else GPy.kern.RBF(input_dim=x.shape[1], ARD=True) 
    for i, point in enumerate(x):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        m = GPy.models.GPRegression(x[mask, :], y[mask, :], kernel=kernel)
        if optimizer:
            m.optimize(optimizer)
        else:
            m.optimize()
        pred, _ = m.predict(np.atleast_2d(x[i, :]))
        sq_errors[i] = (pred-y[i, :])**2
    range_y = np.max(y) - np.min(y)
    avg_err = np.sqrt(1/n*np.sum(sq_errors))/range_y
    return avg_err