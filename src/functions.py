import math

################################################################
# important points
# Single data and set data is imported as numpy array from any format file - needs to taken care operations according to ndarray
################################################################

import scipy.signal
import seaborn as sns
import pandas as pd
import sklearn
import numpy as np
import matplotlib.pyplot as plt

from tkinter import END
from sklearn import svm
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from tkinter import simpledialog
from spectres import spectres

# plt.style.use('seaborn-white')


class Functions(object):
    def __init__(self, inverse_gui):
        self.inverse_gui = inverse_gui  # initailizing the inverse_gui class

    def tx2abs(self):
        d1 = self.inverse_gui  # creating object for inverse_gui so that we can access all the variables and functions from inverse_gui class
        if d1.choice == 1:
            WL = d1.wavelength
            data = d1.spectra
            if np.mean(data)>10:
                abs_spectra = 2-np.log10(data)  # apply negetive log base 10 to convert tx to abs
            else:
                abs_spectra = -np.log10(data)  # apply negetive log base 10 to convert tx to abs
            d1.plot_fig(WL, abs_spectra)
            k = d1.listval  # get current listval
            d1.spec_wl_data.append([WL, abs_spectra])  # update generated data to listbox
            d1.listboxitems.append(d1.indexselected + '_Absorbance')
            d1.listbox.insert(END, d1.listboxitems[k])
            d1.listval = k + 1  # increment listval
        elif d1.choice == 2:
            WL = d1.wavelength_set
            data = d1.spectra_set
            label = d1.label
            if np.mean(data)>10:
                abs_spectra = 2-np.log10(data)  # apply negetive log base 10 to convert tx to abs
            else:
                abs_spectra = -np.log10(data)  # apply negetive log base 10 to convert tx to abs
            k = d1.listval_set  # get the current listval set
            d1.spec_wl_data_set.append([WL, abs_spectra, label])  # update generated dataset to listboxset
            d1.plot_fig_dataset(WL, abs_spectra, label='Absorbance spectra')
            d1.listboxitems_set.append(d1.indexselected + '_Absorbance')
            d1.listbox_set.insert(END, d1.listboxitems_set[k])
            d1.listval_set = k + 1  # increment the listvalset

    def abs2tx(self):
        d1 = self.inverse_gui
        if d1.choice == 1:
            WL = d1.wavelength
            data = d1.spectra
            if np.mean(data)>10:
                tx_spectra = np.power(10,2) - np.power(10, -data)  # equation to convert the abs to tx
            else:
                tx_spectra = np.power(10, -data)  # equation to convert the abs to tx
            d1.plot_fig(WL, tx_spectra)
            k = d1.listval
            d1.spec_wl_data.append([WL, tx_spectra])
            d1.listboxitems.append(d1.indexselected + '_transmittance')
            d1.listbox.insert(END, d1.listboxitems[k])
            d1.listval = k + 1
        elif d1.choice == 2:
            WL = d1.wavelength_set
            data = d1.spectra_set
            label = d1.label
            if np.mean(data) > 10:
                tx_spectra = np.power(10, 2) - np.power(10, -data)  # equation to convert the abs to tx
            else:
                tx_spectra = np.power(10, -data)  # equation to convert the abs to tx
            d1.plot_fig_dataset(WL, tx_spectra, label='Transmittance spectra')
            k = d1.listval_set
            d1.spec_wl_data_set.append([WL, tx_spectra, label])
            d1.listboxitems_set.append(d1.indexselected + '_transmittance')
            d1.listbox_set.insert(END, d1.listboxitems_set[k])
            d1.listval_set = k + 1

    def pca(self):
        d1 = self.inverse_gui
        if d1.choice == 2:
            pc_column = []
            WL = d1.wavelength_set
            data = d1.spectra_set
            label = d1.label
            data = data.T  # transpose the data and label
            label = label.T
            data = StandardScaler().fit_transform(data)  # fit and transform the data
            ncomp = simpledialog.askinteger("input",
                                            "Enter the number of components")  # ask user the number of PCA components
            for i in range(0, ncomp, 1):
                pc_column.append('PC' + str(i))  # creating the column of PC's
            print(pc_column)
            pca = PCA(n_components=ncomp)  # call PCA inuilt function
            pc = pca.fit_transform(data)  # apply PCA object on the data
            plt.clf()  # clear all the plots
            plt.subplot(1,2,1)
            plt.plot(np.cumsum(pca.explained_variance_ratio_))
            plt.xlabel('number of components')
            plt.ylabel('cumulative explained variance');
            pc_df = pd.DataFrame(data=pc,
                                 columns=pc_column)
            pc_df['Cluster'] = label[0].tolist()
            pc_df.head()

            df_expvar = pd.DataFrame({'var': pca.explained_variance_ratio_,
                                      'PC': pc_column})
            plt.subplot(1,2,2)
            sns.barplot(x='PC', y="var",
                        data=df_expvar, color="c");

            sns.lmplot(x="PC0", y="PC1",
                       data=pc_df,
                       fit_reg=False,
                       hue='Cluster',  # color by cluster
                       legend=True,
                       scatter_kws={"s": 80});
            plt.title("PCA components cluster")
        else:
            simpledialog.messagebox.showerror("Error", "PCA need batch data to function!")

    # function to get the accuracy of training of data
    def getAccuracy(self, testSet, predictions):
        correct = 0
        for x in range(len(testSet)):
            if testSet[x] == predictions[x]:
                correct += 1
        return (correct / float(len(testSet))) * 100.0

    # function to apply logistic regression on the data set.
    def LR(self):
        d1 = self.inverse_gui
        if d1.choice == 2:
            data = d1.spectra_set
            data = data.T
            label = d1.label
            label = label.T
            wavelength = d1.wavelength_set
            test_size = simpledialog.askinteger("input",
                                                "Enter the test size in percentage(out of 100)")  # ask user the percent of test split
            X_train, X_test, y_train, y_test = train_test_split(data, label,
                                                                test_size=test_size / 100)  # train_test_split
            print(X_train.shape, y_train.shape)
            print(X_test.shape, y_test.shape)

            clf = LogisticRegression(random_state=0, solver='lbfgs',
                                     multi_class='multinomial')  # craeting object for LR

            clf.fit(X_train, y_train)  # fitting data

            print(clf)
            # matrix = clf.densify()
            # print(matrix)
            accu = clf.predict_proba(X_test)
            preds = clf.predict(X_test)
            print(pd.crosstab(y_test[0], preds, rownames=['Actual Result'], colnames=['Predicted Result']))
            accuracy = self.getAccuracy(list(y_test[0]), preds)
            print('Accuracy: ' + repr(accuracy) + '%')
            d1.Result.insert(END, pd.crosstab(y_test[0], preds, rownames=['Actual Result'],
                                              colnames=['Predicted Result']))  # print decision matrix on result section
            d1.Result.insert(END, '\n')
            d1.Result.insert(END,
                             'Accuracy: ' + repr(accuracy) + '%')  # pint the accuracy of algorithm in result section
        else:
            simpledialog.messagebox.showerror("Error", "LR need batch data to function!")

    def KNN(self):
        d1 = self.inverse_gui
        if d1.choice == 2:
            data = d1.spectra_set
            data = data.T
            label = d1.label
            label = label.T
            wavelength = d1.wavelength_set
            test_size = simpledialog.askinteger("input", "Enter the test size in percentage(out of 100)")
            X_train, X_test, y_train, y_test = train_test_split(data, label, test_size=test_size / 100)
            print(X_train.shape, y_train.shape)
            print(X_test.shape, y_test.shape)

            clf = KNeighborsClassifier(n_neighbors=6, weights='distance', algorithm='auto', leaf_size=20, p=2,
                                       metric='minkowski', n_jobs=2)

            clf.fit(X_train, y_train)

            # matrix = clf.densify()
            # print(matrix)
            accu = clf.predict_proba(X_test)
            preds = clf.predict(X_test)
            print(pd.crosstab(y_test[0], preds, rownames=['Actual Result'], colnames=['Predicted Result']))
            accuracy = self.getAccuracy(list(y_test[0]), preds)
            print('Accuracy: ' + repr(accuracy) + '%')
            d1.Result.delete(1.0, END)
            d1.Result.insert(END,
                             pd.crosstab(y_test[0], preds, rownames=['Actual Result'], colnames=['Predicted Result']))
            d1.Result.insert(END, '\n')
            d1.Result.insert(END, 'Accuracy: ' + repr(accuracy) + '%')
        else:
            simpledialog.messagebox.showerror("Error", "KNN need batch data to function!")

    def svm_classification(self):
        d1 = self.inverse_gui
        if d1.choice == 2:
            data = d1.spectra_set
            data = data.T
            label = d1.label
            label = label.T
            wavelength = d1.wavelength_set
            test_size = simpledialog.askinteger("input", "Enter the test size in percentage(out of 100)")
            X_train, X_test, y_train, y_test = train_test_split(data, label, test_size=test_size / 100)
            print(X_train.shape, y_train.shape)
            print(X_test.shape, y_test.shape)

            clf = svm.SVC(gamma='scale')

            clf.fit(X_train, y_train)

            # matrix = clf.densify()
            # print(matrix)
            # accu = clf.predict_proba(X_test)
            preds = clf.predict(X_test)
            print(pd.crosstab(y_test[0], preds, rownames=['Actual Result'], colnames=['Predicted Result']))
            accuracy = self.getAccuracy(list(y_test[0]), preds)
            print('Accuracy: ' + repr(accuracy) + '%')
            d1.Result.delete(1.0, END)
            d1.Result.insert(END,
                             pd.crosstab(y_test[0], preds, rownames=['Actual Result'], colnames=['Predicted Result']))
            d1.Result.insert(END, '\n')
            d1.Result.insert(END, 'Accuracy: ' + repr(accuracy) + '%')
        else:
            simpledialog.messagebox.showerror("Error", "SVM classification need batch data to function!")

    def linear_discreminate_analysis(self):
        d1 = self.inverse_gui
        if d1.choice == 2:
            data = d1.spectra_set
            data = data.T
            label = d1.label
            label = label.T
            wavelength = d1.wavelength_set
            test_size = simpledialog.askinteger("input", "Enter the test size in percentage(out of 100)")
            X_train, X_test, y_train, y_test = train_test_split(data, label, test_size=test_size / 100)
            print(X_train.shape, y_train.shape)
            print(X_test.shape, y_test.shape)

            clf = LinearDiscriminantAnalysis()

            clf.fit(X_train, y_train)

            # matrix = clf.densify()
            # print(matrix)
            # accu = clf.predict_proba(X_test)
            preds = clf.predict(X_test)
            print(pd.crosstab(y_test[0], preds, rownames=['Actual Result'], colnames=['Predicted Result']))
            accuracy = self.getAccuracy(list(y_test[0]), preds)
            print('Accuracy: ' + repr(accuracy) + '%')
            d1.Result.delete(1.0, END)
            d1.Result.insert(END,
                             pd.crosstab(y_test[0], preds, rownames=['Actual Result'], colnames=['Predicted Result']))
            d1.Result.insert(END, '\n')
            d1.Result.insert(END, 'Accuracy: ' + repr(accuracy) + '%')
        else:
            simpledialog.messagebox.showerror("Error", "Linear discreminate analysis need batch data to function!")

    def Random_forest(self):
        d1 = self.inverse_gui
        if d1.choice == 2:
            data = d1.spectra_set
            data = data.T
            label = d1.label
            label = label.T
            wavelength = d1.wavelength_set
            test_size = simpledialog.askinteger("input", "Enter the test size in percentage(out of 100)")
            X_train, X_test, y_train, y_test = train_test_split(data, label, test_size=test_size / 100)
            print(X_train.shape, y_train.shape)
            print(X_test.shape, y_test.shape)

            clf = RandomForestClassifier(n_jobs=2, random_state=0)

            clf.fit(X_train, y_train)

            # matrix = clf.densify()
            # print(matrix)
            accu = clf.predict_proba(X_test)
            preds = clf.predict(X_test)
            print(pd.crosstab(y_test[0], preds, rownames=['Actual Result'], colnames=['Predicted Result']))
            accuracy = self.getAccuracy(list(y_test[0]), preds)
            print('Accuracy: ' + repr(accuracy) + '%')
            d1.Result.delete(1.0, END)
            d1.Result.insert(END,
                             pd.crosstab(y_test[0], preds, rownames=['Actual Result'], colnames=['Predicted Result']))
            d1.Result.insert(END, '\n')
            d1.Result.insert(END, 'Accuracy: ' + repr(accuracy) + '%')
        else:
            simpledialog.messagebox.showerror("Error", "Random forest need batch data to function!")

    def resolution_change(self):
        d1 = self.inverse_gui
        if d1.choice == 1:
            wavelength = d1.wavelength
            data = d1.spectra
            current_resolution = wavelength[1] - wavelength[0]
            simpledialog.messagebox.showinfo("Info", "Current resolution is " + str(current_resolution))
            new_spectra_resolution = simpledialog.askfloat("input", "Enter the new spectral resolution")

            start_wl = wavelength[0] + new_spectra_resolution
            end_wl = wavelength[-1] - new_spectra_resolution
            newgrid = np.arange(start_wl, end_wl, new_spectra_resolution) + current_resolution

            spec_resampled = spectres(newgrid, wavelength, data, spec_errs=None)
            plt.clf()
            plt.plot(wavelength, data, label='Original spectra')
            plt.plot(newgrid, spec_resampled, label='Resampled spectra')

            k = d1.listval
            d1.spec_wl_data.append([newgrid, spec_resampled])
            d1.listboxitems.append(f'{d1.indexselected}_Resampled_{new_spectra_resolution}')
            d1.listbox.insert(END, d1.listboxitems[k])
            d1.listval = k + 1
        else:
            wavelength = d1.wavelength_set
            data = d1.spectra_set
            label = d1.label
            wavelength = wavelength.values()
            # data = data.values
            # data = data.ravel()
            current_resolution = wavelength[1] - wavelength[0]
            simpledialog.messagebox.showinfo("Info", "Current resolution is " + str(current_resolution))
            new_spectra_resolution = simpledialog.askfloat("input", "Enter the new spectral resolution")

            start_wl = wavelength[0] + new_spectra_resolution
            end_wl = wavelength[-1] - new_spectra_resolution
            newgrid = np.arange(start_wl, end_wl, new_spectra_resolution) + current_resolution

            spec_resampled = spectres(newgrid, wavelength, data, spec_errs=None)
            plt.clf()
            plt.plot(wavelength, data, label='Original spectra')
            plt.plot(newgrid, spec_resampled, label='Resampled spectra')

            k = d1.listval_set
            d1.spec_wl_data_set.append([wavelength, spec_resampled, label])
            d1.listboxitems_set.append(d1.indexselected + '_Resampled_')
            d1.listbox_set.insert(END, d1.listboxitems_set[k])
            d1.listval_set = k + 1

    def moving_average(self):
        d1 = self.inverse_gui
        if d1.choice == 1:
            wavelength = d1.wavelength
            data = d1.spectra
            windowsize = simpledialog.askinteger("input", "Enter the window size of filter")
            moving = pd.DataFrame(data).rolling(window=windowsize).mean()
            plt.clf()
            plt.plot(wavelength, data, label="original spectra")
            plt.plot(wavelength, moving, label="MA Smoothened Spectra")

            k = d1.listval
            d1.spec_wl_data.append([wavelength, moving])
            d1.listboxitems.append(d1.indexselected + '_movingaverage_' + str(windowsize))
            d1.listbox.insert(END, d1.listboxitems[k])
            d1.listval = k + 1
        else:
            wavelength = d1.wavelength_set
            data = d1.spectra_set
            shape = data.shape
            label = d1.label
            windowsize = simpledialog.askinteger("input", "Enter the window size of filter")
            moving = pd.DataFrame(data).rolling(window=windowsize).mean()
            data = np.reshape(data, shape)
            moving = np.reshape(moving, shape)
            plt.clf()
            plt.plot(wavelength, data, label="original spectra")
            plt.plot(wavelength, moving, label="MA Smoothened Spectra")
            plt.legend()

            moving = pd.DataFrame(moving)
            k = d1.listval_set
            d1.spec_wl_data_set.append([wavelength, moving, label])
            d1.listboxitems_set.append(d1.indexselected + '_movingaverage_' + str(windowsize))
            d1.listbox_set.insert(END, d1.listboxitems_set[k])
            d1.listval_set = k + 1

    def gaussian_filter(self):
        d1 = self.inverse_gui
        if d1.choice == 1:
            wavelength = d1.wavelength
            data = d1.spectra
            sigma = simpledialog.askinteger("input", "Enter the sigma value of the filter")
            order = simpledialog.askinteger("input", "Enter the order of the filter")
            gaussian = scipy.ndimage.gaussian_filter(data, sigma, order)
            plt.clf()
            plt.plot(wavelength, data, label="original spectra")
            plt.plot(wavelength, gaussian, label="Gaussian filtered Spectra")

            k = d1.listval
            d1.spec_wl_data.append([wavelength, gaussian])
            d1.listboxitems.append(d1.indexselected + '_Gaussianfilter_' + str(sigma))
            d1.listbox.insert(END, d1.listboxitems[k])
            d1.listval = k + 1
        else:
            wavelength = d1.wavelength_set
            data = d1.spectra_set
            shape = data.shape
            label = d1.label
            # data = data.values
            # data = data.ravel()
            sigma = simpledialog.askinteger("input", "Enter the sigma value of the filter")
            order = simpledialog.askinteger("input", "Enter the order of the filter")
            gaussian = scipy.ndimage.gaussian_filter(data, sigma, order)
            data = np.reshape(data, shape)
            gaussian = np.reshape(gaussian, shape)
            plt.clf()
            plt.plot(wavelength, data, label="original spectra")
            plt.plot(wavelength, gaussian, label="Gaussian filtered Spectra")

            gaussian = pd.DataFrame(gaussian)
            k = d1.listval_set
            d1.spec_wl_data_set.append([wavelength, gaussian, label])
            d1.listboxitems_set.append(d1.indexselected + '_Gaussianfilter_' + str(sigma))
            d1.listbox_set.insert(END, d1.listboxitems_set[k])
            d1.listval_set = k + 1

    def median_filter(self):
        d1 = self.inverse_gui
        if d1.choice == 1:
            wavelength = d1.wavelength
            data = d1.spectra
            windowsize = simpledialog.askinteger("input", "Enter the window size of filter")
            if windowsize%2 != 0:
                median_filter = scipy.signal.medfilt(data, windowsize)
                plt.clf()
                plt.plot(wavelength, data, label="Original spectra")
                plt.plot(wavelength, median_filter, label="median Smoothened Spectra")
                plt.legend()
                k = d1.listval
                d1.spec_wl_data.append([wavelength, median_filter])
                d1.listboxitems.append(d1.indexselected + '_medianfilter_' + str(windowsize))
                d1.listbox.insert(END, d1.listboxitems[k])
                d1.listval = k + 1
            else:
                 simpledialog.messagebox.showerror("ERROR",
                                                      "window_length must be a positive odd integer!")
        else:
            wavelength = d1.wavelength_set
            data = d1.spectra_set
            shape = data.shape
            # data = data.values
            # data = data.ravel()
            windowsize = simpledialog.askinteger("input", "Enter the window size of filter")
            if windowsize % 2 != 0:
                median_filter = scipy.signal.medfilt(data, windowsize)
                data = np.reshape(data, shape)
                median_filter = np.reshape(median_filter, shape)
                plt.plot(wavelength, data, label="Original spectra")
                plt.plot(wavelength, median_filter, label="Median Smoothened Spectra")

                median_filter = pd.DataFrame(median_filter)
                k = d1.listval_set
                d1.spec_wl_data_set.append([wavelength, median_filter, d1.label])
                d1.listboxitems_set.append(d1.indexselected + '_medianfilter_' + str(windowsize))
                d1.listbox_set.insert(END, d1.listboxitems_set[k])
                d1.listval_set = k + 1
            else:
                simpledialog.messagebox.showerror("ERROR",
                                                  "window_length must be a positive odd integer!")

    def SG_filter(self):
        d1 = self.inverse_gui
        if d1.choice == 1:
            wavelength = d1.wavelength
            data = d1.spectra
            windowsize = simpledialog.askinteger("input", "Enter the window length of the filter")
            polyorder = simpledialog.askinteger("input", "Enter the polyorder")
            if (windowsize % 2 != 0) and polyorder < windowsize:
                sg_filter = scipy.signal.savgol_filter(data, windowsize, polyorder, deriv=0)
                plt.clf()
                plt.plot(wavelength, data, label="Original spectra")
                plt.plot(wavelength, sg_filter, label="SG smothned spectra")

                k = d1.listval
                d1.spec_wl_data.append([wavelength, sg_filter])
                d1.listboxitems.append(d1.indexselected + '_SGfilter_' + str(windowsize))
                d1.listbox.insert(END, d1.listboxitems[k])
                d1.listval = k + 1
            else:
                simpledialog.messagebox.showerror("ERROR",
                                                  "window_length must be a positive odd integer and polyorder must be less than window_length.")

        else:
            wavelength = d1.wavelength_set
            data = d1.spectra_set
            shape = data.shape
            # data = data.values
            # data = data.ravel()
            windowsize = simpledialog.askinteger("input", "Enter the window length of the filter")
            polyorder = simpledialog.askinteger("input", "Enter the polyorder")
            if (windowsize % 2 != 0) and polyorder < windowsize:
                sg_filter = scipy.signal.savgol_filter(data, windowsize, polyorder, deriv=0)
                data = np.reshape(data, shape)
                sg_filter = np.reshape(sg_filter, shape)
                plt.clf()
                plt.plot(wavelength, data, label="Original spectra")
                plt.plot(wavelength, sg_filter, label="SG smothned spectra")

                sg_filter = pd.DataFrame(sg_filter)
                k = d1.listval_set
                d1.spec_wl_data_set.append([wavelength, sg_filter, d1.label])
                d1.listboxitems_set.append(d1.indexselected + '_SGfilter_' + str(windowsize))
                d1.listbox_set.insert(END, d1.listboxitems_set[k])
                d1.listval_set = k + 1
            else:
                simpledialog.messagebox.showerror("ERROR",
                                                  "window_length must be a positive odd integer and polyorder must be less than window_length.")

    def SG_deriv(self):
        d1 = self.inverse_gui
        if d1.choice == 1:
            wavelength = d1.wavelength
            data = d1.spectra
            windowsize = simpledialog.askinteger("input", "Enter the window length of the filter")
            polyorder = simpledialog.askinteger("input", "Enter the polyorder")
            deriv = simpledialog.askinteger("Input", "Enter the order of the derivative")
            if (windowsize % 2 != 0) and polyorder < windowsize:
                sg_deriv = scipy.signal.savgol_filter(data, windowsize, polyorder, deriv=deriv)
                plt.clf()
                plt.plot(wavelength, data, label="Original spectra")
                plt.plot(wavelength, sg_deriv, label="SG derivative spectra")

                k = d1.listval
                d1.spec_wl_data.append([wavelength, sg_deriv])
                d1.listboxitems.append(d1.indexselected + '_SGderiv_' + str(windowsize))
                d1.listbox.insert(END, d1.listboxitems[k])
                d1.listval = k + 1
            else:
                simpledialog.messagebox.showerror("ERROR",
                                                  "window_length must be a positive odd integer and polyorder must be less than window_length.")
        else:
            wavelength = d1.wavelength_set
            data = d1.spectra_set
            shape = data.shape
            # data = data.values
            data = data.ravel()
            windowsize = simpledialog.askinteger("input", "Enter the window length of the filter")
            polyorder = simpledialog.askinteger("input", "Enter the polyorder")
            deriv = simpledialog.askinteger("Input", "Enter the order of the derivative")
            if (windowsize % 2 != 0) and polyorder < windowsize:
                sg_deriv = scipy.signal.savgol_filter(data, windowsize, polyorder, deriv=deriv)
                data = np.reshape(data, shape)
                sg_deriv = np.reshape(sg_deriv, shape)
                plt.clf()
                plt.plot(wavelength, data, label="Original spectra")
                plt.plot(wavelength, sg_deriv, label="SG derivative spectra")
                sg_deriv = pd.DataFrame(sg_deriv)
                k = d1.listval_set
                d1.spec_wl_data_set.append([wavelength, sg_deriv, d1.label])
                d1.listboxitems_set.append(d1.indexselected + '_SGderiv_' + str(windowsize))
                d1.listbox_set.insert(END, d1.listboxitems_set[k])
                d1.listval_set = k + 1
            else:
                simpledialog.messagebox.showerror("ERROR",
                                                  "window_length must be a positive odd integer and polyorder must be less than window_length.")

    def snv(input_data):

        # Define a new array and populate it with the corrected data
        data_snv = np.zeros_like(input_data)
        for i in range(input_data.shape[1]):
            # Apply correction
            data_snv[:, i] = (input_data[:, i] - np.mean(input_data[:, i])) / np.std(input_data[:, i])

        return data_snv

    def apply_snv(self):
        d1 = self.inverse_gui
        if d1.choice == 1:
            simpledialog.messagebox.showerror("Error", "SNV need batch data to function!")
        else:
            wavelength = d1.wavelength_set
            data = d1.spectra_set
            label = d1.label
            data = data.values
            # data = data.ravel()
            # Xsnv = self.snv(data)
            data_snv = np.zeros_like(data)
            for i in range(data.shape[1]):
                # Apply correction
                data_snv[:, i] = (data[:, i] - np.mean(data[:, i])) / np.std(data[:, i])
            plt.clf()
            plt.subplot(211)
            plt.plot(wavelength, data, label='Original spectra')
            plt.subplot(212)
            plt.plot(wavelength, data_snv, label="SNV applied spectra")
            data_snv = pd.DataFrame(data_snv)
            k = d1.listval_set
            d1.spec_wl_data_set.append([wavelength, data_snv, label])
            d1.listboxitems_set.append(d1.indexselected + '_SNV')
            d1.listbox_set.insert(END, d1.listboxitems_set[k])
            d1.listval_set = k + 1

    def msc(self, input_data, reference=None):
        ''' Perform Multiplicative scatter correction'''

        # mean centre correction
        for i in range(input_data.shape[0]):
            input_data[i, :] -= input_data[i, :].mean()

        # Get the reference spectrum. If not given, estimate it from the mean
        if reference is None:
            # Calculate mean
            ref = np.mean(input_data, axis=0)
        else:
            ref = reference

        # Define a new array and populate it with the corrected data
        data_msc = np.zeros_like(input_data)
        for i in range(input_data.shape[0]):
            # Run regression
            fit = np.polyfit(ref, input_data[i, :], 1, full=True)
            # Apply correction
            data_msc[i, :] = (input_data[i, :] - fit[0][1]) / fit[0][0]

        return (data_msc, ref)

    def apply_msc(self):
        d1 = self.inverse_gui
        if d1.choice == 1:
            simpledialog.messagebox.showerror("Error", "SNV need batch data to function!")
        else:
            wavelength = d1.wavelength_set
            data = d1.spectra_set
            label = d1.label
            data = data.T
            data = data.values
            # data = data.ravel()

            msc_data = self.msc(data.copy())[0]
            msc_data = pd.DataFrame(msc_data)

            data = data.T
            msc_data = msc_data.T
            plt.subplot(211)
            plt.plot(wavelength, data, label="Original spectra")
            plt.subplot(212)
            plt.plot(wavelength, msc_data, label="SG smothned spectra")

    def interpolate(self):
        d1 = self.inverse_gui
        if d1.choice == 1:
            wavelength = d1.wavelength
            wavelength = wavelength.values
            data = d1.spectra
            data = data.values
            data = data.ravel()

            inter = scipy.interpolate.interp1d(wavelength, data, "cubic")
            wavelength_new = np.arange(wavelength[0], wavelength[-1], (wavelength[1] - wavelength[0]) / 4)
            data_inter = inter(wavelength_new)

            plt.subplot(211)
            plt.plot(wavelength, data, label="Original spectra")
            plt.subplot(212)
            plt.plot(wavelength_new, data_inter, label="SG smothned spectra")
        else:
            simpledialog.messagebox.showerror("Error", "Interpolate can not be applied on Batch data!")

    def normalize(self):
        d1 = self.inverse_gui
        if d1.choice == 1:
            simpledialog.messagebox.showerror("Error", "SNV need batch data to function!")
        else:
            wavelength = d1.wavelength_set
            data = d1.spectra_set
            label = d1.label
            data = data.values
            # data = data.ravel()
            Xnormalize = sklearn.preprocessing.normalize(data)
            Xnormalize = pd.DataFrame(Xnormalize)
            plt.clf()
            plt.subplot(211)
            plt.plot(wavelength, data, label='Original spectra')
            plt.subplot(212)
            plt.plot(wavelength, Xnormalize, label="Normalized spectra")

            k = d1.listval_set
            d1.spec_wl_data_set.append([wavelength, Xnormalize, label])
            d1.listboxitems_set.append(d1.indexselected + '_Normalized')
            d1.listbox_set.insert(END, d1.listboxitems_set[k])
            d1.listval_set = k + 1

    def transpose(self):
        d1 = self.inverse_gui
        if d1.choice == 1:
            simpledialog.messagebox.showerror("Error", "Transpose need batch data to function!")
        else:
            wavelength = d1.wavelength_set
            data = d1.spectra_set
            label = d1.label

            data_t = data.T
            wavelength_t = wavelength.T
            label_t = label.T

            k = d1.listval_set
            d1.spec_wl_data_set.append([wavelength_t, data_t, label_t])
            d1.listboxitems_set.append(d1.indexselected + '_transposed')
            d1.listbox_set.insert(END, d1.listboxitems_set[k])
            d1.listval_set = k + 1

    def duplicate(self):
        d1 = self.inverse_gui
        if d1.choice == 1:
            wavelength = d1.wavelength
            data = d1.spectra
            shape = data.shape
            dup = simpledialog.askinteger("Input", "Enter the number of duplicate spectras with noise")
            dup_data = []
            for i in range(dup):
                noise = 0.01 * (np.random.normal(0, 1, shape[0]))
                dup_data.append(data.ravel() + noise)
            dup_data = np.reshape(dup_data, [shape[0],dup])
            plt.plot(wavelength, dup_data)

            k = d1.listval
            d1.spec_wl_data.append([wavelength, dup_data])
            d1.listboxitems.append(d1.indexselected + '_duplicate' + str(dup))
            d1.listbox.insert(END, d1.listboxitems[k])
            d1.listval = k + 1
        if d1.choice == 2:
            simpledialog.messagebox.showerror("Error", "Duplicate is only for single data!")

    def info(self):
        d1 = self.inverse_gui
        if d1.choice == 1:
            start_wl = d1.wavelength[0][0]
            end_wl = d1.wavelength[-1][0]
            resolution = np.round((d1.wavelength[2]-d1.wavelength[1])[0],2)
            mean_data = np.round(np.mean(d1.spectra),2)
            simpledialog.messagebox.showinfo(title="Info",
                                        message= f'file name: {d1.filename} \n'
                                                 f'starting wavelength: {start_wl} \n'
                                                 f'ending wavelength: {end_wl} \n'
                                                 f'Spectral Resolution: {resolution} \n'
                                                 f'Mean data: {mean_data}')
        else:
            start_wl = d1.wavelength_set[0][0]
            end_wl = d1.wavelength_set[-1][0]
            resolution = np.round((d1.wavelength_set[2] - d1.wavelength_set[1])[0],2)
            mean_data = np.round(np.mean(d1.spectra_set), 2)
            simpledialog.messagebox.showinfo(title="Info",
                                             message=f'file name: {d1.filename} \n'
                                                     f'starting wavelength: {start_wl} \n'
                                                     f'ending wavelength: {end_wl} \n'
                                                     f'Spectral Resolution: {resolution} \n'
                                                     f'Mean data: {mean_data}')


    def resize(self):
        d1 = self.inverse_gui
        if d1.choice == 1:
            wavelength = d1.wavelength
            data = d1.spectra
            shape = data.shape
            wl_min = simpledialog.askfloat("Input", "Enter the minimum wavelength within the range")
            wl_max = simpledialog.askfloat("Input", "Enter the maximum wavelength within the range")
            new_wl = list(filter(lambda x: float(x) >= float(wl_min) and float(x) <= float(wl_max), wavelength))
            outnew = []
            b = len(wavelength)
            s = len(new_wl)
            for i in range(0, b):
                for j in range(0, s):
                    if wavelength[i] == new_wl[j]:
                        outnew.append(i)
            p = outnew[0]
            q = outnew[-1]
            newX = data[p:q + 1]
            plt.plot(wavelength, data)
            plt.plot(new_wl, newX)

            k = d1.listval
            d1.spec_wl_data.append([new_wl, newX])
            d1.listboxitems.append(d1.indexselected + '_Resized')
            d1.listbox.insert(END, d1.listboxitems[k])
            d1.listval = k + 1

# class Demo():
#     instance = None
#
#     def __new__(cls, xx):
#         if not cls.instance:
#             cls.instance = Demo._Demo(xx)
#         return cls.instance
#
#     class _Demo():
#         def __init__(self, xx):
#             self.xx = xx
#
#         def print_xx(self):
#             print(self.xx)
