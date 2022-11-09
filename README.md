![isea tests](https://github.com/team-3-cs633/isea-backend/actions/workflows/testing.yml/badge.svg)
![](https://img.shields.io/badge/coverage-70%25-orange)


# isea-backend
The backend repository for isea

## Setup

1. `git clone git@github.com:team-3-cs633/isea-backend.git`
2. `cd isea-backend`
3. `python3 -m venv venv`
4. `source ./venv/bin/activate`
5. `pip install -r requirements.txt`
6. `pip install pipenv black pytest`

## Running  

Run `python3 ./src/app.py`

## Testing  

Run `python3 -m pytest`

## Formatting 

Before creating a pull request run `pipenv run black .` to format the repository

## Table Diagram
![Table Diagram](./img/table_diagram.png)

## Endpoints
**Users**   
→ **/users GET** : Get all users    
→ **/users POST** : Create a user   
→ **/users DELETE** : Delete a user   
→ **/users/{id} GET** : Get a user    
→ **/users/{id}/favorite GET** : Get a users favorite events    
→ **/users/{id}/registration GET** : Get a users event registrations    
→ **/users/{id}/suggestion GET** : Get a users event suggestions   
→ **/users/login POST** : Login a user    
→ **/users/roles GET** : Get user roles   
→ **/users/roles POST** : Create a user role    

**Events**    
→ **/events GET** : Get all events    
→ **/events POST** : Create an event    
→ **/events DELETE** : Delete an event   
→ **/events/{id} GET** : Get an event   
→ **/events/{id} POST** : Update an event   
→ **/events/registration POST** : Register to an event    
→ **/events/registration/{id} POST** : Unregister from an event   
→ **/events/favorite POST** : Favorite an event   
→ **/events/favorite/{id} POST** : Remove a favorite    
→ **/events/share POST** : Share an event   
→ **/events/{id}/metrics GET** : Get an events metrics   
