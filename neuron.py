import numpy as np


class perceptron:
    def __init__(self, nbr_parametre, func_activation='signoide'):
        self.nbr_parametre = nbr_parametre
        self.weights = np.random.randn(nbr_parametre + 1, 1) 

        self.formule = self.choose_activation(func_activation)

    def __str__(self):
        return str(self.weights)
    
    def pre_activation(self, input_data : np.ndarray):
        return np.dot(input_data, self.weights[:self.nbr_parametre]) + self.weights[self.nbr_parametre]

    def activation(self, z):
        # retourne 0 ou 1 ainsi que la probabilité
        return self.formule(z)
    
    @staticmethod
    def choose_activation(formule):
        if formule == 'signoide':
            return lambda z: 1 / (1 + np.exp(-np.clip(z, -500, 500)))
        if formule == 'tanh':
            return lambda z: (1 - np.exp(-2*z)) / (1 + np.exp(-2*z))
        if formule == 'ReLU':
            return lambda z: max(0, z)
        if formule == 'marche':
            return lambda z: 0 if z < 0 else 1
        if formule == "Leaky ReLU":
            return lambda z: max(0.01*z, z)
        if formule == 'SoftPlus':
            return lambda z: np.log(1 + np.exp(z))


    def update_waights(self, *args):
        pass

class perceptron_mutation(perceptron):
    def __init__(self, weights):
        super().__init__(weights)


    def update_waights(self, new_weight):
        prob_mutation = 0.6
        max_mutation = 0.3
        self.weights = new_weight.copy()
        self.weights += np.where(np.random.rand(len(new_weight), 1) < prob_mutation, np.random.uniform(-max_mutation, max_mutation, (len(new_weight), 1)), 0)