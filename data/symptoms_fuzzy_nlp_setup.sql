-- ============================================================================
-- AegisMed: NLP Smart Input & Fuzzy Matching Symptoms Setup
-- File: data/symptoms_fuzzy_nlp_setup.sql
-- Database: medical_diagnosis_assistant
-- ============================================================================

USE medical_diagnosis_assistant;
GO

-- 1. Ensure Columns Exist in symptoms table
IF COL_LENGTH(N'dbo.symptoms', N'name') IS NULL
BEGIN
    ALTER TABLE dbo.symptoms ADD [name] NVARCHAR(255) NULL;
END
GO

IF COL_LENGTH(N'dbo.symptoms', N'alternate_names') IS NULL
BEGIN
    ALTER TABLE dbo.symptoms ADD alternate_names NVARCHAR(1000) NULL;
END
GO

IF COL_LENGTH(N'dbo.symptoms', N'urdu_name') IS NULL
BEGIN
    ALTER TABLE dbo.symptoms ADD urdu_name NVARCHAR(255) NULL;
END
GO

IF COL_LENGTH(N'dbo.symptoms', N'urdu_alternate_names') IS NULL
BEGIN
    ALTER TABLE dbo.symptoms ADD urdu_alternate_names NVARCHAR(1000) NULL;
END
GO

-- Populate [name] from [code] or [label] if empty
UPDATE dbo.symptoms
SET [name] = LOWER(REPLACE(code, '_', ' '))
WHERE [name] IS NULL AND code IS NOT NULL;
GO

-- 2. Upsert / Update Comprehensive Symptom Variations (English, Roman Urdu, Urdu Script)

-- Helper Table / Merge for Variations
CREATE TABLE #TempSymptomVariations (
    symptom_name NVARCHAR(255),
    alternate_names NVARCHAR(1000),
    urdu_name NVARCHAR(255),
    urdu_alternate_names NVARCHAR(1000),
    category NVARCHAR(100)
);
GO

INSERT INTO #TempSymptomVariations (symptom_name, alternate_names, urdu_name, urdu_alternate_names, category) VALUES
-- CHEST & BREATHING
(N'cough', N'khasi, khansi, kasi, kasee, khuski, coughhing, dry cough, persistent cough', N'کھانسی, خانسی, خاں سی', N'کھاں سی, خوشکی', N'chest'),
(N'breathlessness', N'shortness of breath, difficulty breathing, saans, saans phulna, saans chalti, saans lena, saans phoolna, dam ghutna', N'سانس لینے میں مشکل, دم پھولنا, سانس پھولنا', N'سانس پھول جانا, دم گھٹنا', N'chest'),
(N'chest pain', N'chest tightness, heart pain, seena dard, seene mein dard, chest burning, cardiac pain, chati dard', N'سینہ درد, دل کا درد, سینے میں درد', N'سینہ میں جکڑاہٹ, دل میں درد', N'chest'),
(N'wheezing', N'wheze, breathing sound, saans mein aavaaz, saans se awaz', N'سانس میں سیٹی', N'سانس سے آواز', N'chest'),

-- HEAD & NERVOUS
(N'headache', N'head ache, sir dard, sar dard, sar me dard, migraine, headaches', N'سر درد, درد سر', N'سر میں درد, شدید سر درد', N'head'),
(N'dizziness', N'dizzy, vertigo, chakkar, ghumrana, chakra, sar ghoomna', N'چکر, سر چکرانا, سر میں چکر', N'چکر آنا, گھومتا ہوا سر', N'head'),

-- FEVER & GENERAL
(N'fever', N'temperature, high temp, temp, high fever, bukhar, taap, chalo, bukhar uthna, tez bukhar', N'بخار, تپ, درجہ حرارت', N'بخار آنا, گرمی دار بخار', N'general'),
(N'fatigue', N'tiredness, weakness, exhaustion, kamzori, thakavat, thakan, tired, susti', N'تھکاوٹ, کمزوری, تھکن', N'بہت تھکا ہوا, جسم میں کمزوری', N'general'),

-- DIGESTIVE & STOMACH
(N'nausea', N'feeling sick, queasiness, ulti, dilkasahi, jee ghbrana, matlhi, matli', N'متلی, الٹی', N'الٹی آنا, جی بھرنا', N'digestive'),
(N'vomiting', N'vomit, throwing up, ulti, qaey, qay, ulti ana', N'الٹی کرنا, قے', N'الٹی ہونا, قے کرنا', N'digestive'),
(N'diarrhea', N'loose motion, loose stool, diarrhea, peshaab, pakhana, dast, pet kharab', N'اسہال, ڈھیلا پاخانہ', N'اسہال ہونا, پاخانہ', N'digestive'),
(N'constipation', N'kostband, kabz, locked bowels, tight stomach', N'قبض, بند پاخانہ', N'پاخانہ بند ہونا', N'digestive'),
(N'abdominal pain', N'stomach pain, belly pain, pet ka dard, pet mein dard, pet mein takleef, pait dard', N'پیٹ درد, پیٹ میں درد', N'پیٹ میں تکلیف, پیٹ میں مروڑ', N'digestive'),
(N'acidity', N'heartburn, seene mein jalan, acid reflux, khate dakar, gas', N'سینے میں جلن, تیزابیت', N'کھٹے ڈکار, جلن', N'digestive'),

-- SKIN & RASHES
(N'rash', N'skin rash, eruption, daane, khilaf, kharish ke daane, jild par daane', N'خارش والے داغ, دانے', N'جلد پر داغ, داغ و خارش', N'skin'),
(N'itching', N'itchy, itching sensation, scratching, khuji, kharish, khujli', N'خارش, کھجلی', N'خارش کرنا, کھجلی ہونا', N'skin'),

-- SORE THROAT & COLD
(N'sore throat', N'throat pain, throat ache, gale ka dard, gale mein dard, throat discomfort, gala kharab, gala dukhna', N'گلے کا درد, گلے میں دردیں', N'گلا خراب, گلا درد کرنا', N'respiratory'),
(N'runny nose', N'cold, nasal congestion, runny, stuffy nose, naak behna, nazla, naak band', N'نزلہ, بہتی ناک', N'ناک بہنا, ناک بند ہونا', N'respiratory'),

-- BODY & MUSCLES
(N'body ache', N'muscle pain, aches, muscles pain, jism dard, puri jism mein dard, jism me dard', N'جسم کا درد, پٹھوں میں درد', N'پورے جسم میں درد, عضلات میں درد', N'muscles'),
(N'back pain', N'backache, peeth ka dard, kamar dard, kmar mein dard', N'پیٹھ درد, کمر درد', N'کمر میں درد, پیٹھ میں تکلیف', N'muscles'),
(N'joint pain', N'arthritis, joint ache, bone pain, jod mein dard, haddi dard, joron ka dard', N'جوڑوں میں درد, ہڈیوں میں درد', N'جوڑ درد کرنا, ہڈی میں درد', N'muscles'),

-- EMERGENCY (High Severity)
(N'severe chest pain', N'crushing chest pain, cardiac emergency, sudden chest pain, shadeed seena dard', N'سینہ میں شدید درد, دل کا شدید درد', N'شدید سینہ درد, دل کی شدید تکلیف', N'emergency'),
(N'severe breathlessness', N'cant breathe, severe shortness of breath, respiratory distress, bilkul saans nahi aa rahi, shadeed saans ki takleef', N'بالکل سانس نہیں آ رہی, سانس میں شدید مشکل', N'سانس لینا بند ہو گیا, بہت شدید سانس کی کمی', N'emergency'),
(N'unconsciousness', N'fainting, passed out, unconscious, behoosh, behosh ho jana', N'بے ہوش, بے ہوشی', N'بے ہوش ہونا, احساس کھونا', N'emergency'),

-- EYES & VISION
(N'blurred vision', N'unclear vision, vision problem, nigah dhundli, saaf nahi dikhta, dhundla nazar aana', N'دھندلی نگاہ, صاف نہیں دیکھ رہے', N'نظر آنا, نظر میں مسئلہ', N'eyes'),
(N'eye pain', N'eye ache, ankh ka dard, ankh mein dard', N'آنکھ میں درد, آنکھ میں تکلیف', N'آنکھ درد کرنا, آنکھ میں جلن', N'eyes'),

-- URINARY
(N'urinary pain', N'painful urination, peshab mein jalan, peshab mein dard, burning urination', N'پیشاب میں جلن, پیشاب کرتے وقت درد', N'پیشاب میں تکلیف', N'urinary'),
(N'frequent urination', N'urinating often, baar baar peshab, peshab zada ata hai', N'بار بار پیشاب, پیشاب کثرت سے', N'بہت سارا پیشاب', N'urinary'),

-- SLEEP & MOOD
(N'insomnia', N'sleep problem, cant sleep, nind nahi aati, neend na ane ka masla, neend na aana', N'نیند نہ آنا, الارام میں رکاوٹ', N'نیند میں مسئلہ, نیند آنا بند', N'sleep'),
(N'anxiety', N'nervousness, worried, tension, ghabra jana, tension horaha hai, bechaini', N'فکر, بے چینی, گھبراہٹ', N'گھبراہٹ کا احساس, فکر مند', N'mood'),

-- ALLERGIES
(N'allergic reaction', N'allergy, allergies, ales, reacton, ale se reaction', N'الرجی, حساس جلد', N'الرجی کا ردعمل', N'allergy'),
(N'sneezing', N'sneezes, frequent sneezing, chhink, chhinkne ka maara, cheenkein', N'چھینک, بار بار چھینک', N'چھینک آنا', N'allergy');
GO

-- Apply to dbo.symptoms
UPDATE s
SET s.[name] = t.symptom_name,
    s.alternate_names = t.alternate_names,
    s.urdu_name = t.urdu_name,
    s.urdu_alternate_names = t.urdu_alternate_names,
    s.category = t.category
FROM dbo.symptoms s
INNER JOIN #TempSymptomVariations t
    ON s.code = REPLACE(t.symptom_name, ' ', '_')
    OR LOWER(s.label) = LOWER(t.symptom_name)
    OR LOWER(s.[name]) = LOWER(t.symptom_name);
GO

-- Insert any remaining that don't exist yet
INSERT INTO dbo.symptoms (code, label, [name], alternate_names, urdu_name, urdu_alternate_names, category, severity_weight, is_critical)
SELECT 
    REPLACE(t.symptom_name, ' ', '_'),
    UPPER(LEFT(t.symptom_name, 1)) + SUBSTRING(t.symptom_name, 2, LEN(t.symptom_name)),
    t.symptom_name,
    t.alternate_names,
    t.urdu_name,
    t.urdu_alternate_names,
    t.category,
    CASE WHEN t.category = 'emergency' THEN 9 ELSE 3 END,
    CASE WHEN t.category = 'emergency' THEN 1 ELSE 0 END
FROM #TempSymptomVariations t
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.symptoms s 
    WHERE s.code = REPLACE(t.symptom_name, ' ', '_')
       OR LOWER(s.[name]) = LOWER(t.symptom_name)
);
GO

DROP TABLE #TempSymptomVariations;
GO

PRINT 'AegisMed: NLP Symptoms with Multilingual Fuzzy Match Variations successfully updated in database!';
GO
