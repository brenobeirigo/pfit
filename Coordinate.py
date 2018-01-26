import urllib.request
import json
import csv


class Coordinate(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_manhattan_dist(self, p2):
        manhattan = abs(self.get_x() - p2.get_x()) + \
            abs(self.get_y() - p2.get_y())
        return round(manhattan * 10, 0)

    # Read distances from file
    def get_distances_from(self, csv_dist):
        # List of requests
        dist_dic = {}

        # Try opening csv file
        with open(csv_dist) as f:
            reader = csv.reader(f)
            header = next(reader)

            # Id customer according to number of rows
            id_customer = 0

            # For each data row
            for row in reader:
                # Pickup latitude
                pickup_x = float(row[0])
                # Pickup longitude
                pickup_y = float(row[1])
                # Dropoff latitude
                dropoff_x = float(row[2])
                # Dropoff longitude
                dropoff_y = float(row[3])
                # Distance betweeen points
                dist = float(row[4])

                # Save distance
                dist_dic[(pickup_x, pickup_y, dropoff_x, dropoff_y)] = dist

        return dist_dic

    def get_distance_online(self, p2):
        # print("GET DISTANCE ONLINE")
        distances = self.get_distances_from("dist.csv")
        # print(distances)
        key = (self.get_x(), self.get_y(), p2.get_x(), self.get_y())
        if (key not in distances.keys()):
            print("DISTANCE NOT FOUND")
            self.MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoiYnJlbm9iZWlyaWdvIiwiYSI6ImNpeHJiMDNidTAwMm0zNHFpcXVzd2UycHgifQ.tWIDAiRhjSzp1Bd40rxaHw"
            url = "https://api.mapbox.com/directions-matrix/v1/mapbox/driving/" \
                    + str(self.get_x()) + "," + str(self.get_y()) + ";" \
                    + str(p2.get_x()) + "," + str(self.get_y()) + \
                    "?access_token=" + self.MAPBOX_ACCESS_TOKEN
            print("URL:" + url)
            response = urllib.request.urlopen(url).read()
            j = json.loads(response.decode('utf-8'))
            print(j)
            line = str(self.get_x()) + "," + str(self.get_y()) + "," + str(p2.get_x()) + \
                "," + str(self.get_y()) + "," + \
                str(float(j["durations"][0][1])) + "," + str(j)
            print("TEST: " + line)
            with open("dist.csv", "a") as myfile:
                myfile.write("\n"+line)
            return float(j["durations"][0][1])
        else:
            print("SAVED: " + str(distances[key]))
            return distances[key]
            

    @classmethod
    def get_middle_point(self, c1, c2):
         # Get middle point of an arrow
        min_x = min([c1.get_x(), c2.get_x()])
        max_x = max([c1.get_x(), c2.get_x()])
        x = min_x + (max_x - min_x) / 2.0
        min_y = min([c1.get_y(), c2.get_y()])
        max_y = max([c1.get_y(), c2.get_y()])
        y = min_y + (max_y - min_y) / 2.0
        return Coordinate(x, y)

    def get_x(self):
        # Getter method for a Coordinate object's x coordinate.
        return self.x

    def get_y(self):
        # Getter method for a Coordinate object's y coordinate
        return self.y

    def __str__(self):
        return '<' + str(self.get_x()) + ',' + str(self.get_y()) + '>'

    def __eq__(self, other):
        # First make sure `other` is of the same type
        assert type(other) == type(self)
        # Since `other` is the same type, test if coordinates are equal
        return self.get_x() == other.get_x() and self.get_y() == other.get_y()

    def __repr__(self):
        return 'Coordinate(' + str(self.get_x()) + ',' + str(self.get_y()) + ')'
