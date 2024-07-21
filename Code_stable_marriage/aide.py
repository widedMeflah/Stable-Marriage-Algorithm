from flask import Flask, render_template, request, jsonify
import random
import csv
app = Flask(__name__)

school_names = []
student_names = []
school_preferences = {}
student_preferences = {}
matching_students = {}
matching_schools = {}


def generate_preferences():
    global student_preferences, school_preferences
    student_preferences = {}
    school_preferences = {}

    for student in student_names:
        random_schools = list(school_names)
        random.shuffle(random_schools)
        student_preferences[student] = random_schools

    for school in school_names:
        random_students = list(student_names)
        random.shuffle(random_students)
        school_preferences[school] = random_students


def generate_names(number):
    global school_names, student_names
    school_names = ["Etablissement " + str(i) for i in range(1, number + 1)]
    student_names = ["Etudiant " + str(i) for i in range(1, number + 1)]


@app.route('/')
def index():
    return render_template('index1.html')
def css():
    return render_template('css/styles.css')


@app.route('/generate_names', methods=['POST'])
def generate_and_show_names():
    number = int(request.form['sampleSize'])
    generate_names(number)
    return jsonify({'school_names': school_names, 'student_names': student_names})


@app.route('/generate_preferences', methods=['POST'])
def generate_and_save_preferences():
    generate_preferences()
    return jsonify({'student_preferences': student_preferences, 'school_preferences': school_preferences})


def perform_stable_marriage_students_first():
    global matching_students, matching_schools
    matching_students = {}
    matching_schools = {}
    available_students = set(student_names)
    students_preferences_index = {student: 0 for student in student_names}

    while available_students:
        student = available_students.pop()
        school = student_preferences[student][students_preferences_index[student]]
        students_preferences_index[student] += 1

        if school not in matching_schools:
            matching_students[student] = school
            matching_schools[school] = student
        else:
            current_match = matching_schools[school]
            if school_preferences[school].index(student) < school_preferences[school].index(current_match):
                available_students.add(current_match)
                matching_students[student] = school
                matching_schools[school] = student
            else:
                available_students.add(student)

    return matching_students


def matching_in_school_students_first(school):
    for student, school_assigned in matching_students.items():
        if school_assigned == school:
            return student
    return None

def get_matching_for_all_schools(matching_students):
    matching_for_all_schools = {}

    for school in school_names:
        student = matching_in_school_students_first(school)
        matching_for_all_schools[school] = student

    return matching_for_all_schools


def perform_stable_marriage_schools_first():
    global matching_students, matching_schools
    matching_students = {}
    matching_schools = {}
    available_schools = set(school_names)
    schools_preferences_index = {school: 0 for school in school_names}

    while available_schools:
        school = available_schools.pop()
        student = school_preferences[school][schools_preferences_index[school]]
        schools_preferences_index[school] += 1

        if student not in matching_students:
            matching_students[student] = school
            matching_schools[school] = student
        else:
            current_match = matching_students[student]
            if student_preferences[student].index(school) < student_preferences[student].index(current_match):
                available_schools.add(current_match)
                matching_students[student] = school
                matching_schools[school] = student
            else:
                available_schools.add(school)

    return matching_schools







def matching_in_student_students_first(student):
    for school, student_assigned in matching_schools.items():
        if student_assigned == student:
            return school
    return None

def get_matching_for_all_students(matching_schools):
    matching_for_all_students = {}

    for student in student_names:
        school = matching_in_student_students_first(student)
        matching_for_all_students[student] = school

    return matching_for_all_students





def calculate_satisfaction_students(student_preferences, matching_students):
    satisfaction_sum = 0
    max_possible_satisfaction = len(student_preferences)  

    for student, school in matching_students.items():
        rank = len(student_preferences[student]) - student_preferences[student].index(school)
        satisfaction_sum += rank

    satisfaction_percentage = (satisfaction_sum / (max_possible_satisfaction * len(student_preferences[list(student_preferences.keys())[0]]))) * 100
    return satisfaction_percentage


def execute_algorithm_and_save_results():
    results_file = 'results.csv'

    with open(results_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Value of n', 'satisfaction etudients (priorité etudiant)', 'satisfaction etablissements (priorité etudiant)', 'satisfaction etablissements (priorité etablissement)', 'satisfaction etudients (priorité etablissement)'])

        for n in range(2, 101):  # Pour différentes valeurs de n de 2 à 100
            generate_names(n)  # Générer des noms pour les établissements et les étudiants
            generate_preferences()  # Générer des préférences aléatoires

            result1 = perform_stable_marriage_students_first()
            school_student1 = get_matching_for_all_schools(result1)
            satisf11 = calculate_satisfaction_students(student_preferences, result1)  
            satisf12 = calculate_satisfaction_students(school_preferences, school_student1)  
            
            result = perform_stable_marriage_schools_first()
            student_school= get_matching_for_all_students(result)
            satisf21 = calculate_satisfaction_students(school_preferences, result)
            satisf22 = calculate_satisfaction_students(student_preferences, student_school)  
            writer.writerow([n, satisf11, satisf12, satisf21, satisf22 ])

    print(f"Les résultats ont été enregistrés dans {results_file}")

@app.route('/automate_execution', methods=['GET'])
def automate_execution():
    execute_algorithm_and_save_results()
    return jsonify({'message': 'Exécution automatisée terminée et résultats enregistrés.'})

@app.route('/perform_stable_marriage_students_first', methods=['POST'])
def get_stable_marriage_results_students_first():
    result = perform_stable_marriage_students_first()
    school_student = get_matching_for_all_schools(result)
    satisf11 = calculate_satisfaction_students(student_preferences, result)  
    satisf12 = calculate_satisfaction_students(school_preferences, school_student)  
    return jsonify({'matching_students': result, 'school_student': school_student, 'satisf11': satisf11, 'satisf12': satisf12})


@app.route('/perform_stable_marriage_schools_first', methods=['POST'])
def get_stable_marriage_results_schools_first():
    result = perform_stable_marriage_schools_first()
    student_school= get_matching_for_all_students(result)
    satisf21 = calculate_satisfaction_students(school_preferences, result)
    satisf22 = calculate_satisfaction_students(student_preferences, student_school)  
    return jsonify({'matching_students': result, 'student_school': student_school,'satisf21': satisf21,'satisf22': satisf22})


if __name__ == '__main__':
    app.run(debug=True)