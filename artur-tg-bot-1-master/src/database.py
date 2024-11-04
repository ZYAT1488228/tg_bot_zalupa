from datetime import date, datetime, timedelta

from src.models import Base, Pass, Person, Vessel, Test, GenAct1, NotificationAct1

import atexit

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.schema import (
    DropConstraint,
    DropTable,
    MetaData,
    Table,
    ForeignKeyConstraint,
)

# URL = 'postgresql+psycopg2://ygzkbldqgkezzd:8ef7e55f1cb17c369879c6b94c06bb9506aa10dcf79a5e7ca98eee4a0f90123e@ec2-63-34-16-201.eu-west-1.compute.amazonaws.com:5432/d4dvn592mhjllc'
URL = 'postgresql+psycopg2://kascbazxeaybud:74f4bca6daa0729e4a83ae0e012850b2681a7a98cc6bfacff239e53d2f29b12f@ec2-54-72-196-9.eu-west-1.compute.amazonaws.com:5432/dc6itevgp1ic4i'

engine = create_engine(URL)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(bind=engine)

def shutdown_handler():
    print('Shutting down')
    session.close_all()
    engine.dispose()

atexit.register(shutdown_handler)

def create_new_pass(
    names: list[str],
    start_date: date,
    end_date: date,
    created_at: datetime,
    auto_model:str,
    auto_plates:str
):
    people = [
        Person(name=name) 
        for name in names
    ]
    
    new_pass = Pass(
        people = people,
        date_start=start_date,
        date_end=end_date,
        created_at=created_at,
        auto_model=auto_model,
        auto_plates = auto_plates
    )
    
    session.add(new_pass)
    session.commit()
    
    session.refresh(new_pass)

    return new_pass

def get_formatted_last_id():
    # Запрос на получение ID последней строки
    last_row = session.query(Test).order_by(Test.id.desc()).first()
    
    if last_row:
        last_id = last_row.id
        # Форматирование ID в требуемый формат (например, 001)
        formatted_id = f"{last_id:03d}"
        new_row = Vessel()
        session.add(new_row)
        session.commit()
        return formatted_id
    else:
        new_row = Test()
        session.add(new_row)
        last_row = session.query(Vessel).order_by(Vessel.id.desc()).first()

        last_id = last_row.id
        # Форматирование ID в требуемый формат (например, 001)
        formatted_id = f"{last_id:03d}"
        session.commit()
        return formatted_id


def get_last_id_gen_act():
    last_row = session.query(GenAct1).order_by(GenAct1.id.desc()).first()

    if last_row:
        last_id = last_row.id
        new_row = GenAct1()
        session.add(new_row)
        session.commit()
        return last_id
    else:
        new_row = GenAct1()
        session.add(new_row)
        last_row = session.query(GenAct1).order_by(GenAct1.id.desc()).first()
        last_id = last_row.id
        new_row1 = GenAct1()
        session.add(new_row1)
        session.commit()
        return last_id


def get_last_id_notification_act():
    last_row = session.query(NotificationAct1).order_by(NotificationAct1.id.desc()).first()

    if last_row:
        last_id = last_row.id
        new_row = NotificationAct1()
        session.add(new_row)
        session.commit()
        
        return last_id
    else:
        new_row = NotificationAct1()
        session.add(new_row)
        last_row = session.query(NotificationAct1).order_by(NotificationAct1.id.desc()).first()
        last_id = last_row.id
        new_row1 = NotificationAct1()
        session.add(new_row1)
        session.commit()
        return last_id

def get_all_passes_db():
    today = date.today()
    
    passes = session.query(Pass).filter(Pass.date_end >= today).all()
    
    return passes

def drop_everything(engine):
    con = engine.connect()
    trans = con.begin()
    inspector = Inspector.from_engine(engine)

    meta = MetaData()
    tables = []
    all_fkeys = []

    for table_name in inspector.get_table_names():
        fkeys = []

        for fkey in inspector.get_foreign_keys(table_name):
            if not fkey["name"]:
                continue

            fkeys.append(ForeignKeyConstraint((), (), name=fkey["name"]))

        tables.append(Table(table_name, meta, *fkeys))
        all_fkeys.extend(fkeys)

    for fkey in all_fkeys:
        con.execute(DropConstraint(fkey))

    for table in tables:
        con.execute(DropTable(table))

    trans.commit()


    
if __name__ == "__main__":
    # create_new_pass(["teest", "test"], date.today(), date.today(), datetime.now())
    drop_everything(engine)
    # shutdown_handler()