# Importing the Flask Framework

from flask import *
import database
import configparser


# appsetup

page = {}
session = {}

# Initialise the FLASK application
app = Flask(__name__)
app.secret_key = 'SoMeSeCrEtKeYhErE'


# Debug = true if you want debug output on error ; change to false if you dont
app.debug = True


# Read my unikey to show me a personalised app
config = configparser.ConfigParser()
config.read('config.ini')
dbuser = config['DATABASE']['user']
portchoice = config['FLASK']['port']
if portchoice == '10000':
    print('ERROR: Please change config.ini as in the comments or Lab instructions')
    exit(0)

session['isadmin'] = False

###########################################################################################
###########################################################################################
####                                 Database operative routes                         ####
###########################################################################################
###########################################################################################



#####################################################
##  INDEX
#####################################################

# What happens when we go to our website (home page)
@app.route('/')
def index():
    # If the user is not logged in, then make them go to the login page
    if( 'logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    page['username'] = dbuser
    page['title'] = 'Welcome'
    return render_template('welcome.html', session=session, page=page)

#####################################################
# User Login related                        
#####################################################
# login
@app.route('/login', methods=['POST', 'GET'])
def login():
    page = {'title' : 'Login', 'dbuser' : dbuser}
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        # Get our login value
        val = database.check_login(request.form['userid'], request.form['password'])
        print(val)
        print(request.form)
        # If our database connection gave back an error
        if(val == None):
            errortext = "Error with the database connection."
            errortext += "Please check your terminal and make sure you updated your INI files."
            flash(errortext)
            return redirect(url_for('login'))

        # If it's null, or nothing came up, flash a message saying error
        # And make them go back to the login screen
        if(val is None or len(val) < 1):
            flash('There was an error logging you in')
            return redirect(url_for('login'))

        # If it was successful, then we can log them in :)
        print(val[0])
        session['name'] = val[0]['firstname']
        session['userid'] = request.form['userid']
        session['logged_in'] = True
        session['isadmin'] = val[0]['isadmin']
        return redirect(url_for('index'))
    else:
        # Else, they're just looking at the page :)
        if('logged_in' in session and session['logged_in'] == True):
            return redirect(url_for('index'))
        return render_template('index.html', page=page)

# logout
@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You have been logged out')
    return redirect(url_for('index'))



########################
#List All Items#
########################

@app.route('/users')
def list_users():
    '''
    List all rows in users by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    users_listdict = database.list_users()

    # Handle the null condition
    if (users_listdict is None):
        # Create an empty list and show error message
        users_listdict = []
        flash('Error, there are no rows in users')
    page['title'] = 'List Contents of users'
    return render_template('list_users.html', page=page, session=session, users=users_listdict)  

########################
#List Single Items#
########################


@app.route('/users/<userid>')
def list_single_users(userid):
    '''
    List all rows in users that match a particular id attribute userid by calling the 
    relevant database calls and pushing to the appropriate template
    '''

    # connect to the database and call the relevant function
    users_listdict = None
    users_listdict = database.list_users_equifilter("userid", userid)

    # Handle the null condition
    if (users_listdict is None or len(users_listdict) == 0):
        # Create an empty list and show error message
        users_listdict = []
        flash('Error, there are no rows in users that match the attribute "userid" for the value '+userid)
    page['title'] = 'List Single userid for users'
    return render_template('list_users.html', page=page, session=session, users=users_listdict)


########################
#List Search Items#
########################

@app.route('/consolidated/users')
def list_consolidated_users():
    '''
    List all rows in users join userroles 
    by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    users_userroles_listdict = database.list_consolidated_users()

    # Handle the null condition
    if (users_userroles_listdict is None):
        # Create an empty list and show error message
        users_userroles_listdict = []
        flash('Error, there are no rows in users_userroles_listdict')
    page['title'] = 'List Contents of Users join Userroles'
    return render_template('list_consolidated_users.html', page=page, session=session, users=users_userroles_listdict)

@app.route('/user_stats')
def list_user_stats():
    '''
    List some user stats
    '''
    # connect to the database and call the relevant function
    user_stats = database.list_user_stats()

    # Handle the null condition
    if (user_stats is None):
        # Create an empty list and show error message
        user_stats = []
        flash('Error, there are no rows in user_stats')
    page['title'] = 'User Stats'
    return render_template('list_user_stats.html', page=page, session=session, users=user_stats)

@app.route('/users/search', methods=['POST', 'GET'])
def search_users_byname():
    '''
    List all rows in users that match a particular name
    by calling the relevant database calls and pushing to the appropriate template
    '''
    if(request.method == 'POST'):

        search = database.search_users_customfilter(request.form['searchfield'],"~",request.form['searchterm'])
        print(search)
        
        users_listdict = None

        if search == None:
            errortext = "Error with the database connection."
            errortext += "Please check your terminal and make sure you updated your INI files."
            flash(errortext)
            return redirect(url_for('index'))
        if search == None or len(search) < 1:
            flash(f"No items found for search: {request.form['searchfield']}, {request.form['searchterm']}")
            return redirect(url_for('index'))
        else:
            
            users_listdict = search
            # Handle the null condition'
            print(users_listdict)
            if (users_listdict is None or len(users_listdict) == 0):
                # Create an empty list and show error message
                users_listdict = []
                flash('Error, there are no rows in users that match the searchterm '+request.form['searchterm'])
            page['title'] = 'Users search by name'
            return render_template('list_users.html', page=page, session=session, users=users_listdict)
            

    else:
        return render_template('search_users.html', page=page, session=session)
        
@app.route('/users/delete/<userid>')
def delete_user(userid):
    '''
    Delete a user
    '''
    # connect to the database and call the relevant function
    resultval = database.delete_user(userid)
    
    page['title'] = f'List users after user {userid} has been deleted'
    return redirect(url_for('list_consolidated_users'))
    
@app.route('/users/update', methods=['POST','GET'])
def update_user():
    """
    Update details for a user
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Update user details'

    userslist = None

    print("request form is:")
    newdict = {}
    print(request.form)

    validupdate = False
    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that at least one value is available:
        if ('userid' not in request.form):
            # should be an exit condition
            flash("Can not update without a userid")
            return redirect(url_for('list_users'))
        else:
            newdict['userid'] = request.form['userid']
            print("We have a value: ",newdict['userid'])

        if ('firstname' not in request.form):
            newdict['firstname'] = None
        else:
            validupdate = True
            newdict['firstname'] = request.form['firstname']
            print("We have a value: ",newdict['firstname'])

        if ('lastname' not in request.form):
            newdict['lastname'] = None
        else:
            validupdate = True
            newdict['lastname'] = request.form['lastname']
            print("We have a value: ",newdict['lastname'])

        if ('userroleid' not in request.form):
            newdict['userroleid'] = None
        else:
            validupdate = True
            newdict['userroleid'] = request.form['userroleid']
            print("We have a value: ",newdict['userroleid'])

        if ('password' not in request.form):
            newdict['password'] = None
        else:
            validupdate = True
            newdict['password'] = request.form['password']
            print("We have a value: ",newdict['password'])

        print('Update dict is:')
        print(newdict, validupdate)

        if validupdate:
            #forward to the database to manage update
            userslist = database.update_single_user(newdict['userid'],newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        else:
            # no updates
            flash("No updated values for user with userid")
            return redirect(url_for('list_users'))
        # Should redirect to your newly updated user
        return list_single_users(newdict['userid'])
    else:
        return redirect(url_for('list_consolidated_users'))

######
## Edit user
######
@app.route('/users/edit/<userid>', methods=['POST','GET'])
def edit_user(userid):
    """
    Edit a user
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin
    if not session.get('isadmin', False):
        flash('You do not have the necessary permissions to perform this action.')
        return redirect(url_for('list_airports'))

    page['title'] = 'Edit user details'

    users_listdict = None
    users_listdict = database.list_users_equifilter("userid", userid)

    # Handle the null condition
    if (users_listdict is None or len(users_listdict) == 0):
        # Create an empty list and show error message
        users_listdict = []
        flash('Error, there are no rows in users that match the attribute "userid" for the value '+userid)

    userslist = None
    print("request form is:")
    newdict = {}
    print(request.form)
    user = users_listdict[0]
    validupdate = False

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that at least one value is available:
        if ('userid' not in request.form):
            # should be an exit condition
            flash("Can not update without a userid")
            return redirect(url_for('list_users'))
        else:
            newdict['userid'] = request.form['userid']
            print("We have a value: ",newdict['userid'])

        if ('firstname' not in request.form):
            newdict['firstname'] = None
        else:
            validupdate = True
            newdict['firstname'] = request.form['firstname']
            print("We have a value: ",newdict['firstname'])

        if ('lastname' not in request.form):
            newdict['lastname'] = None
        else:
            validupdate = True
            newdict['lastname'] = request.form['lastname']
            print("We have a value: ",newdict['lastname'])

        if ('userroleid' not in request.form):
            newdict['userroleid'] = None
        else:
            validupdate = True
            newdict['userroleid'] = request.form['userroleid']
            print("We have a value: ",newdict['userroleid'])

        if ('password' not in request.form):
            newdict['password'] = None
        else:
            validupdate = True
            newdict['password'] = request.form['password']
            print("We have a value: ",newdict['password'])

        print('Update dict is:')
        print(newdict, validupdate)

        if validupdate:
            #forward to the database to manage update
            userslist = database.update_single_user(newdict['userid'],newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        else:
            # no updates
            flash("No updated values for user with userid")
            return redirect(url_for('list_users'))
        # Should redirect to your newly updated user
        return list_single_users(newdict['userid'])
    else:
        # assuming GET request, need to setup for this
        return render_template('edit_user.html',
                           session=session,
                           page=page,
                           userroles=database.list_userroles(),
                           user=user)


######
## add items
######

    
@app.route('/users/add', methods=['POST','GET'])
def add_user():
    """
    Add a new User
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Add user details'

    userslist = None
    print("request form is:")
    newdict = {}
    print(request.form)

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that all values are available:
        if ('userid' not in request.form):
            # should be an exit condition
            flash("Can not add user without a userid")
            return redirect(url_for('add_user'))
        else:
            newdict['userid'] = request.form['userid']
            print("We have a value: ",newdict['userid'])

        if ('firstname' not in request.form):
            newdict['firstname'] = 'Empty firstname'
        else:
            newdict['firstname'] = request.form['firstname']
            print("We have a value: ",newdict['firstname'])

        if ('lastname' not in request.form):
            newdict['lastname'] = 'Empty lastname'
        else:
            newdict['lastname'] = request.form['lastname']
            print("We have a value: ",newdict['lastname'])

        if ('userroleid' not in request.form):
            newdict['userroleid'] = 1 # default is traveler
        else:
            newdict['userroleid'] = request.form['userroleid']
            print("We have a value: ",newdict['userroleid'])

        if ('password' not in request.form):
            newdict['password'] = 'blank'
        else:
            newdict['password'] = request.form['password']
            print("We have a value: ",newdict['password'])

        print('Insert parametesrs are:')
        print(newdict)

        database.add_user_insert(newdict['userid'], newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        # Should redirect to your newly updated user
        print("did it go wrong here?")
        return redirect(url_for('list_consolidated_users'))
    else:
        # assuming GET request, need to setup for this
        return render_template('add_user.html',
                           session=session,
                           page=page,
                           userroles=database.list_userroles())

## Eunice Lee - Individual Codes Start Here

@app.route('/airports', methods=['GET'])
def list_airports():
    '''
    List all rows in airports by calling the relevant database calls and pushing to the appropriate template
    '''
    # Pagination
    requested_page = request.args.get('page', default=1, type=int)
    airport_per_page = 20
    offset = (requested_page - 1) * airport_per_page

    # Fetch valid IATA codes for the drop-down
    valid_iata_codes = database.dropdown_valid_iata_codes()

    # Get the selected IATA code from the request
    selected_iata_code = request.args.get('end_station', default=None)

    # Connect to the database and call the relevant function
    if selected_iata_code:
        airports_listdict = database.list_iatacode_dropdown(selected_iata_code)
        if not airports_listdict:
            flash('No airports found with the selected IATA code.')
    else:
        airports_listdict = database.list_airports_pagination(airport_per_page, offset)

    # Handle the null condition
    if not airports_listdict:
        airports_listdict = []
        flash('No airports found on this page.')
    page_info = {
        'title': f'List Contents of Airports (Page {requested_page})',
        'current_page': requested_page,
        'airport_per_page': airport_per_page
    }
    return render_template('list_airports.html', page=page_info, session=session, airports=airports_listdict, valid_iata_codes=valid_iata_codes)

@app.route('/airports/<airportid>')
def list_single_airport(airportid):
    '''
    List all rows in airports that match a particular id attribute airportid by calling the 
    relevant database calls and pushing to the appropriate template
    '''

    # connect to the database and call the relevant function
    airports_listdict = None
    airports_listdict = database.list_airports_equifilter("airportid", airportid)

    # Handle the null condition
    if (airports_listdict is None or len(airports_listdict) == 0):
        # Create an empty list and show error message
        airports_listdict = []
        flash('Error, there are no rows in airports that match the attribute "airportid" for the value '+airportid)
    page['title'] = 'List Single AirportID for airports'
    return render_template('list_airports.html', page=page, session=session, airports=airports_listdict)

@app.route('/airport_country_stats')
def list_airport_country_stats():
    '''
    List some airport country stats
    '''
    # connect to the database and call the relevant function
    airport_country_stats = database.list_airport_country_stats()

    # Handle the null condition
    if (airport_country_stats is None):
        # Create an empty list and show error message
        airport_country_stats = []
        flash('Error, there are no rows in airport_country_stats')
    page['title'] = 'Airport Statistics by Country'
    return render_template('list_airport_country_stats.html', page=page, session=session, airports=airport_country_stats)

@app.route('/airports/search', methods=['POST', 'GET'])
def search_airports_byID():
    '''
    List all rows in airports that match a particular airport ID
    by calling the relevant database calls and pushing to the appropriate template
    '''
    if(request.method == 'POST'):

        search = database.search_airports_byID(request.form['airportid'])
        print(search)
        
        airports_listdict = None

        if search == None:
            errortext = "Error with the database connection."
            errortext += "Please check your terminal and make sure you updated your INI files."
            flash(errortext)
            return redirect(url_for('index'))
        if search == None or len(search) < 1:
            flash(f"No items found for search: {request.form['airportid']}")
            return redirect(url_for('index'))
        else:
            
            airports_listdict = search
            # Handle the null condition'
            print(airports_listdict)
            if (airports_listdict is None or len(airports_listdict) == 0):
                # Create an empty list and show error message
                airports_listdict = []
                flash('Error, there are no rows in airports that match the searchterm '+request.form['airportid'])
            page['title'] = 'Airport search by ID'
            return render_template('list_airports.html', page=page, session=session, airports=airports_listdict)
            

    else:
        return render_template('search_airports.html', page=page, session=session)

@app.route('/airports/delete/<airportid>')
def delete_airport(airportid):
    '''
    Delete an airport
    '''
    try:
        resultval = database.delete_airport(airportid)
        
        if resultval is None:
            # If the airport couldn't be deleted due to a foreign key constraint
            flash(f"Airport with ID {airportid} cannot be deleted because it is referenced in other records.")
        else:
            flash(f"Airport with ID {airportid} has been successfully deleted.")
    
    except Exception as e:
        # If any unexpected error occurs, flash an error message
        flash(f"An error occurred while trying to delete the airport: {str(e)}")

    # After the operation, redirect to the list of airports
    return redirect(url_for('list_airports'))
    
@app.route('/airports/update', methods=['POST','GET'])
def update_airport():
    """
    Update details for an airport
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Update airport details'

    airportslist = None

    print("request form is:")
    newdict = {}
    print(request.form)

    validupdate = False
    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that at least one value is available:
        if ('airportid' not in request.form):
            # should be an exit condition
            flash("Can not update without an airport ID")
            return redirect(url_for('list_airports'))
        else:
            newdict['airportid'] = request.form['airportid']
            print("We have a value: ",newdict['airportid'])

        if ('name' not in request.form):
            newdict['name'] = None
        else:
            validupdate = True
            newdict['name'] = request.form['name']
            print("We have a value: ",newdict['name'])

        if ('iatacode' not in request.form):
            newdict['iatacode'] = None
        else:
            validupdate = True
            newdict['iatacode'] = request.form['iatacode']
            print("We have a value: ",newdict['iatacode'])

        if ('city' not in request.form):
            newdict['city'] = None
        else:
            validupdate = True
            newdict['city'] = request.form['city']
            print("We have a value: ",newdict['city'])

        if ('country' not in request.form):
            newdict['country'] = None
        else:
            validupdate = True
            newdict['country'] = request.form['country']
            print("We have a value: ",newdict['country'])

        print('Update dict is:')
        print(newdict, validupdate)

        if validupdate:
            #forward to the database to manage update
            airportslist = database.update_single_airport(newdict['airportid'],newdict['name'],newdict['iatacode'],newdict['city'],newdict['country'])
        else:
            # no updates
            flash("No updated values for airport with AirportID")
            return redirect(url_for('list_airports'))
        # Should redirect to your newly updated user
        return list_single_airport(newdict['airportid'])
    else:
        return redirect(url_for('list_airports'))

######
## Edit user
######
@app.route('/airports/edit/<airportid>', methods=['POST','GET'])
def edit_airport(airportid):
    """
    Edit an airport
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Edit airport details'

    airports_listdict = None
    airports_listdict = database.search_airports_byID(airportid)

    # Handle the null condition
    if (airports_listdict is None or len(airports_listdict) == 0):
        # Create an empty list and show error message
        airports_listdict = []
        flash('Error, there are no rows in airports that match the attribute "AirportID" for the value '+airportid)

    airportslist = None
    print("request form is:")
    newdict = {}
    print(request.form)
    airport = airports_listdict[0]
    validupdate = False

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that at least one value is available:
        if ('airportid' not in request.form):
            # should be an exit condition
            flash("Can not update without a Airport ID")
            return redirect(url_for('list_airports'))
        else:
            newdict['airportid'] = request.form['airportid']
            print("We have a value: ",newdict['airportid'])

        if ('name' not in request.form):
            newdict['name'] = None
        else:
            validupdate = True
            newdict['name'] = request.form['name']
            print("We have a value: ",newdict['name'])

        if ('iatacode' not in request.form):
            newdict['iatacode'] = None
        else:
            validupdate = True
            newdict['iatacode'] = request.form['iatacode']
            print("We have a value: ",newdict['iatacode'])

        if ('city' not in request.form):
            newdict['city'] = None
        else:
            validupdate = True
            newdict['city'] = request.form['city']
            print("We have a value: ",newdict['city'])

        if ('country' not in request.form):
            newdict['country'] = None
        else:
            validupdate = True
            newdict['country'] = request.form['country']
            print("We have a value: ",newdict['country'])

        print('Update dict is:')
        print(newdict, validupdate)

        if validupdate:
            #forward to the database to manage update
            airportslist = database.edit_airport(newdict['airportid'],newdict['name'],newdict['iatacode'],newdict['city'],newdict['country'])
        else:
            # no updates
            flash("No updated values for airport with AirportID")
            return redirect(url_for('list_airports'))
        # Should redirect to your newly updated airport
        return list_single_airports(newdict['airportid'])
    else:
        # assuming GET request, need to setup for this
        return render_template('edit_airport.html',
                           session=session,
                           page=page,
                           airports=airport)


######
## add items
######

    
@app.route('/airports/add', methods=['POST','GET'])
def add_airport():
    """
    Add a new airport
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Add airport details'

    airportslist = None
    print("request form is:")
    newdict = {}
    print(request.form)

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that all values are available:
        if ('airportid' not in request.form):
            # should be an exit condition
            flash("Can not add airport without an AirportID")
            return redirect(url_for('add_airport'))
        else:
            newdict['airportid'] = request.form['airportid']
            print("We have a value: ",newdict['airportid'])

        if ('name' not in request.form):
            newdict['name'] = 'Empty name'
        else:
            newdict['name'] = request.form['name']
            print("We have a value: ",newdict['name'])

        if ('iatacode' not in request.form):
            newdict['iatacode'] = 'Empty IATA code'
        else:
            newdict['iatacode'] = request.form['iatacode']
            print("We have a value: ",newdict['iatacode'])

        if ('city' not in request.form):
            newdict['city'] = 'Empty city'
        else:
            newdict['city'] = request.form['city']
            print("We have a value: ",newdict['city'])

        if ('country' not in request.form):
            newdict['country'] = 'Empty country'
        else:
            newdict['country'] = request.form['country']
            print("We have a value: ",newdict['country'])

        print('Insert parameters are:')
        print(newdict)

        database.add_airport(newdict['airportid'], newdict['name'],newdict['iatacode'],newdict['city'],newdict['country'])
        # Should redirect to your newly updated airport
        print("did it go wrong here?")
        return redirect(url_for('list_airports'))
    else:
        # assuming GET request, need to setup for this
        return render_template('add_airport.html',
                           session=session,
                           page=page)