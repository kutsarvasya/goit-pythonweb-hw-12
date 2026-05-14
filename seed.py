import asyncio
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import Contact

fake = Faker()


async def seed_contacts(session: AsyncSession, count: int = 20):
    for _ in range(count):
        contact = Contact(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            phone=fake.numerify("+31#########"),
            birthday=fake.date_of_birth(minimum_age=18, maximum_age=60),
            additional_data=fake.text(max_nb_chars=50),
        )
        session.add(contact)

    await session.commit()


async def main():
    async for session in get_db():
        await seed_contacts(session, 20)


if __name__ == "__main__":
    asyncio.run(main())
