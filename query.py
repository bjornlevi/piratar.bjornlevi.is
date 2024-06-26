import sqlite3

def fetch_speaking_time():
    # Connect to the SQLite database
    conn = sqlite3.connect('thing.db')  # Ensure the database path is correct
    cursor = conn.cursor()

    # SQL query to fetch total speaking time per 'raedumadur' where 'mal_tegund' is 'ft'
    query = '''
    SELECT 
        raedumadur, 
        SUM(strftime('%s', raeda_lauk) - strftime('%s', raeda_hofst)) as total_seconds
    FROM 
        raedur
    WHERE 
        mal_tegund = "ft"
    GROUP BY 
        raedumadur
    '''

    cursor.execute(query)

    # Fetch all results
    results = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Print results
    for raedumadur, total_seconds in results:
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"{raedumadur} spoke for {hours} hours, {minutes} minutes and {seconds} seconds.")

# Call the function to execute and print results
fetch_speaking_time()
