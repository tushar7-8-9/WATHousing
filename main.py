from flask import Flask, render_template, jsonify
import sqlite3, datetime

app = Flask(__name__)

@app.route('/')
def home():
        markers, marker_location, current_year, years, marker_info = controller()
        return render_template('home.html',  markers2 = markers, marker_location2 = marker_location, marker_info2 = marker_info, current_year2 = current_year)

def get_marker_location(db, conn, cur):
        cur.execute(
        '''
        SELECT building_name,lat,long FROM building_location GROUP BY building_name
        '''
        )
        locations, main_dict = cur.fetchall(), {}
        for building in locations: main_dict[building[0]] = {"lat": building[1], "lng": building[2] }
        return main_dict

def get_unique_names(db, conn, cur):
    cur.execute(
        '''
        SELECT DISTINCT(building_name) FROM building_location
        '''
        )
    names = cur.fetchall()
    return [name[0] for name in names]

def data_fetcher_lease(db, conn, cur, year, building, main_dict):
        col_names = ["lease_price_unit","lease_price_room"] #col_names for the data table from where pull is taking place
        key_name= ["leasePriceUnit", "leasePriceRoom"]
        table_names = ["housing_data_unit", "housing_data_room"]
        main_dict[building][str(year)] = {}
        for index in range (0, len(col_names)):
                cur.execute(f''' SELECT AVG({col_names[index]}) FROM {table_names[index]} WHERE building_name = ? AND lease_year = ? AND lease_sublet = "lease"
                        ''', (building, year)
                            )
                price = cur.fetchall()[0][0]
                if price is not None: price = "$" + str(int(price)) + "/month"
                else: price = "Data Not Available"
                main_dict[building][str(year)][key_name[index]] = price

def data_fetcher_general(db, conn, cur, building, main_dict):
    table_names = ["housing_data_unit", "housing_data_room"]
    avg_rating, counter = 0, 0
    for name in table_names:
        cur.execute(f''' SELECT AVG(rating) FROM {name} WHERE building_name = ?
                        ''', (building,))
        test = cur.fetchall()[0][0]
        counter += 1 if test != None else 0 
        avg_rating += float(test) if test != None else 0 
    main_dict[building]["rating"] = avg_rating/counter
    
    cur.execute(''' SELECT address FROM building_location WHERE building_name = ?
                        ''', (building,))
    address = cur.fetchall()[0][0]
    main_dict[building]['address'] = address

def data_fetcher_sublet(db, conn, cur, year, building, main_dict):
      terms = ["spring", "winter", "fall"]
      col_names = ["sublet_price_unit", "sublet_price_room"]
      table_names = ["housing_data_unit", "housing_data_room"]
      key_name= ["subletPriceUnit", "subletPriceRoom"]
      for index in range (0, len(col_names)):
        sub_dict = {}  
        for term in terms:
                cur.execute(f''' SELECT AVG({col_names[index]}) FROM {table_names[index]} WHERE building_name = ? AND lease_year = ? AND lease_sublet = "sublet" and sublet_term = ?
                        ''', (building, year, term)
                            )
                price = cur.fetchall()[0][0]
                if price is not None: price = "$" + str(int(price)) + "/month"
                else: price = "Data Not Available"
                sub_dict[term] = price
        main_dict[building][str(year)][key_name[index]] = sub_dict

def get_marker_info(db, conn, cur, base_year, current_year, markers):
    main_dict = {}
    for building in markers:
            main_dict[building] = {}
            for year in range(base_year, current_year+1):
                  data_fetcher_general(db, conn, cur, building, main_dict)
                  data_fetcher_lease(db, conn, cur, year, building, main_dict)
                  data_fetcher_sublet(db, conn, cur, year, building, main_dict)
    return main_dict

def create_var(db, conn, cur):
    markers = get_unique_names(db, conn, cur)
    marker_location = get_marker_location(db, conn, cur)
    base_year = 2021
    current_year = datetime.datetime.now().year
    years = [n for n in range(base_year, current_year + 1)]
    marker_info = get_marker_info(db, conn, cur, base_year, current_year, markers)
    return markers, marker_location, current_year, years, marker_info

def controller():
    db = "rent_data.db"
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    return create_var(db, conn, cur)



if __name__ == '__main__':
    app.run()
