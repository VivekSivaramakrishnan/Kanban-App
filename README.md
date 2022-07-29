## Simple Kanban App
**Kanban** is a simple task-scheduling methodology formulated by Taiichi Ohno from Toyota, Japan. It entails partitioning a board into lists, and each list is populated with it's appropriate tasks.

This repository is my work in creating a simple and functional Kanban application. It is my final project submission for the MAD-I project, a part of IITM's online Programming diploma.

## Technologies used
- **HTML, CSS, Javascript, Bootstrap, jinja2** - Client-side presentation tools
	- **Popper.js** (modals), **jQuery.js**
- **Python, Flask** - Back-end processing and web routing
	- **Flask SQLAlchemy** - Database management module
	- **Flask-Login, Hashlib** - Frameworks to facilitate login processes
	- **Flask-WTF, WTForms** - Form declaration and input handling
	- **Flask-RESTful** - API declaration, routing and handling
	- **Pandas, io.BytesIO** - To generate excel spreadsheet of data on the fly for further analysis

## DB Schema Design
![DB Schema](https://i.ibb.co/pZSLpvP/dbschema-light.png)

## API Design
Implemented using **Flask-RESTful**. A total of 5 resource classes were used. The following table describes the endpoints:
|Endpoint|Description|
|--|--|
|**/api/login**|Login user using **post** request|
|**/api/logout**|Logout user using **get** request|
|**/api/list**|**CRUD** operations on lists|
|**/api/task/{list_id}**|**CRUD** operations on tasks|
|**/api/stats**|**get** descriptive stats on tasks of current user's lists|

## Architectures and features
```
|───static
│   ├───ico / App icons
│   └───wallpapers / Wallpapers used in forms
├───templates / Jinja 2 Templates
│   ├───errors
│   ├───forms
│   ├───layouts
│   └───pages
```
.py files:
- **api.py** - API Resource definitions
- **app.py** - Controllers and Error Handlers
- **config.py** - Definitions of the Flask application's global variables
- **forms.py** - Form Class definitions and input validators
- **models.py** - SQLite database structure definitions
- **password.py** - MD5 Hashing solution for login framework
- **settings.py** - Instantiates app and db. Used to fix circular import issue.
