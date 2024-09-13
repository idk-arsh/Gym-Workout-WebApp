import random
import pandas as pd

class ExerciseScheduler:
    def __init__(self, exercises_df):
        self.exercises_df = exercises_df
        self.available_muscles = self.exercises_df['BodyPart'].unique().tolist()

    def generate_random_combinations(self, num_combinations=7, combination_size=3, avoid_repetition=True):
        random_combinations = []
        last_combination = []

        for _ in range(num_combinations):
            if avoid_repetition:
                available_muscles = [muscle for muscle in self.available_muscles if muscle not in last_combination]
            else:
                available_muscles = self.available_muscles
            
            if len(available_muscles) < combination_size:
                combination = random.sample(self.available_muscles, combination_size)
            else:
                combination = random.sample(available_muscles, combination_size)

            random_combinations.append(combination)
            last_combination = combination

        return random_combinations

    def generate_muscle_specific_schedule(self, days=7, num_exercises_per_day=10, intensity=None, goal=None, group_size=3):
        weekly_schedule = {}
        muscle_combinations = self.generate_random_combinations(num_combinations=days, combination_size=group_size, avoid_repetition=True)

        for day, muscle_group in enumerate(muscle_combinations, 1):
            body_part_exercises = self._filter_exercises_for_body_part(muscle_group, intensity, goal)

            num_available_exercises = len(body_part_exercises)

            if num_available_exercises == 0:
                print(f"No exercises available for {muscle_group} with intensity {intensity} and goal {goal}.")
                body_part_exercises = self._fallback_exercises(muscle_group) 
            num_exercises_to_sample = min(num_available_exercises, num_exercises_per_day)

            if num_exercises_to_sample == 0:
                print(f"Still no exercises available for {muscle_group}. Skipping this day.")
                continue  
            daily_exercises = self._sample_by_rating(body_part_exercises, num_exercises_to_sample)
            weekly_schedule[f'Day {day} - Focus: {", ".join(muscle_group)}'] = daily_exercises[['Title', 'Desc', 'Type', 'BodyPart', 'Equipment', 'Level', 'Sets', 'Reps per Set']].to_dict(orient='records')

        return weekly_schedule

    def _filter_exercises_for_body_part(self, muscle_group, intensity, goal):
        filtered_exercises = self.exercises_df[self.exercises_df['BodyPart'].isin(muscle_group)]
        if intensity:
            filtered_exercises = filtered_exercises[filtered_exercises['Level'] == intensity]

        if goal:
            filtered_exercises = filtered_exercises[filtered_exercises['Goal'] == goal]

        return filtered_exercises

    def _fallback_exercises(self, muscle_group):
        """
        Fallback method if no exercises are found for a muscle group
        with the provided intensity or goal. It simply returns all
        exercises for the muscle group, ignoring intensity and goal.
        """
        print(f"Falling back to all exercises for {muscle_group}.")
        return self.exercises_df[self.exercises_df['BodyPart'].isin(muscle_group)]

    def _sample_by_rating(self, exercises_df, n):
        if exercises_df['Rating'].sum() == 0:
            return exercises_df.sample(n=n, random_state=42)

        rating_weights = exercises_df['Rating'] / exercises_df['Rating'].sum()

        try:
            return exercises_df.sample(n=n, weights=rating_weights, random_state=42)
        except ValueError:
            return exercises_df.sample(n=n, random_state=42)
