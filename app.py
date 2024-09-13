import os
from flask import Flask, render_template, request
import pandas as pd
import requests
from recommendation import ExerciseScheduler

load_dotenv()

app = Flask(__name__)

# Load exercise data
exercises_df = pd.read_csv('./data2.csv')
scheduler = ExerciseScheduler(exercises_df)

def fetch_images(query):
    api_key = os.getenv('API_KEY')
    search_engine_id = '239678cd7653547b1'
    
    # Construct the search URL
    url = f'https://www.googleapis.com/customsearch/v1'
    
    params = {
        'q': query,
        'cx': search_engine_id,
        'searchType': 'image',
        'key': api_key,
        'num': 5,  # Number of results you want (max is 10)
        'fileType': 'gif',  # Fetch GIFs only
        'imgType': 'animated'  # Fetch animated images (GIFs)
    }
    
    response = requests.get(url, params=params)
    results = response.json()
    
    # Print out the full response to debug
    print(results)
    
    # Extract image URLs (GIFs)
    image_urls = []
    if 'items' in results:
        for item in results['items']:
            image_urls.append(item['link'])
    
    return image_urls



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        days = int(request.form['days'])
        goal = str(request.form['goal'])
        group_size = int(request.form['group_size'])
        w_days = int(request.form['w_days'])
        
        user_schedule = scheduler.generate_muscle_specific_schedule(days=days, num_exercises_per_day=w_days, goal=goal, group_size=group_size)
        
        exercise_names = []
        for exercises in user_schedule.values(): 
            for exercise in exercises:
                exercise_names.append(exercise['Title']) 
        
        # Fetch images for each exercise
        exercise_images = {name: fetch_images(name) for name in exercise_names}
        
        return render_template('result.html', user_schedule=user_schedule, exercise_images=exercise_images)
    else:
        return render_template('index.html', user_schedule=None)


if __name__=='__main__':
    app.run(debug=True)

