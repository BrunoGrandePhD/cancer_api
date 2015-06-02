import cancer_api as ca

try:
    from tests_config import db_cnx
except ImportError:
    db_cnx = ca.SqliteConnection()


session = ca.Session(db_cnx)
session.drop_tables()
session.create_tables()
patient = ca.Patient(patient_name="patient_001")
sample = ca.Sample(sample_name="sample_001", sample_type="primary", patient=patient)
library = ca.Library(library_name="library_001", library_type="genome", sample=sample)
session.add(library)
session.commit()
