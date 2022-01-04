

import numpy as np
import pandas as pd
from sklearn.metrics import r2_score


from PySide2.QtCharts import QtCharts
from PySide2.QtWidgets import QTabWidget, QTableWidgetItem, QHeaderView
from PySide2.QtCore import QDate

import webbrowser




# IMPORT GUI FILE


from ui_interface import *




class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setMinimumSize(850, 600)
        loadJsonStyle(self, self.ui)

        self.ui.pushButton_11.clicked.connect(self.browsefiles)
        self.ui.pushButton_20.clicked.connect(self.workforce)
        arg = 1
        arg2 = 2
        arg3 = 3
        self.ui.pushButton_22.clicked.connect(lambda: self.addRow(arg))
        self.ui.pushButton_21.clicked.connect(lambda: self.removeRow(arg))
        self.ui.nxt.clicked.connect(self.next_page)
        self.ui.prev.clicked.connect(self.prev_page)
        self.ui.pushButton_14.clicked.connect(lambda: self.addRow(arg2))
        self.ui.pushButton_16.clicked.connect(lambda: self.removeRow(arg2))
        self.ui.pushButton_17.clicked.connect(self.feedstock_)

        self.ui.pushButton_18.clicked.connect(self.start_date)
        self.ui.pushButton_19.clicked.connect(self.end_date)

        self.ui.comboBox.activated.connect(self.diurnaEspecial)
        self.ui.pushButton_23.clicked.connect(self.inventory_charts)
        self.ui.pushButton_6.clicked.connect(self.report)
        self.ui.pushButton_5.clicked.connect(self.youtube)

        self.ui.pushButton_25.clicked.connect(lambda: self.addRow(arg3))
        self.ui.pushButton_26.clicked.connect(lambda: self.removeRow(arg3))
        self.ui.pushButton_27.clicked.connect(self.pronostico)

        self.ui.pushButton_24.clicked.connect(self.banner)




        # Calendar
        from datetime import datetime
        month = datetime.now().month
        current_day = datetime.now().day
        year = datetime.now().year

        self.ui.calendarWidget.setSelectedDate(QDate(year, month, current_day))

        self.show()

    def browsefiles(self):  # ----------------------------------------------------------------------------
        filename = QFileDialog.getOpenFileName()
        path = filename[0]

        # Fetching data--------------

        df = pd.read_excel(path)

        X = df.iloc[:, :-1].values
        y = df.iloc[:, -1].values

        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

        # Training the Polynomial Regression model on the whole dataset
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import PolynomialFeatures

        max_poly_score = 0
        for degree in range(2, 5):

            poly_reg = PolynomialFeatures(degree=degree)
            x_poly = poly_reg.fit_transform(X_train)

            regressor = LinearRegression()
            regressor.fit(x_poly, y_train)

            # Predicting the Test set results

            y_pred = regressor.predict(poly_reg.transform(X_test))

            poly_score = r2_score(y_test, y_pred)
            if poly_score > max_poly_score:
                max_poly_score = poly_score
                degree = degree

        # Predicting the Test set results

        arr = np.arange(len(y) + 1, len(y) + 7, 1)

        self.predictions = regressor.predict(poly_reg.transform(np.reshape(arr, (-1, 1))))
        y_pred = regressor.predict(poly_reg.transform(X_test))


        np.set_printoptions(precision=2)

        # score, x_axis, y_axis and instercept-------------------------------------

        score = r2_score(y_test, y_pred)
        intercept = regressor.intercept_

        x_axis = np.arange(0, len(X), 0.1)

        coef = regressor.coef_.tolist()

        y_axis = []
        response = intercept
        for coef_in in coef:
            response += coef[coef.index(coef_in)] * x_axis ** coef.index(coef_in)
        y_axis.append(response)

        y_axis = [value for value in y_axis]
        Y_axis = y_axis[0].tolist()

        # Creating Chart--------------------------
        y_values = y.tolist()
        x_values = (X.flatten()).tolist()

        series = QtCharts.QLineSeries()
        series2 = QtCharts.QScatterSeries()

        for (x, y) in zip(x_axis, Y_axis):
            series.append(x, y)
        for (x, y) in zip(x_values, y_values):
            series2.append(x, y)

        chart = QtCharts.QChart()

        chart.addSeries(series)
        chart.addSeries(series2)

        chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)

        chart.setTitle(f"Regresión Polinomial de grado {degree} ")

        chart.createDefaultAxes()

        chart.legend().hide()
        chart.setBackgroundVisible(visible=False)

        self.ui.chart_view = QtCharts.QChartView(chart)
        self.ui.chart_view.setRenderHint(QPainter.Antialiasing)
        self.ui.chart_view.chart().setTheme(QtCharts.QChart.ChartThemeDark)

        self.ui.chart_view.setMinimumSize(QSize(0, 300))
        self.ui.gridLayout_chart.addWidget(self.ui.chart_view)
        self.ui.chart_view.setStyleSheet(u"background-color: transparent")
        series2.setColor(QtGui.QColor("#66CDAA"))
        series2.setBorderColor(QtGui.QColor(None))
        series.setColor(QtGui.QColor("white"))

        self.create_donuts(max_poly_score)

        # TODO Creating the bar chart Predictions----------------------------------------------------------
        self.barSeries = QtCharts.QBarSeries()
        self.predictions_poly = list(np.around(np.array(self.predictions)))
        print(self.predictions)
        print(self.predictions_poly)

        for i in range(0, 6):
            self.set = QtCharts.QBarSet(str(self.predictions_poly[i]))
            self.set.append(self.predictions_poly[i])
            self.barSeries.append(self.set)

        self.chart = QtCharts.QChart()
        self.chart.addSeries(self.barSeries)

        self.axisY = QtCharts.QValueAxis()
        self.chart.setAxisY(self.axisY, self.barSeries)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignLeft)

        self.chartView = QtCharts.QChartView(self.chart)

        self.chart.setAnimationOptions(QtCharts.QChart.AllAnimations)
        self.chart.setBackgroundVisible(visible=False)
        self.chart.setTitle('Predictions for the Next 6 months')

        self.chartView.chart().setTheme(QtCharts.QChart.ChartThemeDark)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        sizePolicy.setHeightForWidth(self.chartView.sizePolicy().hasHeightForWidth())
        self.chartView.setSizePolicy(sizePolicy)
        self.chartView.setMinimumSize(QSize(0, 300))
        self.ui.gridLayout.addWidget(self.chartView, 0, 0, 0, 0)
        self.ui.frame_22.setStyleSheet(u"background-color: transparent")

    def create_donuts(self, score):

        imp = (1 - score).round(2)
        pre = score.round(2)

        series_donut = QtCharts.QPieSeries()
        series_donut.setHoleSize(0.45)

        series_donut.append(f"Precision {pre * 100}%", pre * 100)
        series_donut.append(f'Imprecision {imp * 100}%', imp * 100)
        series_donut.setPieSize(100)

        chart_donut = QtCharts.QChart()
        chart_donut.legend().setAlignment(Qt.AlignLeft)

        chart_donut.addSeries(series_donut)

        chart_donut.setAnimationOptions(QtCharts.QChart.SeriesAnimations)
        chart_donut.setTitle("Precision Model (R^2)")
        chart_donut.setTheme(QtCharts.QChart.ChartThemeDark)
        chart_donut.setBackgroundVisible(visible=False)
        self.ui.verticalLayout_8.setStretch(2, 3)

        self.ui.chartview_donut = QtCharts.QChartView(chart_donut)
        self.ui.chartview_donut.setRenderHint(QPainter.Antialiasing)

        self.ui.gridLayout_2.addWidget(self.ui.chartview_donut)
        self.ui.frame_23.setStyleSheet(u"background-color: transparent")

    def pronostico(self):

        rowCount = self.ui.tableWidget_4.rowCount()
        columnCount = self.ui.tableWidget_4.columnCount()
        self.predictions_poly = []


        for row in range(rowCount):
            for column in range(columnCount):
                headertext = self.ui.tableWidget_4.horizontalHeaderItem(column).text()
                if 'Pronostico' == headertext:

                    pronost = self.ui.tableWidget_4.item(row, column).text()
                    self.predictions_poly.append(int(pronost))


        print(self.predictions_poly)


    def workforce(self):

        rowCount = self.ui.tableWidget_2.rowCount()
        columnCount = self.ui.tableWidget_2.columnCount()
        workforce_data = {}
        col1 = 'Puesto'
        col2 = 'Cantidad'
        col3 = 'Salario'

        for row in range(rowCount):
            for column in range(columnCount):
                headertext = self.ui.tableWidget_2.horizontalHeaderItem(column).text()
                if col1 == headertext:
                    workforce_data[row] = {}
                    workforce_data[row][col1] = self.ui.tableWidget_2.item(row, column).text()
                elif col2 == headertext:
                    workforce_data[row][col2] = self.ui.tableWidget_2.item(row, column).text()
                elif col3 == headertext:
                    workforce_data[row][col3] = self.ui.tableWidget_2.item(row, column).text()

        subtotal = [float(data['Cantidad']) * float(data['Salario']) for data in workforce_data.values()]

        total = 0
        prestaciones = float(self.ui.lineEdit_2.text())
        for value in subtotal:
            total += round(value)
        self.hora_normal = round(total / 30 / 8,2) * prestaciones
        self.hora_extra = round(self.hora_normal * 1.5,2)

        self.barSeries = QtCharts.QBarSeries()

        self.set2 = QtCharts.QBarSet('Hora Normal')
        self.set3 = QtCharts.QBarSet('Hora Extra')

        self.set2.append(self.hora_normal)
        self.set3.append(self.hora_extra)

        self.barSeries.append(self.set2)
        self.barSeries.append(self.set3)

        self.barSeries.setLabelsVisible(True)
        # series.setLabelsPrecision(2)
        self.barSeries.setLabelsFormat("@value Q")
        self.barSeries.setLabelsPosition(QtCharts.QAbstractBarSeries.LabelsCenter)

        self.chart = QtCharts.QChart()
        self.chart.addSeries(self.barSeries)

        self.axisY = QtCharts.QValueAxis()
        self.chart.setAxisY(self.axisY, self.barSeries)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignLeft)

        self.chartView = QtCharts.QChartView(self.chart)

        self.chart.setAnimationOptions(QtCharts.QChart.AllAnimations)
        self.chart.setBackgroundVisible(visible=False)
        self.chart.setTitle('Mano de Obra por hora')

        self.chartView.chart().setTheme(QtCharts.QChart.ChartThemeDark)

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chartView.sizePolicy().hasHeightForWidth())
        self.chartView.setSizePolicy(sizePolicy)
        self.chartView.setMinimumSize(QSize(0, 300))
        self.ui.verticalLayout_18.addWidget(self.chartView)
        self.ui.frame_31.setStyleSheet(u"background-color: transparent")

    def feedstock_(self):
        self.rowCount = self.ui.tableWidget.rowCount()
        self.columnCount = self.ui.tableWidget.columnCount()
        self.feedstock = {}
        col1 = 'Material'
        col2 = 'Cantidad/Batch'
        col3 = 'Costo Q/u'

        materials = []

        for row in range(self.rowCount):
            for column in range(self.columnCount):
                headertext = self.ui.tableWidget.horizontalHeaderItem(column).text()
                if col1 == headertext:
                    self.feedstock[row] = {}
                    self.feedstock[row][col1] = self.ui.tableWidget.item(row, column).text()
                    materials.append(self.feedstock[row][col1])
                elif col2 == headertext:
                    self.feedstock[row][col2] = self.ui.tableWidget.item(row, column).text()
                elif col3 == headertext:
                    self.feedstock[row][col3] = self.ui.tableWidget.item(row, column).text()


        subtotal = [float(data['Cantidad/Batch']) * float(data['Costo Q/u']) for data in self.feedstock.values()]
        total_por_material = []
        batch = float(1 / int(self.ui.lineEdit.text()))
        for value in subtotal:
            total = round(value * batch,2)
            total_por_material.append(total)

        total_unidad = 0
        for costo in total_por_material:
            total_unidad += costo

        self.ritmo_produccion = int(self.ui.lineEdit_4.text())

        self.costo_hora = round(total_unidad * self.ritmo_produccion)



        self.ui.label_16.setText(str(f'Q. {round(total_unidad,2)}'))
        self.ui.label_18.setText(str(f'Q. {self.costo_hora}'))

        # Creating Pie Chart----------------------------

        series = QtCharts.QPieSeries()
        series.setLabelsVisible(visible=True)

        for material, costo in zip(materials, total_por_material):
            series.append(str(material), costo)

        chart_donut = QtCharts.QChart()
        chart_donut.legend().setAlignment(Qt.AlignBottom)

        chart_donut.addSeries(series)

        chart_donut.setAnimationOptions(QtCharts.QChart.SeriesAnimations)
        chart_donut.setTitle("Costo de material por unidad")
        chart_donut.setTheme(QtCharts.QChart.ChartThemeDark)
        chart_donut.setBackgroundVisible(visible=False)

        self.ui.chartview_donut = QtCharts.QChartView(chart_donut)
        self.ui.chartview_donut.setRenderHint(QPainter.Antialiasing)

        self.ui.gridLayout_6.addWidget(self.ui.chartview_donut)
        self.ui.frame_36.setStyleSheet(u"background-color: transparent")

        self.summary()
        self.inventario()

    def summary(self):

        self.barSeries = QtCharts.QBarSeries()

        self.set2 = QtCharts.QBarSet('Hora Normal')
        self.set3 = QtCharts.QBarSet('Hora Extra')

        self.set2.append(self.hora_normal + self.costo_hora)
        self.set3.append(self.hora_extra + self.costo_hora)

        self.barSeries.append(self.set2)
        self.barSeries.append(self.set3)

        self.barSeries.setLabelsVisible(True)
        # series.setLabelsPrecision(2)
        self.barSeries.setLabelsFormat("@value Q")
        self.barSeries.setLabelsPosition(QtCharts.QAbstractBarSeries.LabelsCenter)

        self.chart = QtCharts.QChart()
        self.chart.addSeries(self.barSeries)

        self.axisY = QtCharts.QValueAxis()
        self.chart.setAxisY(self.axisY, self.barSeries)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignLeft)

        self.chartView = QtCharts.QChartView(self.chart)

        self.chart.setAnimationOptions(QtCharts.QChart.AllAnimations)
        self.chart.setBackgroundVisible(visible=False)

        self.chartView.chart().setTheme(QtCharts.QChart.ChartThemeDark)

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chartView.sizePolicy().hasHeightForWidth())
        self.chartView.setSizePolicy(sizePolicy)
        self.chartView.setMinimumSize(QSize(0, 300))
        self.ui.verticalLayout_23.addWidget(self.chartView)
        self.ui.frame_40.setStyleSheet(u"background-color: transparent")

        # Requerimiento de Produccion-------------------------
        predict = self.predictions_poly

        self.barSeriess = QtCharts.QBarSeries()
        self.requerido = []

        for value in predict:

            req = value * (1 / self.ritmo_produccion)
            self.requerido.append(req)

            self.sett = QtCharts.QBarSet(str(predict.index(value) + 1))
            self.sett.append(round(req))
            self.barSeriess.append(self.sett)

        self.barSeriess.setLabelsVisible(True)
        # series.setLabelsPrecision(2)
        self.barSeriess.setLabelsFormat("@value hr")
        self.barSeriess.setLabelsPosition(QtCharts.QAbstractBarSeries.LabelsCenter)

        self.chart = QtCharts.QChart()
        self.chart.addSeries(self.barSeriess)

        self.axisY = QtCharts.QValueAxis()
        self.chart.setAxisY(self.axisY, self.barSeriess)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignLeft)

        self.chartView = QtCharts.QChartView(self.chart)

        self.chart.setAnimationOptions(QtCharts.QChart.AllAnimations)
        self.chart.setBackgroundVisible(visible=False)
        self.chart.setTitle('Requerimiento de horas por mes')

        self.chartView.chart().setTheme(QtCharts.QChart.ChartThemeDark)

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chartView.sizePolicy().hasHeightForWidth())
        self.chartView.setSizePolicy(sizePolicy)
        self.chartView.setMinimumSize(QSize(0, 300))
        self.ui.gridLayout_5.addWidget(self.chartView)
        self.ui.frame_41.setStyleSheet(u"background-color: transparent")

    def start_date(self):

        self.ui.label_23.setText(self.ui.calendarWidget.selectedDate().toString())
        self.day_i = self.ui.calendarWidget.selectedDate().day()
        self.month_i = self.ui.calendarWidget.selectedDate().month()
        self.year_i = self.ui.calendarWidget.selectedDate().year()

    def end_date(self):
        self.ui.label_24.setText(self.ui.calendarWidget.selectedDate().toString())
        self.day_f = self.ui.calendarWidget.selectedDate().day()
        self.month_f = self.ui.calendarWidget.selectedDate().month()
        self.year_f = self.ui.calendarWidget.selectedDate().year()

        self.time_available()

    def time_available(self):
        from datetime import date, datetime

        d_i = date(self.year_i, self.month_i, self.day_i)
        d_f = date(self.year_f, self.month_f, self.day_f)

        year = datetime.now().year


        sab = 0
        lun_vie = 0


        horas_mes = {}
        feriados = [f'{year}-01-01',f'{year}-04-01',f'{year}-04-02',f'{year}-05-01',f'{year}-05-01',
                    f'{year}-06-30',f'{year}-09-15',f'{year}-10-20',f'{year}-11-01',f'{year}-12-24',f'{year}-12-25',
                    f'{year}-12-31','2022-04-14','2022-04-15','2022-04-16']

        if self.ui.comboBox.currentText() == 'Jornada Diurna':

            for d_ord in range(d_i.toordinal(), d_f.toordinal()+1):
                d = date.fromordinal(d_ord)





                if not d.strftime("%B") in horas_mes:

                    horas_mes[d.strftime("%B")] = {}

                    for mes in horas_mes:
                        if mes == d.strftime("%B"):
                          if d.strftime("%A") != 'Saturday' and d.strftime("%A") != 'Sunday' and str(d) not in feriados :

                                  lun_vie += 1
                                  horas_mes[mes]['lun-vie'] = lun_vie

                          elif  d.strftime("%A") == 'Saturday' and str(d) not in feriados :
                                 sab += 1
                                 horas_mes[mes]['sab'] = sab


                        else:
                            lun_vie= 0
                            sab=0
                else:
                    for mes in horas_mes:
                        if mes == d.strftime("%B"):
                          if d.strftime("%A") != 'Saturday' and d.strftime("%A") != 'Sunday'and str(d) not in feriados :
                                  lun_vie += 1
                                  horas_mes[mes]['lun-vie'] = lun_vie
                          elif  d.strftime("%A") == 'Saturday' and str(d) not in feriados :
                                 sab += 1
                                 horas_mes[mes]['sab'] = sab


        #Adding normal and extras hours to the dictionary------
            months = []
            for month in horas_mes:
                horas_mes[month]['norm'] = horas_mes[month]['lun-vie']*8 + horas_mes[month]['sab']*4
                horas_mes[month]['extras'] = horas_mes[month]['lun-vie'] * 4 + horas_mes[month]['sab'] * 8
                months.append(month)
            self.tiempo_disp = horas_mes
            print(self.tiempo_disp)


        #Displaying Chart----------------------------------------------------------

            h_normal = QtCharts.QBarSet('Horas Normales')
            h_extra = QtCharts.QBarSet('Horas Extras')
            for month in horas_mes:


                h_normal.append(horas_mes[month]['norm'])
                h_extra.append(horas_mes[month]['extras'])

            self.series_aval = QtCharts.QHorizontalBarSeries()
            self.series_aval .append(h_normal)
            self.series_aval .append(h_extra)

            self.chart = QtCharts.QChart()
            self.chart.addSeries(self.series_aval)
            self.chart.setTitle('Horas por mes')

            self.chart.setAnimationOptions(QtCharts.QChart.AllAnimations)

            self.axisY = QtCharts.QBarCategoryAxis()
            self.axisY.append(months)
            self.chart.addAxis(self.axisY, Qt.AlignLeft)
            self.series_aval.attachAxis(self.axisY)

            self.axisX = QtCharts.QValueAxis()
            self.chart.addAxis(self.axisX, Qt.AlignBottom)
            self.series_aval.attachAxis(self.axisX)

            self.axisX.applyNiceNumbers()

            self.series_aval.setLabelsVisible(True)

            self.series_aval.setLabelsFormat("@value hrs ")
            # self.series.setLabelsPosition(QtCharts.QAbstractBarSeries.labelsPosition)

            self.chart.legend().setVisible(True)
            self.chart.legend().setAlignment(Qt.AlignBottom)
            self.chart.setBackgroundVisible(visible=False)



            self.chartView = QtCharts.QChartView(self.chart)
            self.chartView.update()
            self.chartView.chart().setTheme(QtCharts.QChart.ChartThemeDark)



            self.ui.verticalLayout_25.addWidget(self.chartView)
            self.ui.frame_46.setStyleSheet(u"background-color: transparent")

    def diurnaEspecial(self):

        from datetime import date, datetime


        if self.ui.comboBox.currentText() == 'Jornada Diurna Especial':

            d_i = date(self.year_i, self.month_i, self.day_i)
            d_f = date(self.year_f, self.month_f, self.day_f)

            year = datetime.now().year

            vie = 0
            lun_jue = 0

            horas_mes = {}
            feriados = [f'{year}-01-01', f'{year}-04-01', f'{year}-04-02', f'{year}-05-01', f'{year}-05-01',
                        f'{year}-06-30', f'{year}-09-15', f'{year}-10-20', f'{year}-11-01', f'{year}-12-24',
                        f'{year}-12-25',
                        f'{year}-12-31', '2022-04-14', '2022-04-15', '2022-04-16']

            if self.ui.comboBox.currentText() == 'Jornada Diurna Especial':

                for d_ord in range(d_i.toordinal(), d_f.toordinal() + 1):
                    d = date.fromordinal(d_ord)

                    if not d.strftime("%B") in horas_mes:

                        horas_mes[d.strftime("%B")] = {}

                        for mes in horas_mes:
                            if mes == d.strftime("%B"):
                                if d.strftime("%A") != 'Saturday' and d.strftime("%A") != 'Sunday' and str(
                                        d) not in feriados and d.strftime("%A") != 'Friday':

                                    lun_jue += 1
                                    horas_mes[mes]['lun-jue'] = lun_jue

                                elif d.strftime("%A") == 'Friday' and str(d) not in feriados:
                                    vie += 1
                                    horas_mes[mes]['vie'] = vie


                            else:
                                lun_jue = 0
                                vie = 0
                    else:
                        for mes in horas_mes:
                            if mes == d.strftime("%B"):
                                if d.strftime("%A") != 'Saturday' and d.strftime("%A") != 'Sunday' and str(
                                        d) not in feriados and d.strftime("%A") != 'Friday':
                                    lun_jue += 1
                                    horas_mes[mes]['lun-jue'] = lun_jue
                                elif d.strftime("%A") == 'Friday' and str(d) not in feriados:
                                    vie += 1
                                    horas_mes[mes]['vie'] = vie


                # Adding normal and extras hours to the dictionary------
            months = []
            for month in horas_mes:
                horas_mes[month]['norm'] = horas_mes[month]['lun-jue'] * 9 + horas_mes[month]['vie'] * 8
                horas_mes[month]['extras'] = horas_mes[month]['lun-jue'] * 3 + horas_mes[month]['vie'] * 4
                months.append(month)

            # Displaying Chart----------------------------------------------------------

            h_normal = QtCharts.QBarSet('Horas Normales')
            h_extra = QtCharts.QBarSet('Horas Extras')
            for month in horas_mes:
                h_normal.append(horas_mes[month]['norm'])
                h_extra.append(horas_mes[month]['extras'])

            self.series_aval = QtCharts.QHorizontalBarSeries()
            self.series_aval.append(h_normal)
            self.series_aval.append(h_extra)

            self.chart = QtCharts.QChart()
            self.chart.addSeries(self.series_aval)
            self.chart.setTitle('Horas por mes')

            self.chart.setAnimationOptions(QtCharts.QChart.AllAnimations)

            self.axisY = QtCharts.QBarCategoryAxis()
            self.axisY.append(months)
            self.chart.addAxis(self.axisY, Qt.AlignLeft)
            self.series_aval.attachAxis(self.axisY)

            self.axisX = QtCharts.QValueAxis()
            self.chart.addAxis(self.axisX, Qt.AlignBottom)
            self.series_aval.attachAxis(self.axisX)

            self.axisX.applyNiceNumbers()

            self.series_aval.setLabelsVisible(True)

            self.series_aval.setLabelsFormat("@value hrs ")
            # self.series.setLabelsPosition(QtCharts.QAbstractBarSeries.labelsPosition)

            self.chart.legend().setVisible(True)
            self.chart.legend().setAlignment(Qt.AlignBottom)
            self.chart.setBackgroundVisible(visible=False)
            self.chartView.deleteLater()


            self.chartView = QtCharts.QChartView(self.chart)
            self.chartView.update()
            self.chartView.chart().setTheme(QtCharts.QChart.ChartThemeDark)


            self.ui.verticalLayout_25.addWidget(self.chartView)
            self.ui.frame_46.setStyleSheet(u"background-color: transparent")
        else:
            self.chartView.deleteLater()
            self.time_available()


    def addRow(self, arg):
        if arg == 1:
            rowCount = self.ui.tableWidget_2.rowCount()
            self.ui.tableWidget_2.insertRow(rowCount)

        elif arg == 2:
            rowCount = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(rowCount)

        elif arg == 3:
            rowCount = self.ui.tableWidget_4.rowCount()
            self.ui.tableWidget_4.insertRow(rowCount)

    def removeRow(self, arg):
        if arg == 1:
            if self.ui.tableWidget_2.rowCount() > 0:
                self.ui.tableWidget_2.removeRow(self.ui.tableWidget_2.rowCount() - 1)
        elif arg == 2:
            if self.ui.tableWidget.rowCount() > 0:
                self.ui.tableWidget.removeRow(self.ui.tableWidget.rowCount() - 1)
        elif arg ==3:
            if self.ui.tableWidget_4.rowCount() > 0:
                self.ui.tableWidget_4.removeRow(self.ui.tableWidget_4.rowCount() - 1)

            self.ui.tableWidget_2.horizontalHeader().setStretchLastSection(True)
            self.ui.tableWidget_2.horizontalHeader().setSectionResizeMode(
                QHeaderView.Stretch)

    def next_page(self):
        self.ui.stackedWidget_2.setCurrentIndex((self.ui.stackedWidget_2.currentIndex() + 1))

    def prev_page(self):
        self.ui.stackedWidget_2.setCurrentIndex((self.ui.stackedWidget_2.currentIndex() - 1))

    def inventario(self):
        inventario = self.ui.tableWidget_3
        inventario.setRowCount(self.rowCount)
        for row in range(self.rowCount):
         inventario.setItem(row,0,QTableWidgetItem(self.ui.tableWidget.item(row, 0).text()))

        self.predictions_2 = self.predictions_poly
        self.total_predict = 0
        for predict in self.predictions_2:
            self.total_predict+=predict

        self.material = []
        self.tot_material = []

        for mat in self.feedstock.values():

            self.material.append(mat['Material'])
            self.tot_material.append(float(mat['Cantidad/Batch'])*self.total_predict/int(self.ui.lineEdit.text()))

    #TODO -------- CREAR GRAFICA DE BARRAS AQUI

        self.barSeriess2 = QtCharts.QBarSeries()

        for material, total in zip(self.material,self.tot_material):


            self.sett = QtCharts.QBarSet(material)
            self.sett.append(total)
            self.barSeriess2.append(self.sett)

        self.barSeriess2.setLabelsVisible(True)
        # series.setLabelsPrecision(2)
        self.barSeriess2.setLabelsFormat("@value u")
        self.barSeriess2.setLabelsPosition(QtCharts.QAbstractBarSeries.LabelsOutsideEnd)

        self.chart = QtCharts.QChart()
        self.chart.addSeries(self.barSeriess2)

        self.axisY = QtCharts.QValueAxis()
        self.chart.setAxisY(self.axisY, self.barSeriess2)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignLeft)

        self.chartView = QtCharts.QChartView(self.chart)

        self.chart.setAnimationOptions(QtCharts.QChart.AllAnimations)
        self.chart.setBackgroundVisible(visible=False)
        self.chart.setTitle('Total por material')

        self.chartView.chart().setTheme(QtCharts.QChart.ChartThemeDark)

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chartView.sizePolicy().hasHeightForWidth())
        self.chartView.setSizePolicy(sizePolicy)
        self.chartView.setMinimumSize(QSize(0, 300))
        self.ui.gridLayout_7.addWidget(self.chartView)
        self.ui.tabWidget.setStyleSheet(u"background-color: transparent")


    def inventory_charts(self):
        index_total = 0

        for row in range(self.ui.tableWidget_3.rowCount()):

            # series =  QtCharts.QLineSeries()

            for column in range(self.ui.tableWidget_3.columnCount()):


                headertext = self.ui.tableWidget_3.horizontalHeaderItem(column).text()
                plannificado = self.tot_material[index_total]


                if headertext == 'Existencia':
                    exist1 = float(self.ui.tableWidget_3.item(row,column).text())

                elif headertext == 'T. Entrega':
                    Rn = float(self.ui.tableWidget_3.item(row, column).text())

                elif headertext == 'T. Tardío':
                    tardio = float(self.ui.tableWidget_3.item(row, column).text())
                    Rs = tardio-float(self.ui.tableWidget_3.item(row, 2).text())

                elif headertext == 'N max':
                    Nmax = float(self.ui.tableWidget_3.item(row, column).text())




            ciclo = len(self.predictions_2)
            Ss = round((plannificado/ciclo)*Rs,2)
            Nr = round((plannificado/ciclo)*Rn,2)
            nMax = round((plannificado/ciclo)*Nmax,2)
            Opt = round((2*Ss)+Nr,2)
            exist2 = round(Opt + Ss,2)
            LTC1 = (exist1/plannificado)*ciclo
            LTC2 = (exist2/plannificado)*ciclo
            x1 = LTC1*(exist1-Nr)/(exist1-Ss)
            x2 = LTC2*(exist2-Nr)/(exist2-Ss)

            series = QtCharts.QLineSeries()
            series.append(0,exist1)
            series.append(LTC1,Ss)
            series.append(LTC1,exist2)
            series.append(LTC1+LTC2,Ss)
            series.append(LTC1+LTC2,exist2)
            series.append(LTC1 + (2*LTC2), Ss)
            series.setName('Inventario')

            nmax_series = QtCharts.QLineSeries()
            nmax_series.append(0,nMax)
            nmax_series.append(LTC1+2*LTC2, nMax)
            nmax_series.setName('Nmax')


            exist2_series = QtCharts.QLineSeries()
            exist2_series.append(0,exist2)
            exist2_series.append(LTC1+2*LTC2, exist2)
            exist2_series.setName('Existencia2')

            Nr_series = QtCharts.QLineSeries()
            Nr_series.append(0,Nr)
            Nr_series.append(LTC1+2*LTC2, Nr)
            Nr_series.setColor(QtGui.QColor("yellow"))
            Nr_series.setName('NR')

            Ss_series = QtCharts.QLineSeries()
            Ss_series.append(0,Ss)
            Ss_series.append(LTC1+2*LTC2, Ss)
            Ss_series.setName('Ss')



            chart = QtCharts.QChart()
            chart.addSeries(series)
            chart.addSeries(nmax_series)
            chart.addSeries(exist2_series)
            chart.addSeries(Nr_series)
            chart.addSeries(Ss_series)


            chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)

            chart.setTitle(f"{self.material[index_total]}: \nNmax: {nMax}, Existencia 2: {exist2},NR: {Nr}, "
                           f"SS: {Ss}, \nX1: {round(x1,2)}, X2: {round(x2,2)}")
            index_total += 1

            chart.createDefaultAxes()



            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignBottom)
            chart.setBackgroundVisible(visible=False)

            self.ui.chart_view = QtCharts.QChartView(chart)
            self.ui.chart_view.setRenderHint(QPainter.Antialiasing)
            self.ui.chart_view.chart().setTheme(QtCharts.QChart.ChartThemeDark)

            self.ui.chart_view.setMinimumSize(QSize(0, 300))
            self.ui.verticalLayout_28.addWidget(self.ui.chart_view)
            self.ui.chart_view.setStyleSheet(u"background-color: transparent")


    def report(self):
        import anvil.server

        #### TODO: Replace this uplink key with the key for your own app ####
        anvil.server.connect("WBD6TS6XUWAG46XQBBZBKP34-6WKXLNNRYBZWOQI5")

        import anvil.pdf
        import anvil.media


        total_por_material = []
        items = []

        dict = {}
        dict_item = {}
        id = 0
        for mater , total in zip(self.material,self.tot_material):

            if id == self.material.index(mater):

                dict['id'] = id
                dict['title'] = mater
                dict['data_key'] = mater.lower()

                dict_item[f'{mater.lower()}'] = total


                dict_copy = dict.copy()
                total_por_material.append(dict_copy)

                dict_item_copy = dict_item.copy()
                dict = {}

            id += 1

        items.append(dict_item_copy)

        #Tiempo requerido resumen--------------------------
        requerido = []
        dict_tiempo = {}

        items2 = []
        dict_itmes2 = {}

        id_2 = 0
        for hr in  self.requerido:
          dict_tiempo['id']= id_2
          dict_tiempo['title']= f'Mes {id_2+1}'
          dict_tiempo['data_key']=  f'Mes {id_2+1}'

          dict_itmes2[ f'Mes {id_2+1}'] = round(hr)

          dict_tiempo_copy = dict_tiempo.copy()
          requerido.append(dict_tiempo_copy)

          dict_itmes2_copy = dict_itmes2.copy()

          dict_tiempo = {}
          id_2 += 1
        items2.append(dict_itmes2_copy)
        print(items2)

        #ploting bar chart of time available------------------------------
        available = []
        aval = {}
        for month in self.tiempo_disp:
            aval['Mes'] = month
            aval['HN'] = self.tiempo_disp[month]['norm']
            aval['HE'] = self.tiempo_disp[month]['extras']

            aval_copy = aval.copy()
            available.append(aval_copy)
            aval = {}

        normal = self.hora_normal + self.costo_hora
        extra = self.hora_extra + self.costo_hora

        total = self.total_predict

        pdf = anvil.pdf.render_form("ReportForm", total, total_por_material, items,requerido,items2,available,normal,extra)
        anvil.media.write_to_file(pdf, "report.pdf")

    def youtube(self):
        webbrowser.open('https://www.youtube.com/watch?v=9X83dqZd5uU')

    def banner(self):
        webbrowser.open('https://www.screencast.com/t/qfJ5D3pCmjWK')


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
