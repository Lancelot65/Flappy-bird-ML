import numpy as np

class Layer:
    def __init__(self, input_len : int, nbr_noyau : int) -> None:
        self.weights = np.random.randn(input_len + 1, nbr_noyau)
    
    def calcul(self, input : np.ndarray) -> np.ndarray:
        return self.activation(input.dot(self.weights[:-1]) + self.weights[-1])
    
    def activation(self, z):
        return 1 / (1 + np.exp(-z))

class reseau_de_neuronne:
    def __init__(self, layer : list): # [6, 6, 2] # [nombre de input, nbr_neuronne, nbr_neuron, ..., nbr_sortie]
        self.hidden_layer = [Layer(layer[i - 1], layer[i]) for i in range(1, len(layer))]

    def calcul(self, input : np.ndarray):
        for layer in self.hidden_layer:
            input = layer.calcul(input)
        return input