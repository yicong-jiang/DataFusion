from tool/util import *

class LognormalRidge:
    def __init__(self, alpha = 0.05):
        self.alpha = alpha
        self.ridgereg = RidgeCV(alphas = 0.05)
        
    def fit(self, X, y):
        self.ridgefit = self.ridgereg.fit(X, np.log(y))
        self.coef_ = self.ridgefit.coef_
        self.var = np.mean((np.log(y) - self.ridgefit.predict(X)) ** 2)
        return self
        
        
    def predict(self, X):
        ridge_pred = self.ridgefit.predict(X)
        return np.exp(ridge_pred + 0.5 * self.var)

    def predict_var(self, X):
        ridge_pred = self.ridgefit.predict(X)
        return np.exp(2 * ridge_pred + 2 * self.var) - np.exp(2 * ridge_pred + self.var)

class LognormalRidge_var:
    def __init__(self, alpha = 0.05):
        self.alpha = alpha
        self.ridgereg = RidgeCV(alphas = 0.05)
        
    def fit(self, X, y):
        self.ridgefit = self.ridgereg.fit(X, np.log(y))
        self.coef_ = self.ridgefit.coef_
        self.var = np.mean((np.log(y) - self.ridgefit.predict(X)) ** 2)
        return self

    def predict(self, X):
        ridge_pred = self.ridgefit.predict(X)
        return np.sqrt(np.exp(2 * ridge_pred + 2 * self.var) - np.exp(2 * ridge_pred + self.var))
