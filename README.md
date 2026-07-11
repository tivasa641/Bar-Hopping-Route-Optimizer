# Bar Hopping Route Optimizer
#### Video Demo:  <https://youtu.be/D3kPOv-WJz0>
#### Description:
## Project Description
### Core Features:
This project is a Tainan Bar Hopping route optimization tool. Users input their budget, how many bars they want to visit (three to five), what time they go to the first and last bar, which day of the week they want to go bar hopping, what the first and last bars are called, and whether they want to optimize by distance or time. The program will then select intermediate stops from the remaining 17 bars to optimize the route. The final result will display the estimated cost, the optimal route, and what the route looks like on Google Maps.

### Additional Feature (1): Bar List
Users can view the bar list in the database, the bars' operating hours, last order times, and fixed rest days.

### Additional Feature (2): Provide Examples
Provides three sample routes for special needs, which are the limited budget route, classic cocktail route, and epic night out route, which can also bring some ideas to the users.

### Additional Feature (3): Verify User Input
The program validates several possible input problems, including cases where the user did not input any data, the first or last bar is not in the database, the first bar and the last bar are duplicated, the first bar or the last bar is not open on that day, the bar is not open yet when going to the first bar, missed the last order time when going to the last bar, the number of bars they want to go to is not 3, 4, or 5, and the budget is insufficient.


## File Descriptions
* **requirements.txt**:Lists the libraries needed for the project.

* **app.py**: Responsible for the backend processing of all functions.
The functions and algorithms are roughly as follows:
  * `index()`:Responsible for core features and additional feature (3).
    1. Get and verify user input.
    2. Calculate the route combinations of all open bars on that day, and eliminate combinations that do not meet the user's budget.
    3. Execute optimization.
    4. Pass the optimization result to the frontend settlement screen.
  * `list()`:Responsible for additional feature (1).
    1. Retrieve the bar list from the database, the bars' operating hours, last order times, and fixed rest days.
    2. Change the data into a new dictionary structure.
    3. Pass the data to the frontend.
  * `idea()`:Responsible for additional feature (2).

* **functions.py**: Responsible for abstracting and encapsulating the complex logic needed by app.py. The functions and algorithms are roughly as follows:
  * `apology()`:Handles the web rendering of error messages (this is adopted from the Finance problem, I only changed the cat picture).
  * `verify()`:Verifies the rationality of the user's input.
  * `check_bar_exist()`:Checks if the inputted bars exist in the database.
  * `combinations()`:Generate all possible combinations of nodes, and eliminate combinations the user cannot afford.
    1. Find all possible combinations where the first one is the start bar and the last one is the end bar.
    2. Filter out the routes that exceed the user’s budget.
    3. Return all feasible routes as a list.
  * `optimize()`:Calculate best bar hopping route
    1. Find all permutations that first one is the start bar and last one is the end bar
    2. Execute loop:
        1. Calculate the total weight of the permutation.
        2. If the total weight is smaller than the current minimum total weight, set it as the minimum total weight.
    3. Calculate the estimated cost of the best route.
    4. Pack the best permutation, minimum total weight, and estimated cost into a dictionary and return it.

* **bar.db**: The SQLite database of the project. Contains 3 tables:
  * `bars`:Stores the names, latitudes, longitudes, and average cocktail prices of 19 bars.
  * `opening_hours`:Stores the seven-day operating hours and last order times of the bars.
  * `distances`:Stores the distance between two bars and the estimated walking time. Note: Because the distance and required time from A to B and B to A are slightly different on Google Maps, I treat the two as different situations, so this table has 19 * 18 = 342 entries of data in total.

* **distances.py**: A one-time Python program whose purpose is to calculate the distance and estimated walking time between two bars, and write it into the distances table of the database. Algorithm is roughly:
    1. Define a function to connect with the Distance Matrix API provided by Google. The input is the latitude and longitude of one bar and the latitudes and longitudes of other bars. The output is the distance and estimated walking time from this bar to the other bars.
    2. Execute loop:
        1. Select one bar as the starting point.
        2. Store the locations of other bars in memory as strings.
        3. Execute the function.
        4. Save into the database.

* **layout.html**: Responsible for the UI skeleton shared across the entire site. Mainly refers to the layout.html from the Finance problem set, and changed the Bootstrap theme.
* **index.html**: Responsible for the frontend processing of the core features, allowing the user to input their needs.
* **result.html**: Responsible for displaying the settlement screen, and connecting with the Maps JavaScript API and Directions API provided by Google through JavaScript.
    1. Display estimated cost.
    2. Display the best route using a list.
    3. Connect with the Maps JavaScript API and Directions API provided by Google.
    4. Display what the best route looks like on Google Maps.
* **list.html**: Responsible for the frontend processing of additional feature (1), using a double loop to print out the table.
* **idea.html**: Responsible for the frontend processing of additional feature (2), using Bootstrap's card component.
* **apology.html**:Also adopted from the Finance problem set.

## Design Choices
### I listed a plan that I eliminated, and the reasons for elimination:
### Plan: The user inputs an acceptable budget range, and whether they prefer to spend less money but walk more, or spend more money but walk less.
At the very beginning, my project was designed for users to input an acceptable budget range, and whether they preferred to spend less money but walk more, or spend more money but walk less, rather than asking the user how much they can spend at most like it does now. The reason for eliminating this plan is that I realized the optimization algorithm would have to consider two incomparable weights, which would be much more complex than the current optimization algorithm that has a unique solution. Considering this is my first time independently developing a full-stack project, I decided to choose a more conservative plan with a unique solution, and supplemented the limited budget route in the idea subpage to make up for the lack of this functionality.

## How to Run
The steps to execute this program are as follows:
1. Open the terminal and execute "pip install -r requirements.txt" to install the required libraries.
2. Go to Google Cloud Console to register your own API (the API provided with the program has been set to only be usable by my IP address).
3. The API must include the Maps JavaScript API and Directions API features.
4. Go to line 88 of result.html and change the key to your API key.
5. Start the Flask server.