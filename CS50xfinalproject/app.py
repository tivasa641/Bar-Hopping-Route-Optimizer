from cs50 import SQL
from flask import Flask, redirect, render_template, request

from functions import apology, combinations, optimize, verify

# Configure application
app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///bar.db")


@app.route("/", methods=["GET", "POST"])
def index():
    # CASE of post
    if request.method == "POST":
        budget = request.form.get("budget")
        bars_number = request.form.get("bars_number")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        day_of_week = request.form.get("day_of_week")
        start_bar = request.form.get("start_bar")
        last_bar = request.form.get("last_bar")
        optimize_type = request.form.get("optimize_type")

        # VERIFY user's input
        error = verify(budget, bars_number, start_time, end_time, day_of_week, start_bar, last_bar, db)
        if error:
            return error

        # FIND open bar in day of week in database
        open_bar_db = db.execute("SELECT * FROM bars WHERE id IN (SELECT bar_id FROM opening_hours WHERE day_of_week = ?)", day_of_week)
        
        # CALCULATE all possible combinations of nodes
        start_bar_id = db.execute("SELECT id FROM bars WHERE name = ?", start_bar)
        last_bar_id = db.execute("SELECT id FROM bars WHERE name = ?", last_bar)
        combinations_of_nodes = combinations(open_bar_db, bars_number, budget, start_bar_id, last_bar_id)
        if len(combinations_of_nodes) == 0:
            return apology("YOUR BUDGET ISN'T ENOUGH")

        # CALCULATE best bar hopping route
        distances_db = db.execute(f"SELECT {optimize_type} AS optimize_type, origin_bar_id, destination_bar_id FROM distances")
        best_route = optimize(combinations_of_nodes, distances_db, bars_number)
        
        return render_template("result.html", best_route=best_route)
    
    # CASE of get
    else:
        return render_template("index.html")
    

@app.route("/list", methods=["GET"])
def list():
    bars_info_db = db.execute("SELECT name, day_of_week, open_time, close_time, last_order_time FROM opening_hours JOIN bars ON bar_id = bars.id")
    bars_info = {}

    # LET data into dict
    for bar in bars_info_db:
        name = bar["name"]
        day_of_week = bar["day_of_week"]

        # Assum bar close every day
        if name not in bars_info:
            # KEY:day of week, VALUE: all info about time
            bars_info[name] = {
                1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None
            }

        # Let data into second dict if bar open
        open_time = bar["open_time"]
        close_time = bar["close_time"]
        last_order_time = bar["last_order_time"]
        bars_info[name][day_of_week] = {
            "open_time": open_time,
            "close_time": close_time,
            "last_order_time": last_order_time
        }

    return render_template("list.html", bars_info=bars_info)


@app.route("/idea", methods=["GET"])
def idea():
    return render_template("idea.html")