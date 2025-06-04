from faker import Faker
from faker.providers import internet

fake = Faker("zh_CN")
fake.add_provider(internet)

print(fake.date_of_birth().year)
print(fake.job())

print(fake.numerify("maayanishimura@example.org"))
