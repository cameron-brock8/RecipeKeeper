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

@app.route('/')
def home():
    conn = get_db_connection()
    conn.close()
    return "Hello Flask"

@app.route('/recipes')
def recipes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM recipe JOIN ingredients ON recipe.id = ingredients.id JOIN directions ON recipe.id = directions.id')
    items = cursor.fetchall()
    conn.close()
    return render_template('recipe.html', items=items)    

@app.route('/ingredients')
def ingredients():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM recipe JOIN ingredients ON recipe.id = ingredients.id JOIN directions ON recipe.id = directions.id')
    items = cursor.fetchall()
    conn.close()
    return render_template('ingredients.html', items=items)    

@app.route('/directions')
def directions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM recipe JOIN ingredients ON recipe.id = ingredients.id JOIN directions ON recipe.id = directions.id')
    items = cursor.fetchall()
    conn.close()
    return render_template('directions.html', items=items)   

@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        meal = request.form['meal']
        difficulty = request.form['difficulty']
        diet = request.form['diet']
        style = request.form['style']
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
            cursor.execute('INSERT INTO recipe (id, name, meal, difficulty, diet, style) VALUES (?, ?, ?, ?, ?, ?)',
                         (id, name, meal, difficulty, diet, style))
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
    cursor.execute('SELECT * FROM recipe JOIN ingredients ON recipe.id = ingredients.id JOIN directions ON recipe.id = directions.id')
    recipe = cursor.fetchone()
    conn.close()

    if request.method == 'POST':
        name = request.form['name']
        meal = request.form['meal']
        difficulty = request.form['difficulty']
        diet = request.form['diet']
        style = request.form['style']
        list = request.form['list']
        steps = request.form['steps']
        time = request.form['time']

        if not id:
            flash('ID is required!')
        elif not name:
            flash('Name is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE recipe SET name = ?, meal = ?, difficulty = ?, diet = ?, style = ? WHERE id = ?',
                         (name, meal, difficulty, diet, style, id))
            conn.execute('UPDATE ingredients SET list = ? WHERE id = ?',
                        (list, id ))
            conn.execute('UPDATE directions SET steps = ?, time = ? WHERE id = ?',
                        (steps, time, id ))
            conn.commit()
            conn.close()
            return redirect(url_for('recipes'))
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


if __name__ == '__main__':
    app.run(debug=True)

