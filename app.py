from flask import Flask, render_template, request, url_for, flash, redirect, abort
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = '6854973723b9bafcccc55af7816a98956e6b3d278572c340'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_recipe(recipe_id):
    conn = get_db_connection()
    recipe = conn.execute('SELECT * FROM recipe WHERE id = ?',
                        (recipe_id,)).fetchone()
    conn.close()
    if recipe is None:
        abort(404)
    return recipe

def checkDiet(list, allergies):
    allergy = allergies.lower().split()
    ingredients = list.lower().split()

    for ingredient in ingredients:
        if ingredient in allergy:
            return True
        
    return False
    
            
    


@app.route('/')
def home():
    conn = get_db_connection()
    conn.close()
    return render_template('home.html')

@app.route('/recipes')
def recipes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM recipe JOIN ingredients ON recipe.id = ingredients.id JOIN directions ON recipe.id = directions.id')
    items = cursor.fetchall()
    conn.close()
    return render_template('recipe.html', items=items)   

@app.route('/recipekeeper')
def recipekeeper():
    return render_template('recipekeeper.html')     

@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        meal = request.form['meal']
        difficulty = request.form['difficulty']
        diet = request.form['diet']
        list = request.form['list']
        steps = request.form['steps']
        time = request.form['time']

        if not id:
            flash('ID is required!')
        elif not name:
            flash('Name is required!')
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO recipe (id, name, meal, difficulty, diet) VALUES (?, ?, ?, ?, ?)',
                         (id, name, meal, difficulty, diet))
            cursor.execute('INSERT INTO ingredients (id, list) VALUES (?, ?)',
                         (id, list))
            cursor.execute('INSERT INTO directions (id, steps, time) VALUES (?, ?, ?)',
                         (id, steps, time))
            conn.commit()
            conn.close()
            return redirect(url_for('recipes'))
    
    return render_template('add.html')

@app.route('/<int:id>/change', methods=('GET', 'POST'))
def change(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM recipe JOIN ingredients ON recipe.id = ingredients.id JOIN directions ON recipe.id = directions.id WHERE recipe.id = ?', (id,))
    recipe = cursor.fetchone()
    conn.close()

    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        meal = request.form['meal']
        difficulty = request.form['difficulty']
        diet = request.form['diet']
        list = request.form['list']
        steps = request.form['steps']
        time = request.form['time']

        if not id:
            flash('ID is required!')
        elif not name:
            flash('Name is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE recipe SET name = ?, meal = ?, difficulty = ?, diet = ? WHERE id = ?',
                         (name, meal, difficulty, diet, id))
            conn.execute('UPDATE ingredients SET list = ? WHERE id = ?',
                        (list, id ))
            conn.execute('UPDATE directions SET steps = ?, time = ? WHERE id = ?',
                        (steps, time, id ))
            conn.commit()
            conn.close()
            return redirect(url_for('recipes'),)
    return render_template('change.html', recipe=recipe)

@app.route('/<int:id>/delete', methods=('GET', 'POST'))
def delete(id):
    recipe = get_recipe(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM recipe WHERE id = ?',(id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(recipe['name']))
    return redirect(url_for('recipes'))

@app.route('/search', methods=('GET', 'POST'))
def search():
    conn = get_db_connection()
    cursor = conn.cursor()
    id_query = request.form.get('id_query')
    if not id_query:
        id_query = '%'
    name_query = request.form.get('name_query')
    if not name_query:
        name_query = '%'
    meal_query = request.form.get('meal_query')
    if not meal_query:
        meal_query = "%"
    difficulty_query = request.form.get('difficulty_query')
    if not difficulty_query:
        difficulty_query = "%"
    diet_query = request.form.get('diet_query')
    if not diet_query:
        diet_query = "%"
    list_query = request.form.get('list_query')
    if not list_query:
        list_query = "%"
    steps_query = request.form.get('steps_query')
    if not steps_query:
        steps_query = "%"
    time_query = request.form.get('time_query')
    if not time_query:
        time_query = "%"
    if id_query == "%" and name_query == "%" and meal_query == "%" and difficulty_query == "%" and diet_query == "%" and list_query == "%" and steps_query == "%" and time_query == "%": 
        flash('Enter a search query')
        return render_template('search.html')
    else:
        cursor.execute('SELECT * '
                       'FROM recipe JOIN ingredients ON recipe.id = ingredients.id '
                       'JOIN directions ON recipe.id = directions.id '
                        'WHERE recipe.id LIKE ? '
                        'AND recipe.name LIKE ? '
                        'AND (recipe.meal IS NULL or recipe.meal LIKE ?) '
                        'AND (recipe.difficulty IS NULL or recipe.difficulty LIKE ?) '
                        'AND (recipe.diet IS NULL or recipe.diet LIKE ?) '
                        'AND (ingredients.list IS NULL or ingredients.list LIKE ?) '
                        'AND (directions.steps IS NULL or directions.steps LIKE ?) '
                        'AND (directions.time IS NULL or directions.time LIKE ?)',
                    (id_query, f'%{name_query}%', meal_query, difficulty_query, diet_query, f'%{list_query}%', f'%{steps_query}%', time_query))
        items = cursor.fetchall()
        conn.close()
        if not items:
            flash('No recipes match your query')
            return render_template('search.html')
        
        #allergen check
        allergies = request.form['allergies']
        allergen_recipes = []
        if allergies:
            for item in items:
                if (checkDiet(item['list'], allergies)):
                    allergen_recipes.append(item['name'])
            if(len(allergen_recipes) > 0):
                flash(f"Allergen detected in the following recipes: {', '.join(allergen_recipes)}") 
            
    return render_template('recipe.html', items=items)

@app.route('/advancedsearch', methods=('GET', 'POST'))
def advancedsearch():
    conn = get_db_connection()
    cursor = conn.cursor()
    ingredients_query = request.form.get('ingredients_query')
    if not ingredients_query:
        flash('Enter a search query')
        return render_template('advancedsearch.html')
    else:
        ingredients_list = ingredients_query.split(",")
        search_string = "%{}%".format("%".join(ingredients_list))
        cursor.execute('SELECT * FROM recipe JOIN ingredients ON recipe.id = ingredients.id '
                       'JOIN directions ON recipe.id = directions.id WHERE list LIKE ?',
                        (search_string,))
        items = cursor.fetchall()
        print(items)
        conn.close()
        if not items:
            flash('No recipes match your query')
            return render_template('advancedsearch.html')
    flash('You can make these recipes with your ingredients on hand:')
    return render_template('recipe.html', items=items)


if __name__ == '__main__':
    app.run(debug=True)

