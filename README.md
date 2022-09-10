## Task for Django Developer @zookeep

## Project specification

Specifications The ice cream truck is selling many food items: Ice Creams, Shaved Ice, and also Snack bars!
Each one of these food items has a price and a name. An Ice cream has many flavors: Chocolate, Pistachio, Strawberry and
Mint. The Ice cream truck has a limited amount of Ice creams, Shaved ice and Chocolate bars of course. The ice cream
truck has many customers. They come and buy a specific amount of food. Each time they buy something, the truck owner
should say "ENJOY!". If they try to buy more than what the ice cream truck has in stock, then the ice cream truck owner
should respond with "SORRY!". You'll build that ice cream truck as an API. The API should have a simple endpoint to buy
a specific food from the ice cream truck. There should also be another endpoint that gives the inventory of the ice
cream truck, and the total amount of money the ice cream truck has made. Feel free to add more endpoints you consider
necessary for an ice cream truck with customers. The quantity and price of each food item in the ice cream truck is up
to you. You'll make a simple test, so I can confirm it works easily. Try to build it so that it's scalable, so when the
ice cream truck gets famous they can open a franchise and have many ice cream trucks!

## PROJECT DIRECTORY OUTLINE

The project is being modularized to 3 apps which are located inside the apps folder directory.

1. config folder: This folder contains the core system settings such as the settings.py, wsgi.py, and urls.py
2. apps folder: This folder contains each of the app on the system such:
    1. core app: This app handles the user registration and all related activities of a particular user
    2. store app: This app handles the Ice cream inventory.
    3. order app: This app handles all activities relating to ice cream ordering

#

## HOW TO SET UP THE PROJECT

1. Clone the project to your local directory.
2. Create a virtualenv and install the project requirement that is located inside requirement.txt using
   ```
    pip install -r requirements.txt
    ```

3. Copy the .env_sample into .env and set the following variable
   ```
    DB_USER=
    DB_PASSWORD=
    DB_NAME=
    DB_ENGINE='django.db.backends.postgresql'
    ```
4. Setup the database table by running the command below
    ```
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Create a super-admin by running
    ```
   python manage.py createsuperuser
   ```
6. run the project by running the command below
    ```
   python manage.py runserver
   ```

```
 Viola!!! visit 127.0.0.1:8000 to access the swagger ui
```

## TO RUN THE TEST SUITE

To run the test suite for the project kindly run the below command in your terminal

```
   pytest
```