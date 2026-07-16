import itertools

from cs50 import SQL
from flask import render_template


"""
This function is from distribution code of CS50x problem set 9 finance
https://cs50.harvard.edu/x/psets/9/finance/   
"""
def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def check_bar_exist(bar_name, db):
    """Cheak user's starting bar or end bar is in database or not"""

    bar = db.execute("SELECT id FROM bars WHERE name = ?", bar_name)
    if len(bar) == 0:
        # bar isn't in database
        return True
    else:
        return False


def combinations(open_bar_db, bars_number, budget, start_bar_id, last_bar_id):
    """Calculate all possible combinations of nodes"""

    # FIND all combinations that first one is start bar and last one is last bar
    start_node = None
    mid_nodes = []
    end_node = None
    for bar in open_bar_db:
        if bar["id"] != start_bar_id[0]["id"] and bar["id"] != last_bar_id[0]["id"]:
            mid_nodes.append(bar)
        elif bar["id"] == start_bar_id[0]["id"]:
            start_node = bar
        else:
            end_node = bar
    combinations_of_mid_nodes = list(itertools.combinations(mid_nodes, int(bars_number) - 2))
    
    # COLLET combinations user can afford
    valid_combinations = []
    for combination_of_mid_nodes in combinations_of_mid_nodes:
        full_combination = [start_node] + list(combination_of_mid_nodes) + [end_node]

        # CALCULATE min spend of combination
        min_spend = 0
        for bar in full_combination:
            min_spend = min_spend + bar["avg_cocktail_price"] * 2  # Assumes every bar need to order 2 cocktail at least
        if min_spend < int(budget):
            valid_combinations.append(full_combination)

    return valid_combinations


def optimize(combinations_of_nodes, distances_db, bars_number):
    """Calculate best bar hopping route"""
    
    target_permutation = []
    min_sum_of_weights = 15000   # NOTE: Max sum of weights is 12295m or 11119s

    # CREAT a new Dictionary { {("origin_bar_id", "destination_bar_id"): "data_of_optimize_type"}......}
    weight_of_pairs = {}
    for data in distances_db:
        key = (data["origin_bar_id"], data["destination_bar_id"])
        weight_of_pairs[key] = data["optimize_type"]
    
    for combination in combinations_of_nodes:
        # CALCULATE all possible permutations of nodes
        start_node = combination[0]
        end_node = combination[-1]
        mid_nodes = combination[1:-1]
        permutations_of_mid_nodes = list(itertools.permutations(mid_nodes, int(bars_number) - 2))
        
        for permutation_of_mid_nodes in permutations_of_mid_nodes:
            full_permutation = [start_node] + list(permutation_of_mid_nodes) + [end_node]

            # CALCULATE weight of each permutation
            sum_of_weights = 0
            for i in range(len(full_permutation) - 1):
                origin_bar_id = full_permutation[i]["id"]
                destination_bar_id = full_permutation[i + 1]["id"]
                weight = weight_of_pairs[(origin_bar_id, destination_bar_id)]
                sum_of_weights = sum_of_weights + weight

            # FIND min sum of weights of all permutations
            if sum_of_weights < min_sum_of_weights:
                min_sum_of_weights = sum_of_weights
                target_permutation = full_permutation

    # CALCULATE estimated cost
    cost = 0
    for bar in target_permutation:
        cost = cost + bar["avg_cocktail_price"] * 2
            
    final_result = {"route": target_permutation, "weight": min_sum_of_weights, "cost": cost}
    return final_result


def verify(budget, bars_number, start_time, end_time, day_of_week, start_bar, last_bar, optimize_type, db):
    """Verify user's input"""
    # NOTE: Calling the database inside a function is a bad design, but this piece of code is really too long. So I traded off performance for better readability.

    # user miss input
    if not budget:
        return apology("YOUR BUDGET IS MISSING")
    if not bars_number:
        return apology("YOUR NUMBER OF BARS IS MISSING")
    if not start_time:
        return apology("YOUR STARTING TIME IS MISSING")
    if not end_time:
        return apology("YOUR END TIME IS MISSING")
    if day_of_week == "0":
        return apology("YOUR DAY OF WEEK IS MISSING")
    if not start_bar:
        return apology("YOUR START BAR IS MISSING")
    if not last_bar:
        return apology("YOUR LAST BAR IS MISSING")
    
    # start bar or last bar don't in database
    if check_bar_exist(start_bar, db):
        return apology("YOUR STARTING BAR ISN'T IN THE BAR LIST") 
    if check_bar_exist(last_bar, db):
        return apology("YOUR LAST BAR ISN'T IN THE BAR LIST") 
    
    # start bar and last bar is same
    if start_bar == last_bar:
        return apology("THE START BAR AND END BAR CANNOT BE THE SAME. THAT DOESN'T COUNT AS BAR HOPPING.")

    # start bar or last bar don't open in day of week
    bool_start_bar = db.execute("SELECT id FROM opening_hours WHERE bar_id = (SELECT id FROM bars WHERE name = ?) AND day_of_week = ?", start_bar, day_of_week)
    if not bool_start_bar:
         return apology("YOUR STARTING BAR DOESN'T OPEN IN DAY OF WEEK")
    bool_last_bar = db.execute("SELECT id FROM opening_hours WHERE bar_id = (SELECT id FROM bars WHERE name = ?) AND day_of_week = ?", last_bar, day_of_week)
    if not bool_last_bar:
         return apology("YOUR LAST BAR DOESN'T OPEN IN DAY OF WEEK")

    # start bar don't open at starting time 
    open_time_of_start_bar = db.execute("SELECT open_time FROM opening_hours WHERE bar_id = (SELECT id FROM bars WHERE name = ?) AND day_of_week = ?", start_bar, day_of_week)
    if start_time < open_time_of_start_bar[0]["open_time"]:
        return apology("YOUR STARTING BAR DOESN'T OPEN AT START TIME")
    
    # end time already miss last order time of last bar
    lasr_order_time_of_last_bar = db.execute("SELECT last_order_time FROM opening_hours WHERE bar_id = (SELECT id FROM bars WHERE name = ?) AND day_of_week = ?", last_bar, day_of_week)
    if end_time > lasr_order_time_of_last_bar[0]["last_order_time"]:
        return apology("YOU WILL MISS LAST ORDER TIME OF LAST BAR")
    
    # numder of ber isn't [3, 4, 5]
    if int(bars_number) not in [3, 4, 5]:
        return apology("NUMBER OF BARS MUST BE 3, 4 OR 5")

    # optimize type somehow isn't distance or time
    if optimize_type not in ["distance", "time_required"]:
        return apology("WRONG OPTIMIZE TYPE")
