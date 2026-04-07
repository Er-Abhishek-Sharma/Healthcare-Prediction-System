"""
Management Command: seed_data
==============================
Usage: python manage.py seed_data

Populates the database with disease and symptom data.
"""
from django.core.management.base import BaseCommand
from patients.models import Disease, Symptom
from ml_module.predictor import SYMPTOM_LIST


DISEASES_DATA = [
    {
        'name': 'Fungal infection',
        'description': 'A fungal infection is a skin disease caused by a fungus.',
        'category': 'Skin',
        'precautions': 'Bath twice, Use detol or neem in bathing water, Keep infected area dry, Use clean cloths',
        'medications': 'Clotrimazole cream, Fluconazole, Ketoconazole, Terbinafine',
        'diet_plan': 'Eat yogurt, Avoid sugary foods, Eat garlic, Drink green tea, Eat foods rich in zinc',
        'exercises': 'Light walking, Yoga',
        'recommended_specialist': 'Dermatologist',
        'risk_level': 'low',
        'icd_code': 'B36',
    },
    {
        'name': 'Allergy',
        'description': 'An allergy is an immune system response to a foreign substance that is not typically harmful to your body.',
        'category': 'Immunology',
        'precautions': 'Apply calamine lotion, Cover area with bandage, Use ice to compress itching, Avoid allergy triggers',
        'medications': 'Antihistamines, Cetirizine, Loratadine, Fexofenadine, Nasal corticosteroids',
        'diet_plan': 'Eat local honey, Avoid processed foods, Consume Vitamin C rich foods, Drink chamomile tea',
        'exercises': 'Indoor exercises, Swimming (if not water allergic), Light yoga',
        'recommended_specialist': 'Allergist/Immunologist',
        'risk_level': 'low',
        'icd_code': 'J30',
    },
    {
        'name': 'GERD',
        'description': 'Gastroesophageal reflux disease (GERD) is chronic acid reflux into the esophagus.',
        'category': 'Gastroenterology',
        'precautions': 'Avoid fatty spicy food, Avoid lying down after eating, Maintain healthy weight, Exercise regularly',
        'medications': 'Omeprazole, Pantoprazole, Antacids, H2 blockers, Proton pump inhibitors',
        'diet_plan': 'Eat smaller meals, Avoid citrus fruits, Avoid tomatoes, No caffeine, No alcohol, Eat ginger',
        'exercises': 'Walking after meals, Light yoga, Avoid crunches',
        'recommended_specialist': 'Gastroenterologist',
        'risk_level': 'medium',
        'icd_code': 'K21',
    },
    {
        'name': 'Diabetes',
        'description': 'A metabolic disease causing high blood sugar. Either the body does not produce enough insulin, or it cannot effectively use the insulin it produces.',
        'category': 'Endocrinology',
        'precautions': 'Have a balanced diet, Exercise regularly, Monitor blood glucose regularly, Take medications as prescribed',
        'medications': 'Metformin, Insulin therapy, Glipizide, Sitagliptin, Empagliflozin',
        'diet_plan': 'Eat whole grains, Avoid sugary drinks, Include leafy vegetables, Eat fiber-rich foods, Control portion sizes',
        'exercises': 'Walking 30 min daily, Swimming, Cycling, Yoga, Resistance training',
        'recommended_specialist': 'Endocrinologist/Diabetologist',
        'risk_level': 'high',
        'icd_code': 'E11',
    },
    {
        'name': 'Hypertension',
        'description': 'High blood pressure is a common condition where the long-term force of blood against artery walls is high enough to cause health problems.',
        'category': 'Cardiology',
        'precautions': 'Meditation, Salt restriction, Reduce stress, Monitor blood pressure regularly',
        'medications': 'Amlodipine, Atenolol, Losartan, Lisinopril, Hydrochlorothiazide',
        'diet_plan': 'DASH diet, Reduce sodium, Eat potassium-rich foods, Avoid alcohol, Eat fresh fruits',
        'exercises': 'Walking, Swimming, Cycling, Yoga, Avoid heavy lifting',
        'recommended_specialist': 'Cardiologist',
        'risk_level': 'high',
        'icd_code': 'I10',
    },
    {
        'name': 'Migraine',
        'description': 'A neurological condition that can cause multiple symptoms. It is frequently characterized by intense, debilitating headaches.',
        'category': 'Neurology',
        'precautions': 'Limit alcohol, Get adequate sleep, Reduce stress, Use sunglasses in bright light',
        'medications': 'Sumatriptan, Ibuprofen, Acetaminophen, Amitriptyline, Topiramate',
        'diet_plan': 'Avoid red wine, Stay hydrated, Avoid skipping meals, Limit caffeine, Avoid aged cheese',
        'exercises': 'Regular aerobic exercise, Yoga, Tai chi, Swimming',
        'recommended_specialist': 'Neurologist',
        'risk_level': 'medium',
        'icd_code': 'G43',
    },
    {
        'name': 'Common Cold',
        'description': 'A viral infectious disease of the upper respiratory tract that primarily affects the nose.',
        'category': 'General Medicine',
        'precautions': 'Drink vitamin C rich drinks, Take vapour, Avoid cold food, Avoid being in cold temperature',
        'medications': 'Paracetamol, Decongestants, Antihistamines, Cough syrups, Zinc lozenges',
        'diet_plan': 'Drink warm water, Eat chicken soup, Consume ginger tea, Eat citrus fruits, Honey with warm water',
        'exercises': 'Rest, Light walking when feeling better',
        'recommended_specialist': 'General Physician',
        'risk_level': 'low',
        'icd_code': 'J00',
    },
    {
        'name': 'Dengue',
        'description': 'A mosquito-borne tropical disease caused by the dengue virus, causing flu-like illness.',
        'category': 'Infectious Disease',
        'precautions': 'Drink papaya leaf juice, Avoid oily fatty food, Keep surroundings clean, Use mosquito repellent',
        'medications': 'Paracetamol, IV fluids, Rest, Avoid Aspirin and NSAIDs',
        'diet_plan': 'Papaya leaf juice, Coconut water, Orange juice, Kiwi, Pomegranate, Herbal tea',
        'exercises': 'Complete bed rest during acute phase',
        'recommended_specialist': 'Infectious Disease Specialist',
        'risk_level': 'high',
        'icd_code': 'A90',
    },
    {
        'name': 'Malaria',
        'description': 'A life-threatening disease caused by parasites transmitted through infected mosquitoes.',
        'category': 'Infectious Disease',
        'precautions': 'Consult doctor, Mosquito repellant, Keep area around clean, Use mosquito nets',
        'medications': 'Chloroquine, Artemisinin-based therapy, Primaquine, Doxycycline',
        'diet_plan': 'Drink plenty of fluids, Eat light easily digestible foods, Avoid spicy food, Consume ginger',
        'exercises': 'Complete rest during fever, Light activity during recovery',
        'recommended_specialist': 'Infectious Disease Specialist',
        'risk_level': 'critical',
        'icd_code': 'B50',
    },
    {
        'name': 'Typhoid',
        'description': 'A bacterial infection caused by Salmonella typhi, spread through contaminated food and water.',
        'category': 'Infectious Disease',
        'precautions': 'Eat high calorie food, Eat easily digestible food, Drink plenty of fluids, Get vaccinated',
        'medications': 'Ciprofloxacin, Azithromycin, Ceftriaxone, Ampicillin',
        'diet_plan': 'Soft boiled eggs, Bananas, Rice, Boiled potatoes, Soup, Avoid raw vegetables',
        'exercises': 'Complete rest, Gradual return to activity after recovery',
        'recommended_specialist': 'Infectious Disease Specialist/General Physician',
        'risk_level': 'high',
        'icd_code': 'A01',
    },
    {
        'name': 'Pneumonia',
        'description': 'An infection that inflames the air sacs in one or both lungs, which may fill with fluid.',
        'category': 'Pulmonology',
        'precautions': 'Consult doctor, Medication, Rest and ample sleep, Stop smoking',
        'medications': 'Antibiotics, Amoxicillin, Azithromycin, Doxycycline, Cough medicine',
        'diet_plan': 'Drink plenty of water, Eat protein-rich foods, Consume vitamin C foods, Avoid dairy products',
        'exercises': 'Deep breathing exercises, Rest during acute phase',
        'recommended_specialist': 'Pulmonologist',
        'risk_level': 'high',
        'icd_code': 'J18',
    },
    {
        'name': 'Heart attack',
        'description': 'A heart attack occurs when blood flow to the heart is blocked, starving the heart muscle of oxygen.',
        'category': 'Cardiology',
        'precautions': 'Call ambulance immediately, Perform CPR if needed, Chew aspirin, Keep calm',
        'medications': 'Aspirin, Nitroglycerin, Thrombolytics, Beta blockers, ACE inhibitors',
        'diet_plan': 'Heart-healthy diet, Avoid trans fats, Eat omega-3 rich foods, Limit sodium, Eat more fiber',
        'exercises': 'Cardiac rehabilitation exercises under supervision',
        'recommended_specialist': 'Cardiologist/Emergency Medicine',
        'risk_level': 'critical',
        'icd_code': 'I21',
    },
    {
        'name': 'Tuberculosis',
        'description': 'A potentially serious infectious disease that mainly affects the lungs, caused by Mycobacterium tuberculosis.',
        'category': 'Pulmonology/Infectious Disease',
        'precautions': 'Cover mouth when coughing, Use masks, Keep distance from others, Take medications regularly',
        'medications': 'Isoniazid, Rifampin, Pyrazinamide, Ethambutol (HRZE regimen for 6 months)',
        'diet_plan': 'High protein diet, Vitamin D rich foods, Eat garlic, Banana, Milk, Eggs',
        'exercises': 'Light exercise when tolerated, Breathing exercises',
        'recommended_specialist': 'Pulmonologist/Infectious Disease Specialist',
        'risk_level': 'high',
        'icd_code': 'A15',
    },
    {
        'name': 'Acne',
        'description': 'A skin condition that occurs when hair follicles plug with oil and dead skin cells.',
        'category': 'Dermatology',
        'precautions': 'Bath twice daily, Avoid fatty spicy food, Drink 8 glasses of water daily, Avoid touching face',
        'medications': 'Benzoyl peroxide, Salicylic acid, Tretinoin, Doxycycline, Adapalene',
        'diet_plan': 'Drink more water, Eat foods low in glycemic index, Avoid dairy, Eat zinc-rich foods',
        'exercises': 'Regular exercise to reduce stress, Yoga',
        'recommended_specialist': 'Dermatologist',
        'risk_level': 'low',
        'icd_code': 'L70',
    },
    {
        'name': 'Urinary tract infection',
        'description': 'An infection that affects part of the urinary tract: kidney, ureter, bladder, or urethra.',
        'category': 'Urology/Nephrology',
        'precautions': 'Drink plenty of water, Increase vitamin C intake, Urinate after sex, Wear cotton undergarments',
        'medications': 'Trimethoprim-sulfamethoxazole, Nitrofurantoin, Ciprofloxacin, Fosfomycin',
        'diet_plan': 'Drink cranberry juice, Lots of water, Avoid sugary foods, Eat blueberries, Probiotic-rich foods',
        'exercises': 'Regular moderate exercise, Kegel exercises',
        'recommended_specialist': 'Urologist/General Physician',
        'risk_level': 'medium',
        'icd_code': 'N39',
    },
]


class Command(BaseCommand):
    help = 'Seed database with disease and symptom data'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding database...\n')

        # Seed Symptoms
        self.stdout.write('Adding symptoms...')
        created_symptoms = 0
        for sym_name in SYMPTOM_LIST:
            _, created = Symptom.objects.get_or_create(
                name=sym_name,
                defaults={
                    'description': sym_name.replace('_', ' ').replace('and', '&').title(),
                    'severity_weight': 1,
                }
            )
            if created:
                created_symptoms += 1

        self.stdout.write(self.style.SUCCESS(f'  ✅ {created_symptoms} new symptoms added ({Symptom.objects.count()} total)'))

        # Seed Diseases
        self.stdout.write('Adding diseases...')
        created_diseases = 0
        for disease_data in DISEASES_DATA:
            _, created = Disease.objects.get_or_create(
                name=disease_data['name'],
                defaults=disease_data
            )
            if created:
                created_diseases += 1

        self.stdout.write(self.style.SUCCESS(f'  ✅ {created_diseases} new diseases added ({Disease.objects.count()} total)'))

        self.stdout.write(self.style.SUCCESS('\n🎉 Database seeding complete!'))
        self.stdout.write('\nNext steps:')
        self.stdout.write('  1. python manage.py train_models')
        self.stdout.write('  2. python manage.py createsuperuser')
        self.stdout.write('  3. python manage.py runserver')
