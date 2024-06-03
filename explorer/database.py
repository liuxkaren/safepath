import json
import math
import sqlite3
import pandas as pd
from datetime import datetime


DEGREE_DIFFERENCE = 0.0001

def rounding(degree, difference=DEGREE_DIFFERENCE):
    """This method is used to determine rounded values of degrees of latitudes
        or longitudes based on degrees of latitude difference and longitude
        difference, respectively. By default, both latitude and longitude are
        calculated by a constant 'DEGREE_DIFFERENCE' in a value of 0.0001."""
        
    power = math.log10(difference)
    if power > 0:
        return round(float(degree) / difference) * difference
    else:
        decimal_place = math.ceil(abs(power))
        return round(round(float(degree) / difference) * difference, decimal_place)

class InvalidCoordinateError(Exception):
    def __init__(self, message="""Invalid coordinate. Must provide either a single 
                                 iterable or separate latitude and longitude values."""):
        self.message = message
        super().__init__(self.message)

class Coordinate:
    def __init__(self, *coordinate) -> None:
        """This class is mainly used to determine rounded values of coordinates 
            in specific degree difference
            
        :param *coordinate: The latitude value and the longitude value.
        :type *coordinate: two float numbers or a tuple (25.2525, 123.456)."""
        
        if len(coordinate) == 1:
            if len(coordinate[0]) != 2:
                message = "Invalid coordinate format. Must provide latitude and longitude values."
                raise InvalidCoordinateError(message)
            self.latitude = coordinate[0][0]
            self.longitude = coordinate[0][1]
        elif len(coordinate) == 2:
            self.latitude = coordinate[0]
            self.longitude = coordinate[1]
        else:
            raise InvalidCoordinateError()

        if abs(self.latitude) > 90:
            message = "Invalid latitude value. Must between -90 and 90 degrees."
            raise InvalidCoordinateError(message)
        if abs(self.longitude) > 180:
            message = "Invalid latitude value. Must between -180 and 180 degrees."
            raise InvalidCoordinateError(message)

        self.latitude_grid = rounding(self.latitude)
        self.longitude_grid = rounding(self.longitude)

class InvalidCarAccidentError(Exception):
    def __init__(self, message="Invalid."):
        self.message = message
        super().__init__(self.message)

class CarAccident:
    def __init__(self, year, month=None, rank=2):
        """This class is used to get data from car accident csv files.
        
        :param year: The year value of Republic of China.
        :type year: int
        
        :param month: The month value.
        :type month: int
        
        :param rank: The type of rank value of a car accident. There are three
            types of car accidents: A1, A2, and A3. Currently, A3-type data is 
            not supported.
        :type rank: int or string"""
        
        self._year = year
        self._month = month
        self._rank = rank
        self._is_arg_valid()
        self._df = pd.DataFrame()
        self._read_csv_file()
        self._get_data()

    def _is_arg_valid(self):
        """This method is used to determine if the auguments are valid."""
        
        path = r".\data\tracking.json"
        with open(path) as file:
            data = json.load(file)
            starting_year = data["car_accident_csv"]["starting_year"]
            ending_year = data["car_accident_csv"]["ending_year"]
        if (type(self._year) != int or (self._year < starting_year or self._year > ending_year)):
            message = f"Invalid year. Must be an integer between {starting_year} and {ending_year} (including)."
            raise InvalidCarAccidentError(message)
        if self._month:
            if type(self._month) != int or (self._month < 1 or self._month > 12):
                message = "Invalid mouth. Must be an integer between 1 and 12 (including)."
                raise InvalidCarAccidentError(message)

    def _read_csv_file(self):
        """This method is used to read and get data from the csv files."""
        
        dtype_mapping = {
            "發生日期": str,
            "發生時間": str,
            "經度": float,
            "緯度": float,
            "死亡受傷人數": str,
            "發生地點": str,
            "事故類型": str
        }
        if self._rank == 1 or self._rank == '1' or self._rank == "A1" or self._rank == "a1":
            path = f"./data/accidents/{self._year}/{self._year}年度A1交通事故資料.csv"
            self._df = pd.read_csv(path)
            self._df = self._df[:-2]
            # if self._month:
            #     self._df['發生日期'] = self._df['發生日期'].astype(int)
            #     if self._month > 9:
            #         self._df = self._df[self._df['發生日期'].astype(str).str[4:6] == str(self._month)]
            #     else:
            #         self._df = self._df[self._df['發生日期'].astype(str).str[4:6] == f"0{self._month}"]
            #     self._df['發生日期'] = self._df['發生日期'].astype(float)
            #     self._df = self._df.reset_index(drop=True)
        elif self._rank == 2 or self._rank == '2' or self._rank == "A2" or self._rank == "a2":
            if not self._month:
                for m in range(1, 13):
                    path = f"./data/accidents/{self._year}/{self._year}年度A2交通事故資料_{m}.csv"
                    monthly_data = pd.read_csv(path, dtype=dtype_mapping, low_memory=False)
                    monthly_data = monthly_data[:-2]
                    self._df = pd.concat([self._df, monthly_data], ignore_index=True)
            else:
                path = f"./data/accidents/{self._year}/{self._year}年度A2交通事故資料_{self._month}.csv"
                self._df = pd.read_csv(path, dtype=dtype_mapping, low_memory=False)
                self._df = self._df[:-2]
        else:
            message = "Invalid rank. Must be either 1, '1', 'A1', 'a1', or 2, '2', 'A2', 'a2'."
            raise InvalidCarAccidentError(message)

    def _get_data(self):
        """This method is used to take the data of interest"""
        
        self._dates = [datetime.strptime(str(int(d)), "%Y%m%d").strftime("%Y-%m-%d") for d in self._df["發生日期"]]
        self._times = [datetime.strptime(str(int(t)).zfill(6), "%H%M%S").strftime("%H:%M:%S") for t in self._df["發生時間"]]
        self._latitudes = self._df["緯度"]
        self._longitudes = self._df["經度"]
        self._casualties = self._df["死亡受傷人數"]
        self._fatalities = [int(c[2]) for c in self._casualties]
        self._injuries = [int(c[-1]) for c in self._casualties]
        self._location = self._df["發生地點"]
        self._area_1 = [loc[:3] for loc in self._location]
        self._area_2 = [loc[3:6] for loc in self._location]
        # Check if the third character of the string is not one of "鄉", "鎮", "市", or "區"
        for i in range(len(self._area_2)):
            if self._area_2[i][2] not in "鄉鎮市區":
                # If the condition is met, truncate the string to the first two characters
                self._area_2[i] = self._area_2[i][:2]
        self._includes_pedestrian = self._df["事故類型及型態大類別名稱"].str.contains('人')
        
        self._reorganize_data()
        
    def _reorganize_data(self):
        """This method is used to take out the duplicated data"""
        
        check = 0
        longitude_check = 0
        latitude_check = 0
        self._data = []
        for i in range(len(self._dates)):
            if self._times[i] == check:
                if (self._longitudes[i] == longitude_check) and (self._latitudes[i] == latitude_check):
                    continue
                else:
                    longitude_check = self._longitudes[i]
                    latitude_check = self._latitudes[i]
            else:
                check = self._times[i]
                self._data.append([
                    self._dates[i],
                    self._times[i],
                    self._latitudes[i],
                    self._longitudes[i],
                    self._fatalities[i],
                    self._injuries[i],
                    self._area_1[i],
                    self._area_2[i],
                    self._includes_pedestrian[i]
                ])
        self.data = pd.DataFrame(self._data, columns=[
            "date",
            "time",
            "latitude",
            "longitude",
            "fatality",
            "injury",
            "area_1",
            "area_2",
            "includes_pedestrian"
        ])
        self._dates = self.data.iloc[:, 0]
        self._times = self.data.iloc[:, 1]
        self._latitudes = self.data.iloc[:, 2]
        self._longitudes = self.data.iloc[:, 3]
        self._fatalities = self.data.iloc[:, 4]
        self._injuries = self.data.iloc[:, 5]
        self._area_1s = self.data.iloc[:, 6]
        self._area_2s = self.data.iloc[:, 7]
        self._includes_pedestrian = self.data.iloc[:, 8]

    def date(self, id=None):
        if id is not None:
            return self._dates[id]
        else:
            return self._dates

    def time(self, id=None):
        if id is not None:
            return self._times[id]
        else:
            return self._times

    def latitude(self, id=None):
        if id is not None:
            return self._latitudes[id]
        else:
            return self._latitudes

    def longitude(self, id=None):
        if id is not None:
            return self._longitudes[id]
        else:
            return self._longitudes

    def fatality(self, id=None):
        if id is not None:
            return int(self._fatalities[id])
        else:
            return self._fatalities

    def injury(self, id=None):
        if id is not None:
            return int(self._injuries[id])
        else:
            return self._injuries

    def area_1(self, id=None):
        if id is not None:
            return self._area_1s[id]
        else:
            return self._area_1s

    def area_2(self, id=None):
        if id is not None:
            return self._area_2s[id]
        else:
            return self._area_2s
    
    def includes_pedestrian(self, id=None):
        if id is not None:
            return self._includes_pedestrian[id]
        else:
            return self._includes_pedestrian

class Earthquake:
    def __init__(self, year):
        self._year = year
        self._df = pd.read_csv(f".\data\earthquakes\earthquake_{self._year}年.csv", engine='python', encoding="big5")
        self._get_data()
        self._reorganize_data()
        
    def _get_data(self):
        self._dates = [datetime.strptime(d, "%Y-%m-%d") for d in self._df["Date"]]
        if self._year == datetime.now().year:
            self.size = 0
            for date in self._dates:
                if date.month == datetime.now().month:
                    self._dates = self._dates[:self.size]
                    break
                self.size += 1
        else:
            self.size = len(self._df)
        
        self._times = [datetime.strptime(t, "%H:%M:%S").time() for t in self._df["Time"]][:self.size]
        self._latitudes = self._df["北緯"][:self.size]
        self._longitudes = self._df["東經"][:self.size]
        self._magnitudes = self._df["芮氏規模"][:self.size]
        self._depths = self._df["深度"][:self.size]
        self._areas = self._df["城市"][:self.size]
        self._intensities = self._df["震度"][:self.size]
        for i in range(self.size):
            if len(self._intensities[i]) != 1:
                self._intensities[i] = self._intensities[i].replace(" ", "")
            else:
                self._intensities[i] += "級"
                
    def _reorganize_data(self):
        data = []
        for i in range(self.size):
            data.append([
                self._dates[i],
                self._times[i],
                self._latitudes[i],
                self._longitudes[i],
                self._magnitudes[i],
                self._depths[i],
                self._areas[i],
                self._intensities[i]
            ])
        self.data = pd.DataFrame(data, columns=[
            "date",
            "time",
            "latitude",
            "longitude",
            "magnitude",
            "depth",
            "area",
            "intensity"
        ])

    def date(self, id=None):
        if id is None:
            return self._dates
        else:
            return self._dates[id]

    def time(self, id=None):
        if id is None:
            return self._times
        else:
            return self._times[id]
        
    def latitude(self, id=None):
        if id is None:
            return self._latitudes
        else:
            return self._latitudes[id]
        
    def longitude(self, id=None):
        if id is None:
            return self._longitudes
        else:
            return self._longitudes[id]

    def magnitude(self, id=None):
        if id is None:
            return self._magnitudes
        else:
            return self._magnitudes[id]
        
    def depth(self, id=None):
        if id is None:
            return self._depths
        else:
            return self._depths[id]
        
    def area(self, id=None):
        if id is None:
            return self._areas
        else:
            return self._areas[id]

    def intensity(self, id=None):
        if id is None:
            return self._intensities
        else:
            return self._intensities[id]

class SQLController:
    """This class is used to control 'db.sqlites' by using sqlite3 module."""
    
    PATH = r"..\.\db.sqlite3"
    def __init__(self, table_name):
        self.table_name = table_name
        self.conn = sqlite3.connect(SQLController.PATH)
        self.cursor = self.conn.cursor()
    
    def close(self):
        self.conn.close()
    
    def select(self, id=None, column=None):
        if id:
            if column:
                sql = f"SELECT {column} FROM {self.table_name} where id={id}"
                self.cursor.execute(sql)
                return self.cursor.fetchone()[0]
            else:
                sql = f"SELECT * FROM {self.table_name} where id={id}"
                self.cursor.execute(sql)
                return self.cursor.fetchone()
        else:
            sql = "SELECT * FROM {self.table_name}"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

class TrafficAccidentSQLController(SQLController):
    def __init__(self):
        self.table_name = "risk_traffic_accident"
        super().__init__(self.table_name)

    def new(self, latitude, longitude, fatality, injury, includes_pedestrian):
        coordinate = Coordinate(latitude, longitude)
        self.existing_id = self.coordinate_id(coordinate.latitude_grid, 
                                              coordinate.longitude_grid)
        total_fatality = fatality
        total_injury = injury
        if includes_pedestrian:
            pedestrian_fatality = fatality
            pedestrian_injury = injury
        else:
            pedestrian_fatality = pedestrian_injury = 0
        
        if self.existing_id:
            number = self.select(self.existing_id, "number") + 1
            total_fatality += self.select(self.existing_id, "total_fatality")
            total_injury += self.select(self.existing_id, "total_injury")
            pedestrian_fatality += self.select(self.existing_id, "pedestrian_fatality")
            pedestrian_injury += self.select(self.existing_id, "pedestrian_injury")
            sql = f"""UPDATE {self.table_name} 
                        SET number = {number}, 
                        total_fatality = {total_fatality},
                        total_injury = {total_injury},
                        pedestrian_fatality = {pedestrian_fatality},
                        pedestrian_injury = {pedestrian_injury}
                        WHERE id = {self.existing_id}"""
            self.cursor.execute(sql)
        else:
            sql = f"""INSERT INTO {self.table_name} (latitude, longitude, number, 
                        total_fatality, total_injury, pedestrian_fatality,
                        pedestrian_injury) VALUES (?, ?, ?, ?, ?, ?, ?)"""
            self.cursor.execute(sql, (coordinate.latitude_grid, 
                                      coordinate.longitude_grid, 
                                      1, total_fatality, total_injury,
                                      pedestrian_fatality, pedestrian_injury))
        self.conn.commit()
    
    def coordinate_id(self, latitude, longitude):
        sql = f"""SELECT * FROM {self.table_name} 
                    WHERE latitude = {latitude} AND longitude = {longitude}"""
        self.cursor.execute(sql)
        data = self.cursor.fetchone()
        if data:
            return data[0]
        else:
            return None

class PedestrianHellSQLController(SQLController):
    def __init__(self):
        self.table_name = "risk_pedestrian_hell"
        super().__init__(self.table_name)

    def new(self, area_1, area_2, 
            fatality, injury, includes_pedestrian):
        total_fatality = fatality
        total_injury = injury
        if includes_pedestrian:
            pedestrian_fatality = fatality
            pedestrian_injury = injury
        else:
            pedestrian_fatality = pedestrian_injury = 0
            
        self.existing_id = self.administrative_area_id(area_1, 
                                                       area_2)
        if self.existing_id:
            number = self.select(self.existing_id, "number") + 1
            total_fatality += self.select(self.existing_id, "total_fatality")
            total_injury += self.select(self.existing_id, "total_injury")
            pedestrian_fatality += self.select(self.existing_id, "pedestrian_fatality")
            pedestrian_injury += self.select(self.existing_id, "pedestrian_injury")
            sql = f"""UPDATE {self.table_name} 
                    SET number = {number}, 
                    total_fatality = {total_fatality}, 
                    total_injury = {total_injury},
                    pedestrian_fatality = {pedestrian_fatality}, 
                    pedestrian_injury = {pedestrian_injury} WHERE id = {self.existing_id}"""
            self.cursor.execute(sql)
        else:
            sql = f"""INSERT INTO {self.table_name} (
                    area_1, 
                    area_2, 
                    number, 
                    total_fatality, 
                    total_injury, 
                    pedestrian_fatality, 
                    pedestrian_injury) VALUES (?, ?, ?, ?, ?, ?, ?)"""
            self.cursor.execute(sql, (area_1, 
                                      area_2, 
                                      1, total_fatality, total_injury,
                                      pedestrian_fatality, pedestrian_injury))
        self.conn.commit()
    
    def administrative_area_id(self, area_1, area_2):
        sql = f"""SELECT * FROM {self.table_name} 
                    WHERE area_1 = '{area_1}' 
                    AND area_2 = '{area_2}'"""
        self.cursor.execute(sql)
        data = self.cursor.fetchone()
        if data:
            return data[0]
        else:
            return None

class EarthquakeSQLController(SQLController):
    def __init__(self):
        self.table_name = "risk_earthquake"
        super().__init__(self.table_name)

    def new(self, date, time, latitude, longitude, magnitude, depth):
        sql = f"""INSERT INTO {self.table_name} (
                date, time, latitude, longitude, 
                magnitude, depth) VALUES (?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.execute(sql, (date, time, latitude, longitude, magnitude, depth))
        self.conn.commit()

class EarthquakeIntensitySQLController(SQLController):
    def __init__(self):
        self.table_name = "risk_earthquake_intensity"
        super().__init__(self.table_name)

    def new(self, area, intensity):
        self.existing_id = self.administrative_area_id(area_1, 
                                                       area_2)
        if self.existing_id:
            number = self.select(self.existing_id, "number") + 1
            total_fatality += self.select(self.existing_id, "total_fatality")
            total_injury += self.select(self.existing_id, "total_injury")
            pedestrian_fatality += self.select(self.existing_id, "pedestrian_fatality")
            pedestrian_injury += self.select(self.existing_id, "pedestrian_injury")
            sql = f"""UPDATE {self.table_name} 
                    SET number = {number}, 
                    total_fatality = {total_fatality}, 
                    total_injury = {total_injury},
                    pedestrian_fatality = {pedestrian_fatality}, 
                    pedestrian_injury = {pedestrian_injury} WHERE id = {self.existing_id}"""
            self.cursor.execute(sql)
        else:
            sql = f"""INSERT INTO {self.table_name} (
                    area_1, 
                    area_2, 
                    number, 
                    total_fatality, 
                    total_injury, 
                    pedestrian_fatality, 
                    pedestrian_injury) VALUES (?, ?, ?, ?, ?, ?, ?)"""
            self.cursor.execute(sql, (area_1, 
                                      area_2, 
                                      1, total_fatality, total_injury,
                                      pedestrian_fatality, pedestrian_injury))
        self.conn.commit()
    
    def administrative_area_id(self, area_1, area_2):
        sql = f"""SELECT * FROM {self.table_name} 
                    WHERE area_1 = '{area_1}' 
                    AND area_2 = '{area_2}'"""
        self.cursor.execute(sql)
        data = self.cursor.fetchone()
        if data:
            return data[0]
        else:
            return None

class UpdateTrafficAccidentData:
    def __init__(self):
        self.get_tracking_data()
        self.determine_range()
        self.update_data()
        self.update_tracking_data()
        
    def get_tracking_data(self):
        self.tracking_path = r".\data\tracking.json"
        with open(self.tracking_path) as file:
            self.tracking_data = json.load(file)
            self.starting_year = self.tracking_data["car_accident_csv"]["starting_year"]
            self.ending_year = self.tracking_data["car_accident_csv"]["ending_year"]
            self.tracking_year = self.tracking_data["traffic_accident"]["tracking_year"]
            self.tracking_month = self.tracking_data["traffic_accident"]["tracking_month"]
            self.tracking_rank = self.tracking_data["traffic_accident"]["tracking_rank"]
    
    def initialize_range(self):
        if not self.tracking_year:
            self.tracking_year = self.starting_year
        if not self.tracking_month:
            self.tracking_month = 0
        if not self.tracking_rank:
            self.tracking_rank = 1
    
    def determine_range(self):
        self.initialize_range()
        if self.tracking_rank == 1:
            if self.tracking_month == 0:
                self.tracking_month = 12
            elif self.tracking_month == 12:
                self.tracking_rank = 2
                self.tracking_month = 0
        if self.tracking_rank == 2:
            if self.tracking_month == 12:
                self.tracking_year += 1
                self.tracking_rank = 1
            else:
                self.tracking_month += 1

    def update_data(self):
        self.accident = CarAccident(year=self.tracking_year, 
                                    month=self.tracking_month, 
                                    rank=self.tracking_rank)
        self.traffic_controller = TrafficAccidentSQLController()
        self.ped_hell_controller = PedestrianHellSQLController()
        self.number_of_data = len(self.accident.data)
        for i in range(self.number_of_data):
            latitude = self.accident.latitude(i)
            longitude = self.accident.longitude(i)
            fatality = self.accident.fatality(i)
            injury = self.accident.injury(i)
            area_1 = self.accident.area_1(i)
            area_2 = self.accident.area_2(i)
            includes_pedestrian = self.accident.includes_pedestrian(i)
            self.traffic_controller.new(latitude, longitude, 
                                        fatality, injury, includes_pedestrian)
            self.ped_hell_controller.new(area_1, area_2, 
                                         fatality, injury, includes_pedestrian)
        self.traffic_controller.close()
        self.ped_hell_controller.close()
        
    def update_tracking_data(self):
        self.tracking_data["traffic_accident"]["tracking_year"] = self.tracking_year
        self.tracking_data["traffic_accident"]["tracking_month"] = self.tracking_month
        self.tracking_data["traffic_accident"]["tracking_rank"] = self.tracking_rank
        with open(self.tracking_path, 'w') as file:
            json.dump(self.tracking_data, file)
        

def test_CarAccident():
    accident = CarAccident(year=111, month=2, rank=2)
    # print(accident.date())
    # print(accident.time())
    # print(accident.latitude())
    # print(accident.longitude())
    # print(accident.fatality())
    # print(accident.injury())
    # print(accident.area_1())
    # print(accident.area_2())
    # print(accident.includes_pedestrian())
    # print(accident.includes_pedestrian().sum())
    data_id = 1
    # print(accident.date(data_id))
    # print(accident.time(data_id))
    # print(accident.latitude(data_id))
    # print(accident.longitude(data_id))
    # print(accident.fatality(data_id))
    # print(accident.injury(data_id))
    # print(accident.area_1(data_id))
    print(accident.area_2(data_id))

def test_SQLController():
    controller = TrafficAccidentSQLController()
    test_latitude = 24.4389
    test_longitude = 118.2497
    print(controller.coordinate_id(test_latitude, test_longitude))
    print(controller.coordinate_id(test_latitude+50, test_longitude))
    print(controller.select(50956, "total_injury"))
    # controller.new(test_latitude, test_longitude, 55, 66)
    # print(controller.select(50956))
    # controller.new(test_latitude, test_longitude, 99, 77)
    # print(controller.select(50956))
    # controller.new(test_latitude+50, test_longitude+20, 55, 123)
    controller.close()


if __name__ == "__main__":
    test_CarAccident()
    # test_SQLController()
    pass
    
