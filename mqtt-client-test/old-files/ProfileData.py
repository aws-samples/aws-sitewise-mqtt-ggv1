from faker import Faker
from faker_schema.faker_schema import FakerSchema
from faker_schema.schema_loader import load_json_from_file, load_json_from_string

class ProfileData(object):
    @staticmethod
    def get_data():
        json_string = '{"employee_id": "uuid4", "employee_name": "name", "employee address": "address", "email_address": "email"}'
        schema = {'EmployeeInfo': {'ID': 'uuid4', 'Name': 'name', 'Contact': {'Email': 'email',
                                                                              'Phone Number': 'phone_number'}, 'Location': {'Country Code': 'country_code',
                                                                                                                            'City': 'city', 'Country': 'country', 'Postal Code': 'postalcode',
                                                                                                                            'Address': 'street_address'}}}
        #schema = load_json_from_string(json_string)
        faker = FakerSchema()
        data = faker.generate_fake(schema)
        final_data = "{ 'UID': 'PLC-1111', 'main': " + str(data) + "}"
        #fake = Faker()
        print(final_data)
        return data
