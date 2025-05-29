from faker import Faker
from faker.providers import internet

fake = Faker()
fake.add_provider(internet)

print(fake.date_of_birth())
