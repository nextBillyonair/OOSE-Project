# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)

## Iteration 6 - 2017-12-19
- Requests
	- Requests Popup now has tags
- Discover View
	- Preserves ordering of nearby users
	- Tags are shown in popup
	- New Layout choice - Tile (original) vs List with tags
	- Button Group in header to decide between layouts
	- List View - lists users with avatar, first tag in title, second and third as subtitle
- New Algorithms for ordering nearby users
	- Preprocessing Algorithms
		- Spell Checker
		- Remove Stop Words
	- Scoring Algorithms
		- Jaccard Index
		- Dice's Coefficient
		- FuzzyWuzzy - Levenshtein distance (Edit Distance)
- Chat View Avatar Popup has tags
- Settings:
	- 3 Tag Input Boxes
	- bigger avatar
	- changed time default to 6 hours in backend
	- Alert for logout
	- Alert for deactivate
- Launch Screen and Login Title adjusted
- DiscoverView Popup, on Press, now removes keyboard
- Chat View Avatar Popup now dismisses on touch
- Frontend View import statements have been cleaned up
- Refactor Out Features Calculation and Scoring of Features Vectors
- Add logging of user behavior
- Write evaluation metrics and simple machine learning model

## Iteration 5 - 2017-12-08
- Refactored Styling code in Frontend Views
- iPhone Modeling Restucture for Every View (5, Regular, Plus, X)
- Changed all popup buttons to text, to drive home the purpose of each button
- Styling to make a chat appear inactive
- Implemented the Radius and Time algorithms
- Small text to tell the user more information on the slider values for radius and time (X hop(s), Y hour(s))
- In Chat View, can click on avatar to display User Avatar
- Added Refresh button in Chat View Menu
- Added Option to Take Chat offline in Chat View Menu
- Discover View menu to select amount of people to display
- New Settings view layout with sliders, user picture, logout, deactivate, blocked users link
- Activity Indicators when waiting for server response
- Better Error Messages on the frontend
- Refactored tests, increased coverage
- Refactored backend views
- New styling for popups
- Restructure files and directories
- Proper storage of documentation
- Stores who is nearby in backend
  - Can lookup who is nearby someone with time and radius parameters
  - Can give permission to communicate even if you are not connected in the graph
- Optimized graph algorithm to store results in session cache

## Iteration 4 - 2017-11-17
- Default Views for when nothing to render (No users available)
- Random Chat Names for fun
- Menu Button for Chat View
- Can Edit Chat Name
- Can block user from within Chat
- Blocked Users is now stylistically similiar to Discover
- Added Dynamic Styling for Unread Messages in Chats(Messages) View
- Added subtitling for message preview in Chats View
- Deployed on Heroku
- Refresh Buttons on Discover, Chats, and Blocked Users
- Animated Popup transitions when the keyboard is selected (Moves out of the way)
- Facebook Authentication in the Backend
- Travis CI setup
- Avatars in the chat, Chat name displayed on the top.
- Keyboard dismisses when not wanted (tap outside popup, or chat)

## Iteration 3 - 2017-10-30
### Added
- View for login
- View for discovering nearby people
- View for current chats
- View for chatting to a specific person
- View for sending/receiving a request
- View for settings
- View for blocked users
- User login/logout through Facebook
- See nearby users with Facebook Profile Picture
- Backend using Flask, SocketIO, and Postgres created
- Backend testing has begun

### Removed
- Bluetooth mesh network for group chats
- Bluetooth requirement for messaging
