from .models import Athlete

import openai
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

def generate_workout(api_key, user_equipment, workout_type):
    openai.api_key = api_key
    equipment_names = [e.equipment for e in user_equipment]
    equipment = ", ".join(equipment_names)
    prompt = f"""Given the following list of available equipment: '{equipment}', please generate a {workout_type} workout.
    Please respond in the format of:
    <Workout> 
    
    <Excerise 1> 
    <Excerise 2> 
    <Excerise 3> 
    etc.
    
    Please include number of reps and sets.
    """
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens = 2048,
        n = 1, 
        stop = None,
        temperature = 0.2
    )
    result = response['choices'][0]['text']
    return result

def create_weight_graph(x, y):
    plt.figure()
    plt.plot(x, y, marker="*")
    plt.title('Weight over Time')
    plt.xticks(x, rotation='vertical')
    plt.xlabel('Dates')
    plt.ylabel('Weight (lbs)')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return image_base64

def create_blood_pressure_graph(x, systolic_bp, diastolic_bp):
    plt.figure()
    plt.plot(x, systolic_bp, label='Systolic', marker='*')
    plt.plot(x, diastolic_bp, label='Diastolic', marker='*')
    plt.title('Blood Pressure over Time')
    plt.xticks(x, rotation='vertical')
    plt.xlabel('Dates')
    plt.ylabel('Blood Pressure (mmHg)')
    plt.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return image_base64

def convert_to_kilos(weight):
    return float(weight) * 0.45359237

def blood_pressure_category(systolic, diastolic):
    if systolic < 120 and diastolic < 80:
        return Athlete.BP_NORMAL
    elif 120 <= systolic <= 129 and diastolic < 80:
        return Athlete.BP_ELEVATED
    elif 130 <= systolic <= 139 or 80 <= diastolic <= 89:
        return Athlete.BP_HYPERTENSION_STAGE_1
    elif systolic >= 140 or diastolic >= 90:
        return Athlete.BP_HYPERTENSION_STAGE_2
    else:
        return Athlete.BP_HYPERTENSIVE_CRISIS
    
def bmi_category(bmi):
    if bmi < 18.5:
        bmi_class = Athlete.UNDERWEIGHT
    elif bmi >= 18.5 and bmi < 25:
        bmi_class = Athlete.NORMAL
    elif bmi >= 25 and bmi < 30:
        bmi_class = Athlete.OVERWEIGHT
    elif bmi >= 30 and bmi < 35:
        bmi_class = Athlete.OBESE_MODERATE
    elif bmi >= 35 and bmi < 40:
        bmi_class = Athlete.OBESE_SEVERE
    else:
        bmi_class = Athlete.OBESE_VERY_SEVERE
    return bmi_class

def calculate_bmi(weight, height):
    height_m = height / 100
    bmi_unround = weight / (height_m ** 2)
    bmi_round = round(bmi_unround, 2)
    return bmi_round