import torch
import numpy as np
from .model import DynamicsModel
from ..utils.nn import ModelDataHandler
import hydra

class LinearModel(DynamicsModel):
    def __init__(self, datahandler, solver=None):
        """
        Model for a simple linear prediction of the change in state. Consider the following optimization problem:
            (s_t+1 - s_t) = As_t + Bu_t
        - hopefully this will be configurable with different linear solvers beyond least squares.
        - For instance, least squares is only looking to model the residual on the state error, but something like total
            least squares would assume there is noise at the measured state / action too
        - Or something like logistic regression which is less aggressive to outliers (which we definitely have)
        """
        super(LinearModel, self).__init__()
        self.data_handler = hydra.utils.instantiate(datahandler) #ModelDataHandler(cfg)
        self.w = None
        self.solver = solver
        self.ensemble = False # TODO try ensembling these

    def forward(self, x):
        if self.w is None:
            raise ValueError("Model Not Trained Yet, call model.train_cust(dataset, cfg)")
        raise NotImplementedError("Subclass must implement this function")

    def reset(self):
        print("Linear model does not need to reset")
        return

    def preprocess(self, dataset):
        inputs, outputs = self.data_handler.preprocess(dataset)
        return inputs, outputs

    def postprocess(self, dX):
        dX = self.data_handler.postprocess(dX)
        return dX

    def train_cust(self, dataset, train_params):
        X = dataset[0]
        U = dataset[1]
        dX = dataset[2]

        A = np.hstacK((X,U))
        b = dX
        # Generate the weights of the least squares problem
        w = np.linalg.lstsq(A, b)
        self.w = w
        raise NotImplementedError("Subclass must implement this function")

    def predict(self, X, U):
        normX, normU = self.data_handler.forward(X, U)
        val = np.concatenate((normX, normU), axis=1)
        y = self.forward(val)
        return self.data_handler.postprocess(y)