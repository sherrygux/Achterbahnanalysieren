import pandas as pd
import numpy as np
from scipy.ndimage import filters
from scipy.optimize import minimize
import json

class Achterbahn:

    def __init__(self, path, path_json):
        self.path = path
        self.path_json = path_json

    def getJsonFile(self):
        with open(self.path_json, 'r') as load_f:
            load_dict = json.load(load_f)
            zhat_interval = load_dict['known_orientations']['zhat']
            zx_interval = load_dict['known_orientations']['z-x']
            return zhat_interval, zx_interval

    def filter(self):
        df = pd.read_csv(self.path, usecols=[1, 2, 3, 4])
        accs = np.array(df)
        t_N = accs[-1][0]
        N = accs.shape[0]
        h = 1 / N
        t_interp = np.linspace(0, (N - 1) * h * t_N, N, endpoint=True)
        xp = accs[:, 0]
        fp_x = accs[:, 1]
        fp_y = accs[:, 2]
        fp_z = accs[:, 3]
        x_filted = filters.gaussian_filter(np.interp(t_interp, xp, fp_x), 5)
        y_filted = filters.gaussian_filter(np.interp(t_interp, xp, fp_y), 5)
        z_filted = filters.gaussian_filter(np.interp(t_interp, xp, fp_z), 5)
        accsFilted = accs
        accsFilted[:, 0] = t_interp
        accsFilted[:, 1] = x_filted
        accsFilted[:, 2] = y_filted
        accsFilted[:, 3] = z_filted
        return accsFilted


    def afterCalibration(self):

        def rotation(n, alpha):
            aa = 1 - np.cos(alpha)
            bb = np.sin(alpha)
            cc = np.cos(alpha)
            return np.array([[n[0] ** 2 * aa + cc, n[0] * n[1] * aa - n[2] * bb, n[0] * n[2] * aa + n[1] * bb],
                             [n[0] * n[1] * aa + n[2] * bb, n[1] ** 2 * aa + cc, n[1] * n[2] * aa - n[0] * bb],
                             [n[0] * n[2] * aa - n[1] * bb, n[1] * n[2] * aa + n[0] * bb, n[2] ** 2 * aa + cc]])

        accs = self.filter()
        t_coaster = accs[:, 0]
        t_begin = np.array([t for t in t_coaster if t >= self.getJsonFile()[0][0] and t <= self.getJsonFile()[0][1]])
        z = accs[list(t_coaster).index(t_begin[0]):list(t_coaster).index(t_begin[-1]), 1:]
        zHat = np.mean(z, axis=0)
        zHat_norm = zHat / np.linalg.norm(zHat)
        e_3 = np.array([0, 0, 1])
        a = np.cross(zHat_norm, e_3)
        a_norm = a / np.linalg.norm(a)
        phi = np.arctan2(np.linalg.norm(a), np.inner(zHat_norm, e_3))
        accs_new = accs
        accs_new[:, 1:] = (rotation(a_norm, phi) @ accs[:, 1:].T).T
        t_rise = np.array([t for t in t_coaster if t >= self.getJsonFile()[1][0] and t <= self.getJsonFile()[1][1]])
        v = accs_new[list(t_coaster).index(t_rise[0]):list(t_coaster).index(t_rise[-1]), 1:]
        vHat = np.mean(v, axis=0)
        vHat_norm = vHat / np.linalg.norm(vHat)
        psi = -np.arctan2(vHat_norm[1], vHat_norm[0])
        accs_final = accs_new
        accs_final[:, 1:] = (rotation(e_3, psi) @ accs_new[:, 1:].T).T
        accs_abs = np.sqrt(accs_final[:, 1] ** 2 + accs_final[:, 2] ** 2 + accs_final[:, 3] ** 2)
        return accs_final, accs_abs

    def maxAccs(self):
        data = self.afterCalibration()[0]
        maximum = np.max(data[:,1:],axis=0)
        maximum_index = np.argmax(data[:,1:],axis=0)
        t_x = data[maximum_index[0]][0]
        t_y = data[maximum_index[1]][0]
        t_z = data[maximum_index[2]][0]
        return maximum, t_x, t_y, t_z

    def maxAccsAbs(self):
        accs_abs = self.afterCalibration()[1]
        return np.max(accs_abs)

    def frequencyAccs(self):
        data = self.afterCalibration()[0]
        accs_abs = self.afterCalibration()[1]
        N = data.shape[0]
        freq = 0
        maximum = np.max(accs_abs, axis=0)
        if maximum < 2:
            print("This coaster is not so fast!")
        else:
            for accs in accs_abs:
                if accs >= 0.7 * maximum:
                    freq += 1
        return freq / N

    def weightlessness(self):
        data = self.afterCalibration()[0]
        N = data.shape[0]
        i = 0
        for accs_z in data[:, 3]:
            if accs_z >= 1:
                i += 1
        return i / N

    def angle(self):
        data = self.afterCalibration()[0]
        t_coaster = self.afterCalibration()[0][:,0]
        t_rise = np.array([t for t in t_coaster if t >= self.getJsonFile()[1][0] and t <= self.getJsonFile()[1][1]])
        v = data[list(t_coaster).index(t_rise[0]):list(t_coaster).index(t_rise[-1]), 1:]
        vHat = np.mean(v, axis=0)
        return np.arctan2(vHat[0], vHat[2]) * 180 / np.pi

    def Ellipse(self, t_N0, t_N0pN, minLoopLength, maxLoopLength, tol, minXAmp, minZAmp):

        def searchEllipse(t_0, t_N):

            def searchInterval(t_0, t_N):
                return np.array([t for t in t_accs if t >= t_0 and t <= t_N])

            def loss(args):
                E = 0
                x_m, z_m, r, s = args
                for t in interval:
                    a_ref = np.array(
                        [x_m + r * np.sin(2 * np.pi * (t - t_0) / (t_N - t_0)),
                         z_m + s * np.cos(2 * np.pi * (t - t_0) / (t_N - t_0))])
                    a = np.array(
                        [accs[:,1][list(t_accs).index(t)],
                         accs[:,3][list(t_accs).index(t)]])
                    E += np.linalg.norm(a - a_ref) ** 2
                return E / (N + 1)

            output = []
            interval = searchInterval(t_0, t_N)
            N = interval.shape[0]
            x0 = np.random.rand(4)
            bnds = ((None, None), (None, None), (0, None), (0, None))
            res = minimize(loss, x0, bounds=bnds)
            x_m, z_m, r, s = res.x
            if res.fun <= tol and r >= minXAmp and s >= minZAmp:
                ellipsen_x = np.zeros((N,))
                ellipsen_z = np.zeros((N,))
                for i, t in enumerate(interval):
                    ellipsen_x[i] = x_m + r * np.sin(2 * np.pi * (t - t_0) / (t_N - t_0))
                    ellipsen_z[i] = z_m + s * np.cos(2 * np.pi * (t - t_0) / (t_N - t_0))
                output =  [res.fun, interval, ellipsen_x, ellipsen_z]
            return output

        t_accs = self.filter()[:, 0]
        accs = self.afterCalibration()[0]
        t_search = np.array([t for t in t_accs if t >= t_N0 and t <= t_N0pN])
        t_splited = np.array_split(t_search, int(t_search.shape[0] * 0.01))
        ellipse = []
        for search_intervall in t_splited:
            print(search_intervall[0])
            loss_min = 999
            interval_opt = None
            ellipsen_x_opt = None
            ellipsen_z_opt = None
            isplot = False
            for i in range(minLoopLength, maxLoopLength + 1):
                print(i)
                output = searchEllipse(search_intervall[0], search_intervall[i])
                if output:
                    isplot = True
                    loss = output[0]
                    interval = output[1]
                    ellipsen_x = output[2]
                    ellipsen_z = output[3]
                    if loss < loss_min:
                        loss_min = loss
                        interval_opt = interval
                        ellipsen_x_opt = ellipsen_x
                        ellipsen_z_opt = ellipsen_z
            if isplot:
                ellipse.append([interval_opt, ellipsen_x_opt, ellipsen_z_opt])

        return ellipse
