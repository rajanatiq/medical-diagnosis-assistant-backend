-- ============================================================================
-- AegisMed: Medical Diagnosis & Triage Assistant System
-- FINAL ALL-IN-ONE COMPLETE DATABASE SCRIPT (SQL Server / Standard SQL)
-- Database Name: medical_diagnosis_assistant
-- ============================================================================

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'medical_diagnosis_assistant')
BEGIN
    CREATE DATABASE medical_diagnosis_assistant;
END
GO

USE medical_diagnosis_assistant;
GO

-- ============================================================================
-- TABLE 1: users (User Authentication, Roles & Security)
-- ============================================================================
IF OBJECT_ID(N'dbo.users', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.users (
        id INT IDENTITY(1,1) PRIMARY KEY,
        email NVARCHAR(255) NOT NULL UNIQUE,
        hashed_password NVARCHAR(255) NOT NULL,
        full_name NVARCHAR(255) NULL,
        is_active INT DEFAULT 1,
        created_at DATETIME2 DEFAULT GETDATE()
    );
    CREATE NONCLUSTERED INDEX idx_users_email ON dbo.users(email);
END
GO

-- ============================================================================
-- TABLE 2: patient_profiles (Encrypted Patient Baseline Health Data)
-- ============================================================================
IF OBJECT_ID(N'dbo.patient_profiles', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.patient_profiles (
        id INT IDENTITY(1,1) PRIMARY KEY,
        user_id INT NOT NULL UNIQUE FOREIGN KEY REFERENCES dbo.users(id) ON DELETE CASCADE,
        age_band NVARCHAR(50) DEFAULT '30-39',
        sex NVARCHAR(20) DEFAULT 'Other',
        encrypted_medical_history NVARCHAR(MAX) NULL,
        encrypted_allergies NVARCHAR(MAX) NULL,
        encrypted_current_medications NVARCHAR(MAX) NULL,
        created_at DATETIME2 DEFAULT GETDATE(),
        updated_at DATETIME2 DEFAULT GETDATE()
    );
    CREATE NONCLUSTERED INDEX idx_patient_user ON dbo.patient_profiles(user_id);
END
GO

-- ============================================================================
-- TABLE 3: symptoms (All 131 Standardized Clinical Symptoms)
-- ============================================================================
IF OBJECT_ID(N'dbo.symptoms', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.symptoms (
        id INT IDENTITY(1,1) PRIMARY KEY,
        code NVARCHAR(100) NOT NULL UNIQUE,
        label NVARCHAR(255) NOT NULL,
        severity_weight INT NOT NULL DEFAULT 3,
        category NVARCHAR(100) NOT NULL DEFAULT 'General',
        is_critical BIT NOT NULL DEFAULT 0,
        created_at DATETIME2 DEFAULT GETDATE()
    );
    CREATE NONCLUSTERED INDEX idx_symptoms_code ON dbo.symptoms(code);
    CREATE NONCLUSTERED INDEX idx_symptoms_category ON dbo.symptoms(category);
END
GO

-- ============================================================================
-- TABLE 4: diseases (All 41 Medical Conditions, Specialties & Precautions)
-- ============================================================================
IF OBJECT_ID(N'dbo.diseases', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.diseases (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(255) NOT NULL UNIQUE,
        specialty NVARCHAR(100) NOT NULL,
        description NVARCHAR(MAX) NULL,
        precaution_1 NVARCHAR(255) NULL,
        precaution_2 NVARCHAR(255) NULL,
        precaution_3 NVARCHAR(255) NULL,
        precaution_4 NVARCHAR(255) NULL,
        created_at DATETIME2 DEFAULT GETDATE()
    );
    CREATE NONCLUSTERED INDEX idx_diseases_name ON dbo.diseases(name);
    CREATE NONCLUSTERED INDEX idx_diseases_specialty ON dbo.diseases(specialty);
END
GO

-- ============================================================================
-- TABLE 5: assessments (Triage Assessments & Top-3 Probabilities)
-- ============================================================================
IF OBJECT_ID(N'dbo.assessments', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.assessments (
        id INT IDENTITY(1,1) PRIMARY KEY,
        user_id INT NULL FOREIGN KEY REFERENCES dbo.users(id) ON DELETE CASCADE,
        session_id NVARCHAR(100) NULL,
        symptoms_json NVARCHAR(MAX) NOT NULL,
        duration_days INT DEFAULT 1,
        age_band NVARCHAR(50) NULL,
        sex NVARCHAR(20) NULL,
        model_version NVARCHAR(50) DEFAULT 'v1.0.0',
        predictions_json NVARCHAR(MAX) NOT NULL,
        urgency NVARCHAR(50) NOT NULL,
        red_flag_triggered BIT DEFAULT 0,
        red_flag_reason NVARCHAR(255) NULL,
        composite_severity FLOAT DEFAULT 0.0,
        created_at DATETIME2 DEFAULT GETDATE()
    );
    CREATE NONCLUSTERED INDEX idx_assessments_user ON dbo.assessments(user_id);
    CREATE NONCLUSTERED INDEX idx_assessments_urgency ON dbo.assessments(urgency);
END
GO

-- ============================================================================
-- TABLE 6: healthcare_providers (Geospatial Doctor & Hospital Directory)
-- ============================================================================
IF OBJECT_ID(N'dbo.healthcare_providers', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.healthcare_providers (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(255) NOT NULL,
        facility_type NVARCHAR(100) DEFAULT 'Clinic',
        specialty NVARCHAR(100) NOT NULL,
        latitude FLOAT NOT NULL,
        longitude FLOAT NOT NULL,
        address NVARCHAR(255) NOT NULL,
        city NVARCHAR(100) DEFAULT 'Islamabad',
        phone NVARCHAR(50) NULL,
        emergency_capable BIT DEFAULT 0,
        rating FLOAT DEFAULT 4.5,
        hours NVARCHAR(100) DEFAULT '24/7 Open'
    );
    CREATE NONCLUSTERED INDEX idx_providers_specialty ON dbo.healthcare_providers(specialty);
    CREATE NONCLUSTERED INDEX idx_providers_emergency ON dbo.healthcare_providers(emergency_capable);
END
GO

-- ============================================================================
-- TABLE 7: audit_logs (Privacy Audit Trail with Hashed IPs)
-- ============================================================================
IF OBJECT_ID(N'dbo.audit_logs', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.audit_logs (
        id INT IDENTITY(1,1) PRIMARY KEY,
        user_id INT NULL,
        action NVARCHAR(100) NOT NULL,
        resource_type NVARCHAR(50) NOT NULL,
        resource_id NVARCHAR(100) NULL,
        ip_hash NVARCHAR(64) NOT NULL,
        timestamp DATETIME2 DEFAULT GETDATE()
    );
    CREATE NONCLUSTERED INDEX idx_audit_user ON dbo.audit_logs(user_id);
END
GO

-- ============================================================================
-- SEED DATA: Default Demo User & Patient Profile
-- ============================================================================
IF NOT EXISTS (SELECT 1 FROM dbo.users WHERE email = N'patient.demo@aegismed.org')
BEGIN
    INSERT INTO dbo.users (email, hashed_password, full_name, is_active) VALUES
    (N'patient.demo@aegismed.org', N'$2b$12$eXAmpLeHAsheDPaSSwOrd123456789012345678901234567890123456', N'Jane Doe (Demo Patient)', 1);

    DECLARE @new_user_id INT = SCOPE_IDENTITY();
    INSERT INTO dbo.patient_profiles (user_id, age_band, sex, encrypted_medical_history, encrypted_allergies, encrypted_current_medications) VALUES
    (@new_user_id, N'30-39', N'Female', N'gAAAAABn...EncryptedHistory', N'gAAAAABn...EncryptedAllergies', N'gAAAAABn...EncryptedMeds');
END
GO

-- ============================================================================
-- SEED DATA: All 131 Clinical Symptoms
-- ============================================================================
IF NOT EXISTS (SELECT 1 FROM dbo.symptoms)
BEGIN
    INSERT INTO dbo.symptoms (code, label, severity_weight, category, is_critical) VALUES
    (N'abdominal_pain', N'Abdominal Pain', 4, N'Digestive & Gastrointestinal', 0),
    (N'abnormal_menstruation', N'Abnormal Menstruation', 6, N'General & Constitutional', 1),
    (N'acidity', N'Acidity', 3, N'General & Constitutional', 0),
    (N'acute_liver_failure', N'Acute Liver Failure', 6, N'Digestive & Gastrointestinal', 1),
    (N'altered_sensorium', N'Altered Sensorium', 2, N'Neurological & Head', 0),
    (N'anxiety', N'Anxiety', 4, N'General & Constitutional', 0),
    (N'back_pain', N'Back Pain', 3, N'Musculoskeletal & Joints', 0),
    (N'belly_pain', N'Belly Pain', 4, N'General & Constitutional', 0),
    (N'blackheads', N'Blackheads', 2, N'Neurological & Head', 0),
    (N'bladder_discomfort', N'Bladder Discomfort', 4, N'Urinary & Renal', 0),
    (N'blister', N'Blister', 4, N'Dermatology & Skin', 0),
    (N'blood_in_sputum', N'Blood In Sputum', 5, N'General & Constitutional', 0),
    (N'bloody_stool', N'Bloody Stool', 5, N'General & Constitutional', 0),
    (N'blurred_and_distorted_vision', N'Blurred And Distorted Vision', 5, N'Neurological & Head', 0),
    (N'breathlessness', N'Breathlessness', 4, N'Chest & Respiratory', 0),
    (N'brittle_nails', N'Brittle Nails', 5, N'General & Constitutional', 0),
    (N'bruising', N'Bruising', 4, N'Dermatology & Skin', 0),
    (N'burning_micturition', N'Burning Micturition', 6, N'Urinary & Renal', 1),
    (N'chest_pain', N'Chest Pain', 7, N'Chest & Respiratory', 1),
    (N'chills', N'Chills', 3, N'General & Constitutional', 0),
    (N'cold_hands_and_feets', N'Cold Hands And Feets', 5, N'General & Constitutional', 0),
    (N'coma', N'Coma', 7, N'Neurological & Head', 1),
    (N'congestion', N'Congestion', 5, N'General & Constitutional', 0),
    (N'constipation', N'Constipation', 4, N'Digestive & Gastrointestinal', 0),
    (N'continuous_feel_of_urine', N'Continuous Feel Of Urine', 6, N'Urinary & Renal', 1),
    (N'continuous_sneezing', N'Continuous Sneezing', 4, N'General & Constitutional', 0),
    (N'cough', N'Cough', 4, N'Chest & Respiratory', 0),
    (N'cramps', N'Cramps', 4, N'General & Constitutional', 0),
    (N'dark_urine', N'Dark Urine', 4, N'Urinary & Renal', 0),
    (N'dehydration', N'Dehydration', 4, N'General & Constitutional', 0),
    (N'depression', N'Depression', 3, N'General & Constitutional', 0),
    (N'diarrhoea', N'Diarrhoea', 6, N'Digestive & Gastrointestinal', 1),
    (N'dischromic_patches', N'Dischromic Patches', 6, N'Dermatology & Skin', 1),
    (N'distention_of_abdomen', N'Distention Of Abdomen', 4, N'General & Constitutional', 0),
    (N'dizziness', N'Dizziness', 4, N'Neurological & Head', 0),
    (N'drying_and_tingling_lips', N'Drying And Tingling Lips', 4, N'General & Constitutional', 0),
    (N'enlarged_thyroid', N'Enlarged Thyroid', 6, N'General & Constitutional', 1),
    (N'excessive_hunger', N'Excessive Hunger', 4, N'General & Constitutional', 0),
    (N'extra_marital_contacts', N'Extra Marital Contacts', 5, N'General & Constitutional', 0),
    (N'family_history', N'Family History', 5, N'General & Constitutional', 0),
    (N'fast_heart_rate', N'Fast Heart Rate', 5, N'General & Constitutional', 0),
    (N'fatigue', N'Fatigue', 4, N'General & Constitutional', 0),
    (N'fluid_overload', N'Fluid Overload', 4, N'General & Constitutional', 0),
    (N'foul_smell_of_urine', N'Foul Smell Of Urine', 3, N'Urinary & Renal', 0),
    (N'headache', N'Headache', 3, N'Neurological & Head', 0),
    (N'high_fever', N'High Fever', 7, N'General & Constitutional', 1),
    (N'hip_joint_pain', N'Hip Joint Pain', 2, N'Musculoskeletal & Joints', 0),
    (N'history_of_alcohol_consumption', N'History Of Alcohol Consumption', 5, N'General & Constitutional', 0),
    (N'increased_appetite', N'Increased Appetite', 5, N'Digestive & Gastrointestinal', 0),
    (N'indigestion', N'Indigestion', 5, N'Digestive & Gastrointestinal', 0),
    (N'inflammatory_nails', N'Inflammatory Nails', 2, N'General & Constitutional', 0),
    (N'internal_itching', N'Internal Itching', 4, N'Dermatology & Skin', 0),
    (N'irregular_sugar_level', N'Irregular Sugar Level', 5, N'General & Constitutional', 0),
    (N'irritability', N'Irritability', 2, N'General & Constitutional', 0),
    (N'irritation_in_anus', N'Irritation In Anus', 6, N'General & Constitutional', 1),
    (N'itching', N'Itching', 1, N'Dermatology & Skin', 0),
    (N'joint_pain', N'Joint Pain', 3, N'Musculoskeletal & Joints', 0),
    (N'knee_pain', N'Knee Pain', 3, N'Musculoskeletal & Joints', 0),
    (N'lack_of_concentration', N'Lack Of Concentration', 3, N'General & Constitutional', 0),
    (N'lethargy', N'Lethargy', 2, N'General & Constitutional', 0),
    (N'loss_of_appetite', N'Loss Of Appetite', 4, N'Digestive & Gastrointestinal', 0),
    (N'loss_of_balance', N'Loss Of Balance', 4, N'Neurological & Head', 0),
    (N'loss_of_smell', N'Loss Of Smell', 3, N'General & Constitutional', 0),
    (N'malaise', N'Malaise', 6, N'General & Constitutional', 1),
    (N'mild_fever', N'Mild Fever', 5, N'General & Constitutional', 0),
    (N'mood_swings', N'Mood Swings', 3, N'General & Constitutional', 0),
    (N'movement_stiffness', N'Movement Stiffness', 5, N'Musculoskeletal & Joints', 0),
    (N'mucoid_sputum', N'Mucoid Sputum', 4, N'Chest & Respiratory', 0),
    (N'muscle_pain', N'Muscle Pain', 2, N'Musculoskeletal & Joints', 0),
    (N'muscle_wasting', N'Muscle Wasting', 3, N'Musculoskeletal & Joints', 0),
    (N'muscle_weakness', N'Muscle Weakness', 2, N'Neurological & Head', 0),
    (N'nausea', N'Nausea', 5, N'Digestive & Gastrointestinal', 0),
    (N'neck_pain', N'Neck Pain', 5, N'Musculoskeletal & Joints', 0),
    (N'nodal_skin_eruptions', N'Nodal Skin Eruptions', 4, N'Dermatology & Skin', 0),
    (N'obesity', N'Obesity', 4, N'General & Constitutional', 0),
    (N'pain_behind_the_eyes', N'Pain Behind The Eyes', 4, N'General & Constitutional', 0),
    (N'pain_during_bowel_movements', N'Pain During Bowel Movements', 5, N'Digestive & Gastrointestinal', 0),
    (N'pain_in_anal_region', N'Pain In Anal Region', 6, N'General & Constitutional', 1),
    (N'painful_walking', N'Painful Walking', 2, N'General & Constitutional', 0),
    (N'palpitations', N'Palpitations', 4, N'General & Constitutional', 0),
    (N'passage_of_gases', N'Passage Of Gases', 5, N'Digestive & Gastrointestinal', 0),
    (N'patches_in_throat', N'Patches In Throat', 6, N'Chest & Respiratory', 1),
    (N'phlegm', N'Phlegm', 5, N'Chest & Respiratory', 0),
    (N'polyuria', N'Polyuria', 4, N'General & Constitutional', 0),
    (N'prominent_veins_on_calf', N'Prominent Veins On Calf', 6, N'General & Constitutional', 1),
    (N'puffy_face_and_eyes', N'Puffy Face And Eyes', 5, N'General & Constitutional', 0),
    (N'pus_filled_pimples', N'Pus Filled Pimples', 2, N'General & Constitutional', 0),
    (N'receiving_blood_transfusion', N'Receiving Blood Transfusion', 5, N'General & Constitutional', 0),
    (N'receiving_unsterile_injections', N'Receiving Unsterile Injections', 2, N'General & Constitutional', 0),
    (N'red_sore_around_nose', N'Red Sore Around Nose', 2, N'General & Constitutional', 0),
    (N'red_spots_over_body', N'Red Spots Over Body', 3, N'General & Constitutional', 0),
    (N'redness_of_eyes', N'Redness Of Eyes', 5, N'General & Constitutional', 0),
    (N'restlessness', N'Restlessness', 5, N'General & Constitutional', 0),
    (N'runny_nose', N'Runny Nose', 5, N'General & Constitutional', 0),
    (N'rusty_sputum', N'Rusty Sputum', 4, N'General & Constitutional', 0),
    (N'scurring', N'Scurring', 2, N'Dermatology & Skin', 0),
    (N'shivering', N'Shivering', 5, N'General & Constitutional', 0),
    (N'silver_like_dusting', N'Silver Like Dusting', 2, N'General & Constitutional', 0),
    (N'sinus_pressure', N'Sinus Pressure', 4, N'General & Constitutional', 0),
    (N'skin_peeling', N'Skin Peeling', 3, N'Dermatology & Skin', 0),
    (N'skin_rash', N'Skin Rash', 3, N'Dermatology & Skin', 0),
    (N'slurred_speech', N'Slurred Speech', 4, N'Neurological & Head', 0),
    (N'small_dents_in_nails', N'Small Dents In Nails', 2, N'General & Constitutional', 0),
    (N'spinning_movements', N'Spinning Movements', 6, N'Neurological & Head', 1),
    (N'spotting_urination', N'Spotting Urination', 6, N'Urinary & Renal', 1),
    (N'stiff_neck', N'Stiff Neck', 4, N'Musculoskeletal & Joints', 0),
    (N'stomach_bleeding', N'Stomach Bleeding', 6, N'Digestive & Gastrointestinal', 1),
    (N'stomach_pain', N'Stomach Pain', 5, N'Digestive & Gastrointestinal', 0),
    (N'sunken_eyes', N'Sunken Eyes', 3, N'General & Constitutional', 0),
    (N'sweating', N'Sweating', 3, N'General & Constitutional', 0),
    (N'swelled_lymph_nodes', N'Swelled Lymph Nodes', 6, N'General & Constitutional', 1),
    (N'swelling_joints', N'Swelling Joints', 5, N'Musculoskeletal & Joints', 0),
    (N'swelling_of_stomach', N'Swelling Of Stomach', 7, N'Digestive & Gastrointestinal', 1),
    (N'swollen_blood_vessels', N'Swollen Blood Vessels', 5, N'General & Constitutional', 0),
    (N'swollen_extremeties', N'Swollen Extremeties', 5, N'General & Constitutional', 0),
    (N'swollen_legs', N'Swollen Legs', 5, N'General & Constitutional', 0),
    (N'throat_irritation', N'Throat Irritation', 4, N'Chest & Respiratory', 0),
    (N'toxic_look_(typhos)', N'Toxic Look (Typhos)', 5, N'General & Constitutional', 0),
    (N'ulcers_on_tongue', N'Ulcers On Tongue', 4, N'Digestive & Gastrointestinal', 0),
    (N'unsteadiness', N'Unsteadiness', 4, N'Neurological & Head', 0),
    (N'visual_disturbances', N'Visual Disturbances', 3, N'General & Constitutional', 0),
    (N'vomiting', N'Vomiting', 5, N'Digestive & Gastrointestinal', 0),
    (N'watering_from_eyes', N'Watering From Eyes', 4, N'General & Constitutional', 0),
    (N'weakness_in_limbs', N'Weakness In Limbs', 7, N'Neurological & Head', 1),
    (N'weakness_of_one_body_side', N'Weakness Of One Body Side', 4, N'Neurological & Head', 0),
    (N'weight_gain', N'Weight Gain', 3, N'General & Constitutional', 0),
    (N'weight_loss', N'Weight Loss', 3, N'General & Constitutional', 0),
    (N'yellow_crust_ooze', N'Yellow Crust Ooze', 3, N'General & Constitutional', 0),
    (N'yellow_urine', N'Yellow Urine', 4, N'Urinary & Renal', 0),
    (N'yellowing_of_eyes', N'Yellowing Of Eyes', 4, N'General & Constitutional', 0),
    (N'yellowish_skin', N'Yellowish Skin', 3, N'Dermatology & Skin', 0);
END
GO

-- ============================================================================
-- SEED DATA: All 41 Medical Conditions, Descriptions & 4 Precautions
-- ============================================================================
IF NOT EXISTS (SELECT 1 FROM dbo.diseases)
BEGIN
    INSERT INTO dbo.diseases (name, specialty, description, precaution_1, precaution_2, precaution_3, precaution_4) VALUES
    (N'(vertigo) Paroxysmal Positional Vertigo', N'ENT / Neurology', N'Benign paroxysmal positional vertigo (BPPV) is one of the most common causes of vertigo — the sudden sensation that you''re spinning or that the inside of your head is spinning. Benign paroxysmal positional vertigo causes brief episodes of mild to intense dizziness.', N'lie down', N'avoid sudden change in body', N'avoid abrupt head movment', N'relax'),
    (N'AIDS', N'Infectious Diseases / Immunology', N'Acquired immunodeficiency syndrome (AIDS) is a chronic, potentially life-threatening condition caused by the human immunodeficiency virus (HIV). By damaging your immune system, HIV interferes with your body''s ability to fight infection and disease.', N'avoid open cuts', N'wear ppe if possible', N'consult doctor', N'follow up'),
    (N'Acne', N'Dermatology', N'Acne vulgaris is the formation of comedones, papules, pustules, nodules, and/or cysts as a result of obstruction and inflammation of pilosebaceous units (hair follicles and their accompanying sebaceous gland). Acne develops on the face and upper trunk. It most often affects adolescents.', N'bath twice', N'avoid fatty spicy food', N'drink plenty of water', N'avoid too many products'),
    (N'Alcoholic hepatitis', N'Gastroenterology', N'Alcoholic hepatitis is a diseased, inflammatory condition of the liver caused by heavy alcohol consumption over an extended period of time. It''s also aggravated by binge drinking and ongoing alcohol use. If you develop this condition, you must stop drinking alcohol', N'stop alcohol consumption', N'consult doctor', N'medication', N'follow up'),
    (N'Allergy', N'Allergy & Immunology', N'An allergy is an immune system response to a foreign substance that''s not typically harmful to your body.They can include certain foods, pollen, or pet dander. Your immune system''s job is to keep you healthy by fighting harmful pathogens.', N'apply calamine', N'cover area with bandage', N'use ice to compress itching', N''),
    (N'Arthritis', N'Rheumatology', N'Arthritis is the swelling and tenderness of one or more of your joints. The main symptoms of arthritis are joint pain and stiffness, which typically worsen with age. The most common types of arthritis are osteoarthritis and rheumatoid arthritis.', N'exercise', N'use hot and cold therapy', N'try acupuncture', N'massage'),
    (N'Bronchial Asthma', N'Pulmonology', N'Bronchial asthma is a medical condition which causes the airway path of the lungs to swell and narrow. Due to this swelling, the air path produces excess mucus making it hard to breathe, which results in coughing, short breath, and wheezing. The disease is chronic and interferes with daily working.', N'switch to loose cloothing', N'take deep breaths', N'get away from trigger', N'seek help'),
    (N'Cervical spondylosis', N'Orthopedics / Neurology', N'Cervical spondylosis is a general term for age-related wear and tear affecting the spinal disks in your neck. As the disks dehydrate and shrink, signs of osteoarthritis develop, including bony projections along the edges of bones (bone spurs).', N'use heating pad or cold pack', N'exercise', N'take otc pain reliver', N'consult doctor'),
    (N'Chicken pox', N'Infectious Diseases / Pediatrics', N'Chickenpox is a highly contagious disease caused by the varicella-zoster virus (VZV). It can cause an itchy, blister-like rash. The rash first appears on the chest, back, and face, and then spreads over the entire body, causing between 250 and 500 itchy blisters.', N'use neem in bathing', N'consume neem leaves', N'take vaccine', N'avoid public places'),
    (N'Chronic cholestasis', N'Gastroenterology', N'Chronic cholestatic diseases, whether occurring in infancy, childhood or adulthood, are characterized by defective bile acid transport from the liver to the intestine, which is caused by primary damage to the biliary epithelium in most cases', N'cold baths', N'anti itch medicine', N'consult doctor', N'eat healthy'),
    (N'Common Cold', N'General Medicine', N'The common cold is a viral infection of your nose and throat (upper respiratory tract). It''s usually harmless, although it might not feel that way. Many types of viruses can cause a common cold.', N'drink vitamin c rich drinks', N'take vapour', N'avoid cold food', N'keep fever in check'),
    (N'Dengue', N'Infectious Diseases / General Medicine', N'an acute infectious disease caused by a flavivirus (species Dengue virus of the genus Flavivirus), transmitted by aedes mosquitoes, and characterized by headache, severe joint pain, and a rash. — called also breakbone fever, dengue fever.', N'drink papaya leaf juice', N'avoid fatty spicy food', N'keep mosquitos away', N'keep hydrated'),
    (N'Diabetes', N'Endocrinology', N'Diabetes is a disease that occurs when your blood glucose, also called blood sugar, is too high. Blood glucose is your main source of energy and comes from the food you eat. Insulin, a hormone made by the pancreas, helps glucose from food get into your cells to be used for energy.', N'have balanced diet', N'exercise', N'consult doctor', N'follow up'),
    (N'Dimorphic hemorrhoids(piles)', N'Proctology / General Surgery', N'Hemorrhoids, also spelled haemorrhoids, are vascular structures in the anal canal. In their ... Other names, Haemorrhoids, piles, hemorrhoidal disease .', N'avoid fatty spicy food', N'consume witch hazel', N'warm bath with epsom salt', N'consume alovera juice'),
    (N'Drug Reaction', N'Allergy & Immunology', N'An adverse drug reaction (ADR) is an injury caused by taking medication. ADRs may occur following a single dose or prolonged administration of a drug or result from the combination of two or more drugs.', N'stop irritation', N'consult nearest hospital', N'stop taking drug', N'follow up'),
    (N'Fungal infection', N'Dermatology', N'In humans, fungal infections occur when an invading fungus takes over an area of the body and is too much for the immune system to handle. Fungi can live in the air, soil, water, and plants. There are also some fungi that live naturally in the human body. Like many microbes, there are helpful fungi and harmful fungi.', N'bath twice', N'use detol or neem in bathing water', N'keep infected area dry', N'use clean cloths'),
    (N'GERD', N'Gastroenterology', N'Gastroesophageal reflux disease, or GERD, is a digestive disorder that affects the lower esophageal sphincter (LES), the ring of muscle between the esophagus and stomach. Many people, including pregnant women, suffer from heartburn or acid indigestion caused by GERD.', N'avoid fatty spicy food', N'avoid lying down after eating', N'maintain healthy weight', N'exercise'),
    (N'Gastroenteritis', N'Gastroenterology', N'Gastroenteritis is an inflammation of the digestive tract, particularly the stomach, and large and small intestines. Viral and bacterial gastroenteritis are intestinal infections associated with symptoms of diarrhea , abdominal cramps, nausea , and vomiting .', N'stop eating solid food for while', N'try taking small sips of water', N'rest', N'ease back into eating'),
    (N'Heart attack', N'Cardiology', N'The death of heart muscle due to the loss of blood supply. The loss of blood supply is usually caused by a complete blockage of a coronary artery, one of the arteries that supplies blood to the heart muscle.', N'call ambulance', N'chew or swallow asprin', N'keep calm', N''),
    (N'Hepatitis B', N'Gastroenterology', N'Hepatitis B is an infection of your liver. It can cause scarring of the organ, liver failure, and cancer. It can be fatal if it isn''t treated. It''s spread when people come in contact with the blood, open sores, or body fluids of someone who has the hepatitis B virus.', N'consult nearest hospital', N'vaccination', N'eat healthy', N'medication'),
    (N'Hepatitis C', N'Gastroenterology', N'Inflammation of the liver due to the hepatitis C virus (HCV), which is usually spread via blood transfusion (rare), hemodialysis, and needle sticks. The damage hepatitis C does to the liver can lead to cirrhosis and its complications as well as cancer.', N'Consult nearest hospital', N'vaccination', N'eat healthy', N'medication'),
    (N'Hepatitis D', N'Gastroenterology', N'Hepatitis D, also known as the hepatitis delta virus, is an infection that causes the liver to become inflamed. This swelling can impair liver function and cause long-term liver problems, including liver scarring and cancer. The condition is caused by the hepatitis D virus (HDV).', N'consult doctor', N'medication', N'eat healthy', N'follow up'),
    (N'Hepatitis E', N'Gastroenterology', N'A rare form of liver inflammation caused by infection with the hepatitis E virus (HEV). It is transmitted via food or drink handled by an infected person or through infected water supplies in areas where fecal matter may get into the water. Hepatitis E does not cause chronic liver disease.', N'stop alcohol consumption', N'rest', N'consult doctor', N'medication'),
    (N'Hypertension', N'Cardiology', N'Hypertension (HTN or HT), also known as high blood pressure (HBP), is a long-term medical condition in which the blood pressure in the arteries is persistently elevated. High blood pressure typically does not cause symptoms.', N'meditation', N'salt baths', N'reduce stress', N'get proper sleep'),
    (N'Hyperthyroidism', N'Endocrinology', N'Hyperthyroidism (overactive thyroid) occurs when your thyroid gland produces too much of the hormone thyroxine. Hyperthyroidism can accelerate your body''s metabolism, causing unintentional weight loss and a rapid or irregular heartbeat.', N'eat healthy', N'massage', N'use lemon balm', N'take radioactive iodine treatment'),
    (N'Hypoglycemia', N'Endocrinology', N'Hypoglycemia is a condition in which your blood sugar (glucose) level is lower than normal. Glucose is your body''s main energy source. Hypoglycemia is often related to diabetes treatment. But other drugs and a variety of conditions — many rare — can cause low blood sugar in people who don''t have diabetes.', N'lie down on side', N'check in pulse', N'drink sugary drinks', N'consult doctor'),
    (N'Hypothyroidism', N'Endocrinology', N'Hypothyroidism, also called underactive thyroid or low thyroid, is a disorder of the endocrine system in which the thyroid gland does not produce enough thyroid hormone.', N'reduce stress', N'exercise', N'eat healthy', N'get proper sleep'),
    (N'Impetigo', N'Dermatology', N'Impetigo (im-puh-TIE-go) is a common and highly contagious skin infection that mainly affects infants and children. Impetigo usually appears as red sores on the face, especially around a child''s nose and mouth, and on hands and feet. The sores burst and develop honey-colored crusts.', N'soak affected area in warm water', N'use antibiotics', N'remove scabs with wet compressed cloth', N'consult doctor'),
    (N'Jaundice', N'Gastroenterology', N'Yellow staining of the skin and sclerae (the whites of the eyes) by abnormally high blood levels of the bile pigment bilirubin. The yellowing extends to other tissues and body fluids. Jaundice was once called the "morbus regius" (the regal disease) in the belief that only the touch of a king could cure it', N'drink plenty of water', N'consume milk thistle', N'eat fruits and high fiberous food', N'medication'),
    (N'Malaria', N'Infectious Diseases / General Medicine', N'An infectious disease caused by protozoan parasites from the Plasmodium family that can be transmitted by the bite of the Anopheles mosquito or by a contaminated needle or transfusion. Falciparum malaria is the most deadly type.', N'Consult nearest hospital', N'avoid oily food', N'avoid non veg food', N'keep mosquitos out'),
    (N'Migraine', N'Neurology', N'A migraine can cause severe throbbing pain or a pulsing sensation, usually on one side of the head. It''s often accompanied by nausea, vomiting, and extreme sensitivity to light and sound. Migraine attacks can last for hours to days, and the pain can be so severe that it interferes with your daily activities.', N'meditation', N'reduce stress', N'use poloroid glasses in sun', N'consult doctor'),
    (N'Osteoarthristis', N'Orthopedics / Rheumatology', N'Osteoarthritis is the most common form of arthritis, affecting millions of people worldwide. It occurs when the protective cartilage that cushions the ends of your bones wears down over time.', N'acetaminophen', N'consult nearest hospital', N'follow up', N'salt baths'),
    (N'Paralysis (brain hemorrhage)', N'Neurology / Emergency', N'Intracerebral hemorrhage (ICH) is when blood suddenly bursts into brain tissue, causing damage to your brain. Symptoms usually appear suddenly during ICH. They include headache, weakness, confusion, and paralysis, particularly on one side of your body.', N'massage', N'eat healthy', N'exercise', N'consult doctor'),
    (N'Peptic ulcer disease', N'Gastroenterology', N'Peptic ulcer disease (PUD) is a break in the inner lining of the stomach, the first part of the small intestine, or sometimes the lower esophagus. An ulcer in the stomach is called a gastric ulcer, while one in the first part of the intestines is a duodenal ulcer.', N'avoid fatty spicy food', N'consume probiotic food', N'eliminate milk', N'limit alcohol'),
    (N'Pneumonia', N'Pulmonology', N'Pneumonia is an infection in one or both lungs. Bacteria, viruses, and fungi cause it. The infection causes inflammation in the air sacs in your lungs, which are called alveoli. The alveoli fill with fluid or pus, making it difficult to breathe.', N'consult doctor', N'medication', N'rest', N'follow up'),
    (N'Psoriasis', N'Dermatology', N'Psoriasis is a common skin disorder that forms thick, red, bumpy patches covered with silvery scales. They can pop up anywhere, but most appear on the scalp, elbows, knees, and lower back. Psoriasis can''t be passed from person to person. It does sometimes happen in members of the same family.', N'wash hands with warm soapy water', N'stop bleeding using pressure', N'consult doctor', N'salt baths'),
    (N'Tuberculosis', N'Pulmonology', N'Tuberculosis (TB) is an infectious disease usually caused by Mycobacterium tuberculosis (MTB) bacteria. Tuberculosis generally affects the lungs, but can also affect other parts of the body. Most infections show no symptoms, in which case it is known as latent tuberculosis.', N'cover mouth', N'consult doctor', N'medication', N'rest'),
    (N'Typhoid', N'Infectious Diseases / General Medicine', N'An acute illness characterized by fever caused by infection with the bacterium Salmonella typhi. Typhoid fever has an insidious onset, with fever, headache, constipation, malaise, chills, and muscle pain. Diarrhea is uncommon, and vomiting is not usually severe.', N'eat high calorie vegitables', N'antiboitic therapy', N'consult doctor', N'medication'),
    (N'Urinary tract infection', N'Urology', N'Urinary tract infection: An infection of the kidney, ureter, bladder, or urethra. Abbreviated UTI. Not everyone with a UTI has symptoms, but common symptoms include a frequent urge to urinate and pain or burning when urinating.', N'drink plenty of water', N'increase vitamin c intake', N'drink cranberry juice', N'take probiotics'),
    (N'Varicose veins', N'Vascular Surgery', N'A vein that has enlarged and twisted, often appearing as a bulging, blue blood vessel that is clearly visible through the skin. Varicose veins are most common in older adults, particularly women, and occur especially on the legs.', N'lie down flat and raise the leg high', N'use oinments', N'use vein compression', N'dont stand still for long'),
    (N'hepatitis A', N'Gastroenterology', N'Hepatitis A is a highly contagious liver infection caused by the hepatitis A virus. The virus is one of several types of hepatitis viruses that cause inflammation and affect your liver''s ability to function.', N'Consult nearest hospital', N'wash hands through', N'avoid fatty spicy food', N'medication');
END
GO

-- ============================================================================
-- SEED DATA: 10 Healthcare Facilities & Specialist Centers
-- ============================================================================
IF NOT EXISTS (SELECT 1 FROM dbo.healthcare_providers)
BEGIN
    INSERT INTO dbo.healthcare_providers (name, facility_type, specialty, latitude, longitude, address, city, phone, emergency_capable, rating, hours) VALUES
    (N'Central Emergency & Trauma Hospital', N'Hospital', N'Emergency / General Medicine', 33.6844, 73.0479, N'Jinnah Avenue, Sector G-8', N'Islamabad', N'+92 51 9261170', 1, 4.8, N'24/7 Open'),
    (N'St. Jude Heart & Vascular Institute', N'Specialist Hospital', N'Cardiology', 33.6931, 73.0685, N'Health Avenue, Blue Area', N'Islamabad', N'+92 51 8440022', 1, 4.9, N'24/7 Open'),
    (N'City Pulmonology & Chest Clinic', N'Clinic', N'Pulmonology', 33.7012, 73.0521, N'Plaza 14, F-7 Markaz', N'Islamabad', N'+92 51 2654321', 0, 4.7, N'9:00 AM - 7:00 PM'),
    (N'Apex Gastroenterology & Liver Center', N'Specialist Clinic', N'Gastroenterology', 33.7150, 73.0380, N'Margalla Road, F-8/3', N'Islamabad', N'+92 51 2259988', 0, 4.6, N'8:30 AM - 6:00 PM'),
    (N'DermaCare Skin & Laser Institute', N'Clinic', N'Dermatology', 33.7220, 73.0610, N'Executive Complex, F-6 Markaz', N'Islamabad', N'+92 51 2821144', 0, 4.8, N'10:00 AM - 8:00 PM'),
    (N'NeuroSpine Advanced Hospital', N'Hospital', N'Neurology', 33.6650, 73.0210, N'I-8 Center, Sector I-8', N'Islamabad', N'+92 51 4432100', 1, 4.7, N'24/7 Open'),
    (N'Endocrine & Diabetes Care Center', N'Clinic', N'Endocrinology', 33.6780, 73.0720, N'Commercial Block, G-9 Markaz', N'Islamabad', N'+92 51 2267711', 0, 4.5, N'9:00 AM - 5:00 PM'),
    (N'Hope Community Health Center', N'Clinic', N'General Practice', 33.6520, 73.0850, N'Main Service Road, I-10', N'Islamabad', N'+92 51 4445566', 0, 4.4, N'8:00 AM - 10:00 PM'),
    (N'Metro General Hospital', N'Hospital', N'General Medicine', 33.6410, 73.0420, N'Peshawar Road, H-13', N'Rawalpindi / Islamabad', N'+92 51 5567890', 1, 4.6, N'24/7 Open'),
    (N'Arthritis & Rheumatology Clinic', N'Clinic', N'Rheumatology', 33.7310, 73.0750, N'Sector E-7 Medical Complex', N'Islamabad', N'+92 51 2618822', 0, 4.7, N'9:00 AM - 6:00 PM');
END
GO