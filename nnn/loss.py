import numpy as np
from nnn.activation import Softmax


# Base class for loss functions
class Loss:

    # Calculates loss given model output and target/ground truth
    def calculate(self, y_pred : np.array, y_true : np.array):

        # Calculate sample losses
        sample_losses = self.forward(y_pred, y_true)

        # Calculate mean loss
        loss = np.mean(sample_losses)

        # Return mean loss
        return loss


# Categorial cross-entropy loss
class CategoricalCrossEntropy(Loss):

    # Forward pass
    def forward(self, y_pred : np.array, y_true : np.array):

        # Get the number of samples in this batch
        num_samples = len(y_pred)

        # Clip to prevent exploding numbers
        pred_clipped = np.clip(y_pred, 1e-7, 1-1e-7)

        # If y_true is provided as target values
        if len(y_true.shape) == 1:
            loss = -np.log(
                pred_clipped[
                    range(num_samples),
                    y_true
                ]
            )
        # If y_true is provided as distributions
        else:
            loss = -np.sum(
                np.log(pred_clipped) * y_true,
                axis=1
            )
        
        # Return the calculated loss
        return loss

    # Backpropagation
    def backward(self, y_pred : np.array, y_true : np.array):
        # Number of samples
        samples = len(y_pred)
        # Number of labels in every sample
        labels = len(y_pred[0])

        # If labels are sparse, convert to one-hot vector form
        if len(y_true.shape) == 1:
            y_true = np.eye(labels)[y_true]

        # Calculate gradient
        self.dinputs = -y_true / y_pred
        # Normalise gradient
        self.dinputs = self.dinputs / samples


# Softmax activation combined with categorical cross-entropy
class SoftmaxWithCategoricalCrossentropy:

    # Constructor
    def __init__(self):
        # Creates activation and loss function objects
        self.softmax = Softmax()
        self.categoricalcrossentropy = CategoricalCrossEntropy()

    # Forward pass
    def forward(self, inputs : np.array, y_true : np.array):
        # Pass inputs through activation and set self.outputs variable
        self.outputs = self.softmax.forward(inputs)
        # Return the loss value
        return self.categoricalcrossentropy.calculate(self.outputs, y_true)

    # Backpropagation
    def backward(self, y_pred : np.array, y_true : np.array):
        
        # Number of samples
        samples = len(y_pred)

        # If labels are one-hot encoded, convert to spare form
        if len(y_true.shape) == 2:
            y_true = np.argmax(y_true, axis=1)

        # Copy the y_pred so we can modify
        self.dinputs = y_pred.copy()

        # Calculate gradient
        self.dinputs[range(samples), y_true] -= 1

        # Normalise gradient
        self.dinputs = self.dinputs / samples
