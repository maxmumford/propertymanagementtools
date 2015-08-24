from django.db.utils import IntegrityError
from django.contrib.auth.models import User

from datetime import datetime

from models import Building, Room, Person, Tenancy, RentPrice, Transaction, TransactionCategory


SAMPLE_DATA = {
    'SUPERUSER_USERNAME': 'superuser',
    'SUPERUSER_PASSWORD': 'superpass',
    'SUPERUSER_EMAIL': 'super@example.com',

    'BUILDINGS': [
        {'name': 'Osbourne', 'purchase_date': '2014-01-01', 'rooms': ['1', '2']},
        {'name': 'Alderman', 'purchase_date': '2015-01-01', 'rooms': ['1', '2']},
    ],

    'PEOPLE': [
        {'first_name': 'John', 'last_name': 'Smith', 'email': 'johnsmith@example.com', 'phone': '01144422545'},
        {'first_name': 'Amanda', 'last_name': 'Johnson', 'email': 'amandajohnson@example.com', 'phone': '+44 (0) 01144 422 545'},
        {'first_name': 'David', 'last_name': 'Oxford', 'email': 'davidoxford@example.com', 'phone': '07777229993'},
        {'first_name': 'Samantha', 'last_name': 'Oxford', 'email': 'samanthaoxford@example.com', 'phone': '07777229994'},
    ],

    # WARNING! (dates, building) must be unique because of use of get_or_create
    'TENANCIES': [
        {'start_date': '2014-01-01', 'end_date': '2014-12-31', 'building_name': 'Osbourne', 'room_names': ['1', '2'], 'people_emails': ['amandajohnson@example.com'], 
        'rent_prices':
        [
            {'start_date': '2014-01-01', 'end_date': '2014-06-30', 'price': '600'},
            {'start_date': '2014-07-01', 'end_date': '2014-12-31', 'price': '650'},
        ],
        'transactions':
        [
            {'category_hmrc_code': '25', 'date': '2014-01-03', 'amount': 25.32, 'description': 'Repair broken toilet seat'},
            {'category_hmrc_code': '25', 'date': '2014-01-04', 'amount': 78.24, 'description': 'Replace hob cover'},
            {'category_hmrc_code': '25', 'date': '2014-03-07', 'amount': 120, 'description': 'Replace fuses in fuse box'},
            {'category_hmrc_code': '25', 'date': '2014-07-01', 'amount': 25, 'description': 'Replace broken chair'},
            {'category_hmrc_code': '25', 'date': '2014-12-01', 'amount': 5.50, 'description': 'Replace fire alarm'},
            {'category_hmrc_code': '20', 'date': '2014-02-01', 'amount': 600},
            {'category_hmrc_code': '20', 'date': '2014-03-01', 'amount': 600},
            {'category_hmrc_code': '20', 'date': '2014-04-01', 'amount': 600},
            {'category_hmrc_code': '20', 'date': '2014-05-01', 'amount': 600},
            {'category_hmrc_code': '20', 'date': '2014-06-01', 'amount': 600},
            {'category_hmrc_code': '20', 'date': '2014-07-01', 'amount': 650},
            {'category_hmrc_code': '20', 'date': '2014-08-01', 'amount': 650},
            {'category_hmrc_code': '20', 'date': '2014-09-01', 'amount': 650},
            {'category_hmrc_code': '20', 'date': '2014-10-01', 'amount': 650},
            {'category_hmrc_code': '20', 'date': '2014-11-01', 'amount': 650},
            {'category_hmrc_code': '20', 'date': '2014-12-01', 'amount': 650},
        ]},

        {'start_date': '2015-02-01', 'end_date': '2015-12-31', 'building_name': 'Osbourne', 'room_names': ['1'], 'people_emails': ['amandajohnson@example.com'], 
        'rent_prices':
        [
            {'start_date': '2015-02-01', 'end_date': '2015-12-31', 'price': '350'},
        ],
        'transactions':
        [
            {'category_hmrc_code': '25', 'date': '2015-02-09', 'amount': 12, 'description': 'Replace light bulbs'},
            {'category_hmrc_code': '25', 'date': '2015-06-09', 'amount': 300, 'description': 'New pump for shower'},
            {'category_hmrc_code': '20', 'date': '2015-02-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-03-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-04-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-05-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-06-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-07-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-08-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-09-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-10-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-11-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-12-01', 'amount': 350},
        ]},

        {'start_date': '2015-01-01', 'end_date': '2015-12-31', 'building_name': 'Osbourne', 'room_names': ['2'], 'people_emails': ['johnsmith@example.com'], 
        'rent_prices':
        [
            {'start_date': '2015-01-01', 'end_date': '2015-12-31', 'price': '350'},
        ],
        'transactions':
        [
            {'category_hmrc_code': '25', 'date': '2015-08-03', 'amount': 55, 'description': 'New skirting board'},
            {'category_hmrc_code': '20', 'date': '2015-01-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-02-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-03-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-04-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-05-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-06-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-07-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-08-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-09-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-10-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-11-01', 'amount': 350},
            {'category_hmrc_code': '20', 'date': '2015-12-01', 'amount': 350},
        ]},

        {'start_date': '2015-01-01', 'end_date': '2015-12-31', 'building_name': 'Alderman', 'room_names': ['1', '2'], 'people_emails': ['davidoxford@example.com', 'samanthaoxford'], 
        'rent_prices':
        [
            {'start_date': '2015-01-01', 'end_date': '2015-06-30', 'price': '600'},
            {'start_date': '2015-07-01', 'end_date': '2015-12-31', 'price': '650'},
        ],
        'transactions':
        [
            {'category_hmrc_code': '25', 'date': '2015-03-02', 'amount': 250, 'description': 'New kitchen table'},
            {'category_hmrc_code': '25', 'date': '2015-07-03', 'amount': 75, 'description': 'Paint lounge door'},
            {'category_hmrc_code': '25', 'date': '2015-12-09', 'amount': 32, 'description': 'Replace lamp'},
            {'category_hmrc_code': '20', 'date': '2015-01-01', 'amount': 600},
            {'category_hmrc_code': '20', 'date': '2015-02-01', 'amount': 600},
            {'category_hmrc_code': '20', 'date': '2015-03-01', 'amount': 600},
            {'category_hmrc_code': '20', 'date': '2015-04-01', 'amount': 300},
            {'category_hmrc_code': '20', 'date': '2015-05-01', 'amount': 900},
            {'category_hmrc_code': '20', 'date': '2015-06-01', 'amount': 600},
            {'category_hmrc_code': '20', 'date': '2015-07-01', 'amount': 650},
            {'category_hmrc_code': '20', 'date': '2015-08-01', 'amount': 550},
            {'category_hmrc_code': '20', 'date': '2015-09-01', 'amount': 750},
            {'category_hmrc_code': '20', 'date': '2015-10-01', 'amount': 650},
            {'category_hmrc_code': '20', 'date': '2015-11-01', 'amount': 650},
            {'category_hmrc_code': '20', 'date': '2015-12-01', 'amount': 650},
        ]},
    ],

}

def generate_sampledata(options):
    owner = None

    # create superuser
    try:
        owner = User.objects.create_superuser(SAMPLE_DATA['SUPERUSER_USERNAME'], SAMPLE_DATA['SUPERUSER_EMAIL'], SAMPLE_DATA['SUPERUSER_PASSWORD'])
    except IntegrityError as e:
        owner = User.objects.filter(username=SAMPLE_DATA['SUPERUSER_USERNAME'])[0]
        if 'Duplicate' not in str(e):
            raise

    # create building and rooms
    def create_building_and_rooms(building):
        rooms = building.pop('rooms')
        building, created = Building.objects.get_or_create(owner_id=owner.id, **building)
        for room_name in rooms:
            Room.objects.get_or_create(name=room_name, building=building, owner_id=owner.id)
    
    for building in SAMPLE_DATA['BUILDINGS']:
        create_building_and_rooms(building)

    # create people
    def create_person(field_values_dictionary):
        Person.objects.get_or_create(**field_values_dictionary)

    for person in SAMPLE_DATA['PEOPLE']:
        create_person(dict(person, **{'owner_id': owner.id}))

    # create tenancies, rent_prices and transactions
    def create_tenancy_and_rent_prices_and_transactions(field_values_dictionary):
        people = field_values_dictionary.pop('people')
        rooms = field_values_dictionary.pop('rooms')
        rent_prices = field_values_dictionary.pop('rent_prices')
        transactions = field_values_dictionary.pop('transactions')

        # create tenancies
        tenancy, created = Tenancy.objects.get_or_create(**field_values_dictionary)
        tenancy.people.add(*people)
        tenancy.rooms.add(*rooms)

        # create rent prices
        for rent_price in rent_prices:
            RentPrice.objects.get_or_create(tenancy_id=tenancy.id, owner_id=owner.id, **rent_price)

        # create transactions
        for transaction in transactions:
            rent_transaction_category = TransactionCategory.objects.get(hmrc_code=transaction.pop('category_hmrc_code'))
            date = datetime.strptime(transaction['date'], '%Y-%m-%d').date()
            now = datetime.now().date()
            if date.year < now.year or date.year == now.year and date.month <= now.month:
                Transaction.objects.get_or_create(category_id=rent_transaction_category.id, building_id=tenancy.building.id, 
                                                tenancy_id=tenancy.id, owner_id=owner.id, person_id=people[0].id, **transaction)

    for tenancy in SAMPLE_DATA['TENANCIES']:
        tenancy['building_id'] = Building.objects.get(name=tenancy.pop('building_name')).id
        tenancy['rooms'] = Room.objects.filter(name__in=tenancy.pop('room_names'), building_id=tenancy['building_id'])
        tenancy['people'] = Person.objects.filter(email__in=tenancy.pop('people_emails'))
        tenancy['owner_id'] = owner.id
        create_tenancy_and_rent_prices_and_transactions(tenancy)
