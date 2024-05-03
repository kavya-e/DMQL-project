from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import psycopg2.extras

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            dbname='project',
                            user='postgres',
                            password='Abcd.kav1')
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    table_name = 'athletesprofile'  # Default table
    records = None
    error = request.args.get('error', None)
    success = request.args.get('success', None)
    join_query = request.args.get('join_query', None)
    if join_query:
        try:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(join_query)
            records = cur.fetchall()
            cur.close()
            conn.close()
        except psycopg2.Error as e:
            error = f"Error executing join query: {str(e)}"
    elif request.method == 'POST':
        table_name = request.form.get('table_name', 'athletesprofile')
        try:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(f'SELECT * FROM {table_name};')
            records = cur.fetchall()
            cur.close()
            conn.close()
        except psycopg2.Error as e:
            error = f"Error accessing table {table_name}: {str(e)}"
    return render_template('index.html', records=records, table_name=table_name, error=error, success=success, join_query=join_query)

@app.route('/insert', methods=['POST'])
def insert():
    table_name = request.form['insert_table_name']
    values = request.form['insert_values'].split(',')
    values_list = [v.strip().strip("'").strip('"') for v in values]
    placeholders = ','.join(['%s'] * len(values_list))
    query = f"INSERT INTO {table_name} VALUES ({placeholders})"
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, values_list)
        conn.commit()
        cur.close()
        conn.close()
        success_message = f"Record inserted successfully into {table_name}"
        return redirect(url_for('index', success=success_message))
    except psycopg2.Error as e:
        error_message = f"Error inserting into table {table_name}: {str(e)}"
        return redirect(url_for('index', error=error_message))

@app.route('/delete', methods=['POST'])
def delete():
    table_name = request.form['delete_table_name']
    condition = request.form['delete_condition']
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query = f"DELETE FROM {table_name} WHERE {condition};"
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()
        success_message = f"Records deleted successfully from {table_name}"
        return redirect(url_for('index', success=success_message))
    except psycopg2.Error as e:
        error_message = f"Error deleting from table {table_name}: {str(e)}"
        return redirect(url_for('index', error=error_message))

@app.route('/update', methods=['POST'])
def update():
    table_name = request.form['update_table_name']
    set_clause = request.form['update_set_clause']
    condition = request.form['update_condition']
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition};"
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()
        success_message = f"Records updated successfully in {table_name}"
        return redirect(url_for('index', success=success_message))
    except psycopg2.Error as e:
        error_message = f"Error updating table {table_name}: {str(e)}"
        return redirect(url_for('index', error=error_message))

@app.route('/truncate', methods=['POST'])
def truncate():
    table_name = request.form['truncate_table_name']
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"TRUNCATE TABLE {table_name};")
        conn.commit()
        cur.close()
        conn.close()
        success_message = f"Table {table_name} truncated successfully"
        return redirect(url_for('index', success=success_message))
    except psycopg2.Error as e:
        error_message = f"Error truncating table {table_name}: {str(e)}"
        return redirect(url_for('index', error=error_message))

@app.route('/join', methods=['POST'])
def join():
    join_query = request.form['join_query']
    return redirect(url_for('index', join_query=join_query))

if __name__ == '__main__':
    app.run(debug=True)
