from DeepLearning.CourseFive.rnn_utils import *

# Building your Recurrent Neural Network - Step by Step


#  RNN cell forward
def rnn_cell_forward(xt, a_prev, parameters):
    """
    Arguments:
    xt -- your input data at timestep "t", numpy array of shape (n_x, m).
    a_prev -- Hidden state at timestep "t-1", numpy array of shape (n_a, m)
    parameters -- python dictionary containing:
                  Wax -- Weight matrix multiplying the input, numpy array of shape (n_a, n_x)
                  Waa -- Weight matrix multiplying the hidden state, numpy array of shape (n_a, n_a)
                  Wya -- Weight matrix relating the hidden-state to the output, numpy array of shape (n_y, n_a)
                  ba --  Bias, numpy array of shape (n_a, 1)
                  by -- Bias relating the hidden-state to the output, numpy array of shape (n_y, 1)
    Returns:
    a_next -- next hidden state, of shape (n_a, m)
    yt_pred -- prediction at timestep "t", numpy array of shape (n_y, m)
    cache -- tuple of values needed for the backward pass, contains (a_next, a_prev, xt, parameters)
    """
    Wax = parameters["Wax"]
    Waa = parameters["Waa"]
    Wya = parameters["Wya"]
    ba = parameters["ba"]
    by = parameters["by"]

    a_next = np.tanh(np.dot(Waa, a_prev) + np.dot(Wax, xt) + ba)
    yt_pred = softmax(np.dot(Wya, a_next) + by)
    cache = (a_next, a_prev, xt, parameters)

    return a_next, yt_pred, cache


#  RNN forward
def rnn_forward(x, a0, parameters):
    """
    Arguments:
    x -- Input data for every time-step, of shape (n_x, m, T_x).
    a0 -- Initial hidden state, of shape (n_a, m)
    parameters -- python dictionary containing:
                  Waa -- Weight matrix multiplying the hidden state, numpy array of shape (n_a, n_a)
                  Wax -- Weight matrix multiplying the input, numpy array of shape (n_a, n_x)
                  Wya -- Weight matrix relating the hidden-state to the output, numpy array of shape (n_y, n_a)
                  ba --  Bias numpy array of shape (n_a, 1)
                  by -- Bias relating the hidden-state to the output, numpy array of shape (n_y, 1)
    Returns:
    a -- Hidden states for every time-step, numpy array of shape (n_a, m, T_x)
    y_pred -- Predictions for every time-step, numpy array of shape (n_y, m, T_x)
    caches -- tuple of values needed for the backward pass, contains (list of caches, x)
    """
    caches = []  # Initialize "caches" which will contain the list of all caches
    n_x, m, T_x = x.shape
    n_y, n_a = parameters["Wya"].shape

    a = np.zeros((n_a, m, T_x))
    y_pred = np.zeros((n_y, m, T_x))
    a_next = a0

    for t in range(T_x):
        #  Update next hidden state, compute the prediction, get the cache
        a_next, yt_pred, cache = rnn_cell_forward(x[:, :, t], a_next, parameters)
        #  Save the value of the new "next" hidden state in a
        a[:, :, t] = a_next
        #  Save the value of the prediction in y
        y_pred[:, :, t] = yt_pred
        #  Append "cache" to "caches"
        caches.append(cache)
    caches = (caches, x)

    return a, y_pred, caches


#  LSTM cell forward
def lstm_cell_forward(xt, a_prev, c_prev, parameters):
    """
    Arguments:
    xt -- your input data at timestep "t", numpy array of shape (n_x, m).
    a_prev -- Hidden state at timestep "t-1", numpy array of shape (n_a, m)
    c_prev -- Memory state at timestep "t-1", numpy array of shape (n_a, m)
    parameters -- python dictionary containing:
                  Wf -- Weight matrix of the forget gate, numpy array of shape (n_a, n_a + n_x)
                  bf -- Bias of the forget gate, numpy array of shape (n_a, 1)
                  Wi -- Weight matrix of the save gate, numpy array of shape (n_a, n_a + n_x)
                  bi -- Bias of the save gate, numpy array of shape (n_a, 1)
                  Wc -- Weight matrix of the first "tanh", numpy array of shape (n_a, n_a + n_x)
                  bc --  Bias of the first "tanh", numpy array of shape (n_a, 1)
                  Wo -- Weight matrix of the focus gate, numpy array of shape (n_a, n_a + n_x)
                  bo --  Bias of the focus gate, numpy array of shape (n_a, 1)
                  Wy -- Weight matrix relating the hidden-state to the output, numpy array of shape (n_y, n_a)
                  by -- Bias relating the hidden-state to the output, numpy array of shape (n_y, 1)
    Returns:
    a_next -- next hidden state, of shape (n_a, m)
    c_next -- next memory state, of shape (n_a, m)
    yt_pred -- prediction at timestep "t", numpy array of shape (n_y, m)
    cache -- tuple of values needed for the backward pass, contains (a_next, c_next, a_prev, c_prev, xt, parameters)

    Note: ft/it/ot stand for the forget/update/output gates, cct stands for the candidate value (c tilda),
          c stands for the memory value
    """
    Wf = parameters["Wf"]
    bf = parameters["bf"]
    Wi = parameters["Wi"]
    bi = parameters["bi"]
    Wc = parameters["Wc"]
    bc = parameters["bc"]
    Wo = parameters["Wo"]
    bo = parameters["bo"]
    Wy = parameters["Wy"]
    by = parameters["by"]

    n_x, m = xt.shape
    n_y, n_a = Wy.shape

    concat = np.zeros((n_a + n_x, m))
    concat[: n_a, :] = a_prev
    concat[n_a:, :] = xt

    ft = sigmoid(np.dot(Wf, concat) + bf)  # forget gates
    it = sigmoid(np.dot(Wi, concat) + bi)  # update gates
    cct = np.tanh(np.dot(Wc, concat) + bc)  # candidate value(c tilda)
    c_next = np.multiply(ft, c_prev) + np.multiply(it, cct)
    ot = sigmoid(np.dot(Wo, concat) + bo)  # output gates
    a_next = np.multiply(ot, np.tanh(c_next))  # memory value

    yt_pred = softmax(np.dot(Wy, a_next) + by)
    cache = (a_next, c_next, a_prev, c_prev, ft, it, cct, ot, xt, parameters)

    return a_next, c_next, yt_pred, cache


#  LSTM forward
def lstm_forward(x, a0, parameters):
    """
    Arguments:
    x -- Input data for every time-step, of shape (n_x, m, T_x).
    a0 -- Initial hidden state, of shape (n_a, m)
    parameters -- python dictionary containing:
                  Wf -- Weight matrix of the forget gate, numpy array of shape (n_a, n_a + n_x)
                  bf -- Bias of the forget gate, numpy array of shape (n_a, 1)
                  Wi -- Weight matrix of the save gate, numpy array of shape (n_a, n_a + n_x)
                  bi -- Bias of the save gate, numpy array of shape (n_a, 1)
                  Wc -- Weight matrix of the first "tanh", numpy array of shape (n_a, n_a + n_x)
                  bc -- Bias of the first "tanh", numpy array of shape (n_a, 1)
                  Wo -- Weight matrix of the focus gate, numpy array of shape (n_a, n_a + n_x)
                  bo -- Bias of the focus gate, numpy array of shape (n_a, 1)
                  Wy -- Weight matrix relating the hidden-state to the output, numpy array of shape (n_y, n_a)
                  by -- Bias relating the hidden-state to the output, numpy array of shape (n_y, 1)
    Returns:
    a -- Hidden states for every time-step, numpy array of shape (n_a, m, T_x)
    y -- Predictions for every time-step, numpy array of shape (n_y, m, T_x)
    caches -- tuple of values needed for the backward pass, contains (list of all the caches, x)
    """
    caches = []
    n_x, m, T_x = x.shape
    n_y, n_a = parameters["Wy"].shape

    a = np.zeros((n_a, m, T_x))
    c = np.zeros((n_a, m, T_x))
    y = np.zeros((n_y, m, T_x))
    a_next = a0
    c_next = np.zeros((n_a, m))

    for t in range(T_x):
        # Update next hidden state, next memory state, compute the prediction, get the cache
        a_next, c_next, yt, cache = lstm_cell_forward(x[:, :, t], a_next, c_next, parameters)
        # Save the value of the new "next" hidden state in a
        a[:, :, t] = a_next
        # Save the value of the prediction in y
        y[:, :, t] = yt
        # Save the value of the next cell state
        c[:, :, t] = c_next
        # Append the cache into caches
        caches.append(cache)
    caches = (caches, x)

    return a, y, c, caches


# RNN cell backward
def rnn_cell_backward(da_next, cache):
    """
    Arguments:
    da_next -- Gradient of loss with respect to next hidden state
    cache -- python dictionary containing useful values (output of rnn_step_forward())
    Returns:
    gradients -- python dictionary containing:
                 dx -- Gradients of input data, of shape (n_x, m)
                 da_prev -- Gradients of previous hidden state, of shape (n_a, m)
                 dWax -- Gradients of input-to-hidden weights, of shape (n_a, n_x)
                 dWaa -- Gradients of hidden-to-hidden weights, of shape (n_a, n_a)
                 dba -- Gradients of bias vector, of shape (n_a, 1)
    """
    (a_next, a_prev, xt, parameters) = cache

    Wax = parameters["Wax"]
    Waa = parameters["Waa"]
    Wya = parameters["Wya"]
    ba = parameters["ba"]
    by = parameters["by"]

    # compute the gradient of tanh with respect to a_next
    dtanh = (1 - a_next ** 2) * da_next
    # compute the gradient of the loss with respect to Wax
    dxt = np.dot(Wax.T, dtanh)
    dWax = np.dot(dtanh, xt.T)
    # compute the gradient with respect to Waa
    da_prev = np.dot(Waa.T, dtanh)
    dWaa = np.dot(dtanh, a_prev.T)
    # compute the gradient with respect to b
    dba = np.sum(dtanh, axis=1, keepdims=True)

    gradients = {"dxt": dxt, "da_prev": da_prev, "dWax": dWax, "dWaa": dWaa, "dba": dba}
    return gradients


# RNN backward
def rnn_backward(da, caches):
    """
    Arguments:
    da -- Upstream gradients of all hidden states, of shape (n_a, m, T_x)
    caches -- tuple containing information from the forward pass (rnn_forward)
    Returns:
    gradients -- python dictionary containing:
        dx -- Gradient w.r.t. the input data, numpy-array of shape (n_x, m, T_x)
        da0 -- Gradient w.r.t the initial hidden state, numpy-array of shape (n_a, m)
        dWax -- Gradient w.r.t the input's weight matrix, numpy-array of shape (n_a, n_x)
        dWaa -- Gradient w.r.t the hidden state's weight matrix, numpy-arrayof shape (n_a, n_a)
        dba -- Gradient w.r.t the bias, of shape (n_a, 1)
    """
    (caches, x) = caches
    (a1, a0, x1, parameters) = caches[0]

    n_a, m, T_x = da.shape
    n_x, m = x1.shape

    dx = np.zeros((n_x, m, T_x))
    dWax = np.zeros((n_a, n_x))
    dWaa = np.zeros((n_a, n_a))
    dba = np.zeros((n_a, 1))
    da0 = np.zeros((n_a, m))
    da_prevt = np.zeros((n_a, m))

    for t in reversed(range(T_x)):
        # Compute gradients at time step t. Choose wisely the "da_next" and
        # the "cache" to use in the backward propagation step.
        gradients = rnn_cell_backward(da[:, :, t] + da_prevt, caches[t])
        # Retrieve derivatives from gradients
        dxt, da_prevt, dWaxt, dWaat, dbat = gradients["dxt"], gradients["da_prev"], \
                                            gradients["dWax"], gradients["dWaa"], gradients["dba"]
        # Increment global derivatives w.r.t parameters by adding their derivative at time-step t
        dx[:, :, t] = dxt
        dWax += dWaxt
        dWaa += dWaat
        dba += dbat
    da0 = da_prevt
    gradients = {"dx": dx, "da0": da0, "dWax": dWax, "dWaa": dWaa, "dba": dba}

    return gradients

