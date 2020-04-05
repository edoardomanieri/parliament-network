import numpy as np
from scipy.special import betaln


def beta_bernoulli(X, a=1, b=1, A=6,  T=100):

    # initialization
    N = X.shape[0]                                                                          # number of nodes in the network
    z = np.ones((N, 1))
    Z = []
    np.fill_diagonal(X, 0)
    eps = 1e-200

    for _ in range(T):
        for n in range(N):                                                                  # component of each node (at the beginning all nodes belong to the same component)
            nn = [x for x in range(N) if x != n]                                            # indices considered
            K = z.shape[1]                                                                  # number of components
            m = sum(z[nn, :])[:, np.newaxis]                                                # number of nodes for each components
            M = np.tile(m, (1, K))

            # X[nn, nn] in matlab is X_nn_nn
            X_nn_nn = np.delete(X, n, 0)
            X_nn_nn = np.delete(X_nn_nn, n, 1)
            M1 = z[nn, :].T@X_nn_nn@z[nn, :] - np.diag(sum(X_nn_nn@z[nn, :]*z[nn, :])/2)    # number of links between components
            M0 = m@m.T - np.diag((m*(m+1)).ravel() / 2) - M1                                # number of no-links between components
            r = z[nn, :].T@X[nn, n][:, np.newaxis]                                          # number of links from node n(0)
            R = np.tile(r, (1, K))
            beta_old_comps = betaln(M1+R+a, M0+M-R+b)-betaln(M1+a, M0+b)
            beta_new_comp = betaln(r+a, m-r+b)-betaln(a, b)                                 # new component's values
            likelihood_change = sum(np.concatenate((beta_old_comps,
                                    beta_new_comp), axis=1), 0)
            m[m == 0] = eps                                                                 # used to avoid log(0)
            prior_change = np.log(np.append(m, A))
            logP = likelihood_change + prior_change                                         # Log prob of n belonging to existing or new component
            P = np.exp(logP-logP.max())                                                     # Convert from log probability
            rand_arr = np.random.rand() < np.cumsum(P)/P.sum()                              # Random component according to P
            i = rand_arr.tolist().index(True)
            z[n, :] = 0
            new_arr = np.zeros((z.shape[0], 1))
            z = np.concatenate((z, new_arr), axis=1)
            z[n, i] = 1
            empty_cluster = np.argwhere(np.sum(z, axis=0) == 0).squeeze()                   # remove empty components
            z = np.delete(z, empty_cluster, 1)
        Z.append(z.copy())
    return Z