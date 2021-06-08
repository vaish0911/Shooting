# Repose data widgets
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5 import QtGui
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QTimer, QDate, QTime, Qt, QDateTime
from pyqtgraph import PlotWidget, PlotDataItem
from datetime import datetime, date, time, timedelta
import pyqtgraph as pg
import pytz
from pyqtgraph import AxisItem
import json
import sys  # We need sys so that we can pass argv to QApplication
import numpy as np
import os
from random import randint
from utils import TimeAxisItem, timestamp
from time import mktime
import calendar
import tqdm
import csv

#  AuraHealthcare Toolkit
from hrv_analysis_mod import remove_outliers, remove_ectopic_beats, interpolate_nan_values
from hrv_analysis_mod import get_time_domain_features, get_frequency_domain_features, _create_interpolation_time, _create_time_info

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):

        super(MainWindow, self).__init__(*args, **kwargs)
        QtWidgets.QMainWindow.__init__(self)
        #QMainWindow.__init__(self, parent)
        self.graphWidget = pg.PlotWidget(title="Heart Rate Plot", labels={'left': 'Reading / mV'},
                      axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        
        self.time_iter = 0 
        self.data_line = pg.PlotDataItem()
        self.data_line1 = pg.PlotDataItem()
        self.timer = QtCore.QTimer()
        self.setCentralWidget(self.graphWidget)

        Subject_name = 'Sricharan'
        
        # save the paths used for importing the database and the path for
        or_path = r'E:/Stress-HRV/Shooting_based_stress/Datasets/Inhouse_datasets/'
        
        path = or_path + Subject_name + '/'

        #Read all records from a text file given in mitdb database folder and then store it in numpy array.
        RECORDS = np.genfromtxt(path +'JSON_RECORDS.txt',delimiter=',',dtype=None, encoding=None)

        # Open the required json file
        filedata = os.path.join(path,str(RECORDS))

        with open(filedata, 'r') as infile:
            data = json.load(infile)

            # HR Tick values
            dkeys = data['captured_data']['hr']['ticks']
            dkeys = [float(dkeys[i]) for i in range(len(dkeys))]
            dkeys = [int(dkeys[i]) for i in range(len(dkeys))]

            # Obtain Starting Time in string format
            time_in_string = data['Start_date_time']
            
            
            print('Start Time:', time_in_string)

    

        # HR Tick values
        dkeys = data['captured_data']['hr']['ticks']
        dkeys = [float(dkeys[i]) for i in range(len(dkeys))]
        dkeys = [int(dkeys[i]) for i in range(len(dkeys))]


        SC_data = list(data['captured_data']['act']['step count'])
        SC_ticks = data['captured_data']['act']['ticks']
        self.stepcount = np.array(SC_data)
        SC_ticks = np.asarray([float(SC_ticks[i])/512 for i in range(len(SC_ticks))])
        self.stepcount_times = np.asarray([int(SC_ticks[i]) for i in range(len(SC_ticks))])
        import pdb;pdb.set_trace()

        # Compute RR Interval from Tick values
        rr_int = np.asarray([int( (dkeys[i] - dkeys[i-1]) / 512 * 1000) for i in range(1, len(dkeys))])
        rr_tsc = [int(dkeys[i]) for i in range(1, len(dkeys))]
        rr_int = self.recompute_ticks_rr(rr_int, rr_tsc)
        self.rri_times = _create_time_info(list(rr_int))
        self.rr_times = list(self.rri_times)


        # This remove outliers from signal
        rr_intervals_without_outliers = remove_outliers(rr_intervals = list(rr_int), verbose = False,  
                                                        low_rri = 300, high_rri = 2000)
        # This replace outliers nan values with linear interpolation
        interpolated_rr_intervals = interpolate_nan_values(rr_intervals = rr_intervals_without_outliers,
                                                        interpolation_method ="linear", limit = 100000, limit_direction='both')
         
        nn_intervals_list = remove_ectopic_beats(rr_intervals = interpolated_rr_intervals, method="karlsson", custom_removing_rule= 0.1)
        interpolated_nn_intervals = interpolate_nan_values(rr_intervals=nn_intervals_list,
                                                        interpolation_method ="linear", limit = 100000, limit_direction='both')
        self.interpolated_nn_intervals = np.asarray(interpolated_nn_intervals)
        self.hr = np.divide(60000, self.interpolated_nn_intervals)
        self.timestamps_interpolation = _create_interpolation_time(self.rr_times, 4)
        #nni_interpolation = funct(timestamps_interpolation)
        #heart_rate_list = np.divide(60000, nni_interpolation)
        
        self.timestamp = self.utc_convertor(data['timezone'], time_in_string)
        self.timestamp = np.array(self.timestamp)
        
        
        
        self.interpolate_fs = 4
        self.process_window = 5   ###(5 minute window)
        self.window_size = int(self.interpolate_fs * 60 * self.process_window)
        self.window_slide = 1   ###  slide in minutes
        self.stride_samples = int(self.window_slide * 60 * self.interpolate_fs) ### window_size - overlap_samples)
        self.total_windows = int(self.timestamps_interpolation[-1] * self.interpolate_fs - self.window_size) // int(self.stride_samples) + 1
        self.rri_times_min = np.divide(self.rri_times, 60)
          

        #if self.time_iter == 0:
        #    for k_ in tqdm(range(self.total_windows)):
        
        #        #windowed_nn_intervals = nni_interpolation[stride_samples * k_ : stride_samples * k_ + window_size]
        self.win_data = self.hr [(self.rri_times_min >= self.time_iter * self.window_slide) & (self.rri_times_min < ((self.time_iter * self.window_slide) + self.process_window))]
        self.win_time = self.timestamp[(self.rri_times_min >= self.time_iter * self.window_slide) & (self.rri_times_min < ((self.time_iter * self.window_slide) + self.process_window))]
        
       
        
        
        #self.cursor = self.rri_time[50]
        #self.cursor_x = [self.cursor] *130
        #self.cursor_y = list(range(130))
        #self.update_plot_data

        self.timer.setInterval(2000)
        #import pdb; pdb.set_trace()
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

        #import pdb; pdb.set_trace()

        #hour = [1,2,3,4,5,6,7,8,9,10]
        #temperature = [30,32,34,32,33,31,29,32,35,45]

        
        
        #----------------------------------- set background colour-----------------------------------#
        self.graphWidget.setBackground('w')
        #import pdb; pdb.set_trace()

        ## hex notation
        #self.graphWidget.setBackground('#bbccaa')
        ## RGB  notation
        #self.graphWidget.setBackground((100,50,255))      # RGB each 0-255
        #self.graphWidget.setBackground((100,50,255,25))   # RGBA (A = alpha opacity)
        ## Qtcolor type 
        #self.graphWidget.setBackground(QtGui.QColor(100,50,254,25))



        #-----------------------------------Add Axis Labels-----------------------------------#
        styles = {"color": "#f00", "font-size": "20px"}
        self.graphWidget.setLabel("left", "Heart Rate in bpm", **styles)
        self.graphWidget.setLabel("bottom", "Time", **styles)


        #------------------------------------Add legend-----------------------------------#
        #self.graphWidget.addLegend()

        #------------------------------------Add grid-----------------------------------#
        self.graphWidget.showGrid(x=True, y=True)

        #------------------------------------Set Range-----------------------------------#
        #self.graphWidget.setXRange(0, 12, padding=0)
        #self.graphWidget.setYRange(20, 55, padding=0)

        #-------------------------------------Line Style-----------------------------------#
        pen = pg.mkPen(color=(0, 0, 255), width=5, style=QtCore.Qt.SolidLine)
        pen1 = pg.mkPen(color = (255, 0, 0), width = 5, style =QtCore.Qt.DashLine)

        # ------------------------------------plot data: x, y values-----------------------------------#
      
        x = list(self.win_time)
        y = list(self.win_data)
        self.data_line = self.graphWidget.plot(x, y, pen = pen)
                              #symbol='+', symbolSize=20, symbolBrush=('r'))
        #xformatter = mdates.DateFormatter('%H:%M')
        #xx = np.array(self.cursor_x)
        #yy = np.array(self.cursor_y)
        #self.data_line1 = self.graphWidget.plot(xx, yy, pen = pen1)

        #------------------------------------Add title-----------------------------------#
        #self.graphWidget.setTitle("HEART RATE", color="b", size="15pt")

    def recompute_ticks_rr(self, rr_int, tsc_rr):

        ### Will only factor for no HR if no HR is received for over 20 seconds ###
        rr_in_ms = rr_int
        no_hr_indices = np.where(rr_in_ms > 20000)
        indice_shift = 0
        for i in list(no_hr_indices[0]):
            if i != 0:
                tsc_rr = np.insert(tsc_rr, i + indice_shift , (tsc_rr[i-1 + indice_shift] + 2100))
            tsc_rr = np.insert(tsc_rr, i + 1 + indice_shift , (tsc_rr[i + indice_shift] + 2100))
            tsc_rr = np.insert(tsc_rr, i + 2 + indice_shift , (tsc_rr[i + 1 + indice_shift] + 2100))  
            indice_shift += 3
        rr_in_ms = np.asarray([int( (tsc_rr[i] - tsc_rr[i-1]) / 512 * 1000) for i in range(1, len(tsc_rr))])
        rr_in_ms =  list(np.concatenate((np.zeros(1) ,rr_in_ms)))
        return rr_in_ms     


    #_______________________________________________________Timezones________________________________________________________________#

    def utc_convertor(self, tzone, st_str):

        timezone_offset_to_name_mapping = {
        "UTC": ["Africa/Casablanca", "Africa/El_Aaiun", "America/Danmarkshavn", "Etc/GMT", "Atlantic/Canary",
                "Atlantic/Faeroe", "Atlantic/Madeira", "Europe/Dublin", "Europe/Lisbon", "Europe/Isle_of_Man",
                "Europe/Guernsey", "Europe/Jersey", "Europe/London", "Africa/Abidjan", "Africa/Accra", "Africa/Bamako",
                "Africa/Banjul", "Africa/Bissau", "Africa/Conakry", "Africa/Dakar", "Africa/Freetown", "Africa/Lome",
                "Africa/Monrovia", "Africa/Nouakchott", "Africa/Ouagadougou", "Africa/Sao_Tome", "Atlantic/Reykjavik",
                "Atlantic/St_Helena"],
        "UTC+05:45": ["Asia/Kathmandu"],
        "UTC+01:00": ["Europe/Isle_of_Man", "Europe/Guernsey", "Europe/Jersey", "Europe/London", "Arctic/Longyearbyen",
                      "Europe/Amsterdam", "Europe/Andorra", "Europe/Berlin", "Europe/Busingen", "Europe/Gibraltar",
                      "Europe/Luxembourg", "Europe/Malta", "Europe/Monaco", "Europe/Oslo", "Europe/Rome",
                      "Europe/San_Marino", "Europe/Stockholm", "Europe/Vaduz", "Europe/Vatican", "Europe/Vienna",
                      "Europe/Zurich", "Europe/Belgrade", "Europe/Bratislava", "Europe/Budapest", "Europe/Ljubljana",
                      "Europe/Podgorica", "Europe/Prague", "Europe/Tirane", "Africa/Ceuta", "Europe/Brussels",
                      "Europe/Copenhagen", "Europe/Madrid", "Europe/Paris", "Europe/Sarajevo", "Europe/Skopje",
                      "Europe/Warsaw", "Europe/Zagreb", "Africa/Algiers", "Africa/Bangui", "Africa/Brazzaville",
                      "Africa/Douala", "Africa/Kinshasa", "Africa/Lagos", "Africa/Libreville", "Africa/Luanda",
                      "Africa/Malabo", "Africa/Ndjamena", "Africa/Niamey", "Africa/Porto-Novo", "Africa/Tunis", "Etc/GMT-1",
                      "Africa/Windhoek"],
        "UTC+02:00": ["Asia/Nicosia", "Europe/Athens", "Europe/Bucharest", "Europe/Chisinau", "Asia/Beirut", "Africa/Cairo",
                      "Asia/Damascus", "Asia/Nicosia", "Europe/Athens", "Europe/Bucharest", "Europe/Chisinau",
                      "Europe/Helsinki", "Europe/Kiev", "Europe/Mariehamn", "Europe/Nicosia", "Europe/Riga", "Europe/Sofia",
                      "Europe/Tallinn", "Europe/Uzhgorod", "Europe/Vilnius", "Europe/Zaporozhye", "Africa/Blantyre",
                      "Africa/Bujumbura", "Africa/Gaborone", "Africa/Harare", "Africa/Johannesburg", "Africa/Kigali",
                      "Africa/Lubumbashi", "Africa/Lusaka", "Africa/Maputo", "Africa/Maseru", "Africa/Mbabane", "Etc/GMT-2",
                      "Europe/Helsinki", "Europe/Kiev", "Europe/Mariehamn", "Europe/Riga", "Europe/Sofia", "Europe/Tallinn",
                      "Europe/Uzhgorod", "Europe/Vilnius", "Europe/Zaporozhye", "Asia/Jerusalem", "Africa/Tripoli",
                      "Europe/Kaliningrad"],
        "UTC+03:00": ["Europe/Istanbul", "Asia/Amman", "Asia/Baghdad", "Asia/Aden", "Asia/Bahrain", "Asia/Kuwait",
                      "Asia/Qatar", "Asia/Riyadh", "Africa/Addis_Ababa", "Africa/Asmera", "Africa/Dar_es_Salaam",
                      "Africa/Djibouti", "Africa/Juba", "Africa/Kampala", "Africa/Khartoum", "Africa/Mogadishu",
                      "Africa/Nairobi", "Antarctica/Syowa", "Etc/GMT-3", "Indian/Antananarivo", "Indian/Comoro",
                      "Indian/Mayotte", "Europe/Kirov", "Europe/Moscow", "Europe/Simferopol", "Europe/Volgograd",
                      "Europe/Minsk"],
        "UTC+03:30": ["Asia/Tehran"],
        "UTC+04:00": ["Europe/Astrakhan", "Europe/Samara", "Europe/Ulyanovsk", "Asia/Dubai", "Asia/Muscat", "Etc/GMT-4",
                      "Asia/Baku", "Indian/Mahe", "Indian/Mauritius", "Indian/Reunion", "Asia/Tbilisi", "Asia/Yerevan"],
        "UTC+04:30": ["Asia/Kabul"],
        "UTC+05:00": ["Antarctica/Mawson", "Asia/Aqtau", "Asia/Aqtobe", "Asia/Ashgabat", "Asia/Dushanbe", "Asia/Oral",
                      "Asia/Samarkand", "Asia/Tashkent", "Etc/GMT-5", "Indian/Kerguelen", "Indian/Maldives",
                      "Asia/Yekaterinburg", "Asia/Karachi"],
        "UTC+05:30": ["Asia/Kolkata", "Asia/Colombo"],
        "UTC+06:00": ["Antarctica/Vostok", "Asia/Almaty", "Asia/Bishkek", "Asia/Qyzylorda", "Asia/Urumqi", "Etc/GMT-6",
                      "Indian/Chagos", "Asia/Dhaka", "Asia/Thimphu"],
        "UTC+06:30": ["Asia/Rangoon", "Indian/Cocos"],
        "UTC+07:00": ["Antarctica/Davis", "Asia/Bangkok", "Asia/Hovd", "Asia/Jakarta", "Asia/Phnom_Penh", "Asia/Pontianak",
                      "Asia/Saigon", "Asia/Vientiane", "Etc/GMT-7", "Indian/Christmas", "Asia/Novokuznetsk",
                      "Asia/Novosibirsk", "Asia/Omsk"],
        "UTC+08:00": ["Asia/Hong_Kong", "Asia/Macau", "Asia/Shanghai", "Asia/Krasnoyarsk", "Asia/Brunei",
                      "Asia/Kuala_Lumpur", "Asia/Kuching", "Asia/Makassar", "Asia/Manila", "Asia/Singapore", "Etc/GMT-8",
                      "Antarctica/Casey", "Australia/Perth", "Asia/Taipei", "Asia/Choibalsan", "Asia/Ulaanbaatar",
                      "Asia/Irkutsk"],
        "UTC+09:00": ["Asia/Dili", "Asia/Jayapura", "Asia/Tokyo", "Etc/GMT-9", "Pacific/Palau", "Asia/Pyongyang",
                      "Asia/Seoul", "Asia/Chita", "Asia/Khandyga", "Asia/Yakutsk"],
        "UTC+09:30": ["Australia/Adelaide", "Australia/Broken_Hill", "Australia/Darwin"],
        "UTC+10:00": ["Australia/Brisbane", "Australia/Lindeman", "Australia/Melbourne", "Australia/Sydney",
                      "Antarctica/DumontDUrville", "Etc/GMT-10", "Pacific/Guam", "Pacific/Port_Moresby", "Pacific/Saipan",
                      "Pacific/Truk", "Australia/Currie", "Australia/Hobart"],
        "UTC+11:00": ["Antarctica/Macquarie", "Etc/GMT-11", "Pacific/Efate", "Pacific/Guadalcanal", "Pacific/Kosrae",
                      "Pacific/Noumea", "Pacific/Ponape", "Asia/Sakhalin", "Asia/Ust-Nera", "Asia/Vladivostok"],
        "UTC+12:00": ["Antarctica/McMurdo", "Pacific/Auckland", "Etc/GMT-12", "Pacific/Funafuti", "Pacific/Kwajalein",
                      "Pacific/Majuro", "Pacific/Nauru", "Pacific/Tarawa", "Pacific/Wake", "Pacific/Wallis", "Pacific/Fiji",
                      "Asia/Anadyr", "Asia/Kamchatka", "Asia/Magadan", "Asia/Srednekolymsk", "Asia/Kamchatka"],
        "UTC+13:00": ["Etc/GMT-13", "Pacific/Enderbury", "Pacific/Fakaofo", "Pacific/Tongatapu", "Pacific/Apia"],
        "UTC-01:00": ["America/Scoresbysund", "Atlantic/Azores", "Atlantic/Cape_Verde", "Etc/GMT+1"],
        "UTC-02:00": ["America/Noronha", "Atlantic/South_Georgia", "Etc/GMT+2"],
        "UTC-03:00": ["America/Sao_Paulo", "America/Argentina/La_Rioja", "America/Argentina/Rio_Gallegos",
                      "America/Argentina/Salta", "America/Argentina/San_Juan", "America/Argentina/San_Luis",
                      "America/Argentina/Tucuman", "America/Argentina/Ushuaia", "America/Buenos_Aires", "America/Catamarca",
                      "America/Cordoba", "America/Jujuy", "America/Mendoza", "America/Araguaina", "America/Belem",
                      "America/Cayenne", "America/Fortaleza", "America/Maceio", "America/Paramaribo", "America/Recife",
                      "America/Santarem", "Antarctica/Rothera", "Atlantic/Stanley", "Etc/GMT+3", "America/Godthab",
                      "America/Montevideo", "America/Bahia"],
        "UTC-03:30": ["America/St_Johns"],
        "UTC-04:00": ["America/Asuncion", "America/Glace_Bay", "America/Goose_Bay", "America/Halifax", "America/Moncton",
                      "America/Thule", "Atlantic/Bermuda", "America/Campo_Grande", "America/Cuiaba", "America/Anguilla",
                      "America/Antigua", "America/Aruba", "America/Barbados", "America/Blanc-Sablon", "America/Boa_Vista",
                      "America/Curacao", "America/Dominica", "America/Grand_Turk", "America/Grenada", "America/Guadeloupe",
                      "America/Guyana", "America/Kralendijk", "America/La_Paz", "America/Lower_Princes", "America/Manaus",
                      "America/Marigot", "America/Martinique", "America/Montserrat", "America/Port_of_Spain",
                      "America/Porto_Velho", "America/Puerto_Rico", "America/Santo_Domingo", "America/St_Barthelemy",
                      "America/St_Kitts", "America/St_Lucia", "America/St_Thomas", "America/St_Vincent", "America/Tortola",
                      "Etc/GMT+4", "America/Santiago", "Antarctica/Palmer"],
        "UTC-04:30": ["America/Caracas"],
        "UTC-05:00": ["America/Bogota", "America/Cayman", "America/Coral_Harbour", "America/Eirunepe", "America/Guayaquil",
                      "America/Jamaica", "America/Lima", "America/Panama", "America/Rio_Branco", "Etc/GMT+5",
                      "America/Detroit", "America/Havana", "America/Indiana/Petersburg", "America/Indiana/Vincennes",
                      "America/Indiana/Winamac", "America/Iqaluit", "America/Kentucky/Monticello", "America/Louisville",
                      "America/Montreal", "America/Nassau", "America/New_York", "America/Nipigon", "America/Pangnirtung",
                      "America/Port-au-Prince", "America/Thunder_Bay", "America/Toronto", "EST5EDT",
                      "America/Indiana/Marengo", "America/Indiana/Vevay", "America/Indianapolis"],
        "UTC-06:00": ["America/Belize", "America/Costa_Rica", "America/El_Salvador", "America/Guatemala", "America/Managua",
                      "America/Tegucigalpa", "Etc/GMT+6", "Pacific/Galapagos", "America/Chicago", "America/Indiana/Knox",
                      "America/Indiana/Tell_City", "America/Matamoros", "America/Menominee", "America/North_Dakota/Beulah",
                      "America/North_Dakota/Center", "America/North_Dakota/New_Salem", "America/Rainy_River",
                      "America/Rankin_Inlet", "America/Resolute", "America/Winnipeg", "CST6CDT", "America/Bahia_Banderas",
                      "America/Cancun", "America/Merida", "America/Mexico_City", "America/Monterrey", "America/Regina",
                      "America/Swift_Current"],
        "UTC-07:00": ["America/Dawson", "America/Los_Angeles", "America/Tijuana", "America/Vancouver", "America/Whitehorse",
                      "America/Creston", "America/Dawson_Creek", "America/Hermosillo", "America/Phoenix", "Etc/GMT+7",
                      "America/Chihuahua", "America/Mazatlan", "America/Boise", "America/Cambridge_Bay", "America/Denver",
                      "America/Edmonton", "America/Inuvik", "America/Ojinaga", "America/Yellowknife", "MST7MDT"],
        "UTC-08:00": ["America/Santa_Isabel", "America/Dawson", "America/Los_Angeles", "America/Tijuana",
                      "America/Vancouver", "America/Whitehorse", "PST8PDT"],
        "UTC-09:00": ["America/Anchorage", "America/Juneau", "America/Nome", "America/Sitka", "America/Yakutat"],
        "UTC-10:00": ["Etc/GMT+10", "Pacific/Honolulu", "Pacific/Johnston", "Pacific/Rarotonga", "Pacific/Tahiti"],
        "UTC-11:00": ["Etc/GMT+11", "Pacific/Midway", "Pacific/Niue", "Pacific/Pago_Pago"],
        "UTC-12:00": ["Etc/GMT+12"]
        }

        # Time compute
        start_time_in_str = str(st_str)

        utc_start_time = datetime.strptime(start_time_in_str,"%Y-%m-%dT%H:%M:%SZ") # Extracting the UTC time from the data

        local_tz = pytz.timezone(timezone_offset_to_name_mapping[tzone][0]) # Obtaining the time difference
        local_dt = utc_start_time.replace(tzinfo=pytz.utc).astimezone(local_tz) # Converting the UTC time to Local time
        corrected_time = str(local_tz.normalize(local_dt))

        rr_timestamp = datetime.strptime(corrected_time, "%Y-%m-%d %H:%M:%S%z")
        
        rr_time = [rr_timestamp + timedelta(seconds = i) for i in self.rr_times]
        rri_time = [rr_time.timestamp() for rr_time in rr_time]

        return rri_time
   

    def update_plot_data(self):

        #self.hr = self.hr[1:]  # Remove the first
        #new_Value = randint(500, 1000)
        #self.hr.append(60000/new_Value)  # Add a new random value.

        #self.rr_time = self.rr_time[1:]  # Remove the first y element.
        #self.rr_time.append(self.rr_time[-1] + timedelta(seconds= new_Value/1000))  # Add a new value 1 higher than the last.
        #self.rri_time = [rr_time.timestamp() for rr_time in self.rr_time]
        
        
        
        
        print(self.time_iter+1)
        #windowed_nn_intervals = nni_interpolation[stride_samples * k_ : stride_samples * k_ + window_size]
        self.win_data = self.hr [(self.rri_times_min >= self.time_iter * self.window_slide) & (self.rri_times_min < ((self.time_iter * self.window_slide) + self.process_window))]
        self.win_time = self.timestamp[(self.rri_times_min >= self.time_iter * self.window_slide) & (self.rri_times_min < ((self.time_iter * self.window_slide) + self.process_window))]

        #self.cursor = self.rri_time[50]
        #self.cursor_x = [self.cursor] *120
        #self.cursor_y = list(range(120))
        x = list(self.win_time)
        y = list(self.win_data)
        #print(self.centralWidget.isVisible == True)
        self.data_line.setData(x, y)  # Update the data.
        self.time_iter = self.time_iter + 1
        #xx = np.array(self.cursor_x)
        #yy = np.array(self.cursor_y)
        #self.data_line1.setData(xx, yy)

                                                                                               

app = QtWidgets.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
