# Under the Run | Edit Configurations menu, select "Emulate terminal in output console" to get the getpass to work.
"""
The purpose of this code is to demonstrate some tools in MongoDB for updating an embedded array.
If your database design features an embedded array, adding and deleting elements from that array
would have been performed by means of inserting and deleting rows from a child table in the
relational database.  In SQLAlchemy, if you used bi-directional relationships, the same updates
would be accomplished by adding/deleting a member in a list of references in the parent.  For
instance, we would add an instance of StudentMajor to an instance of Student to record that a
given student has declared a given major.

So far, in SQLAlchemy, we have made the parents in a many to many symmetrical.  Student has
a list of StudentMajor instances, and Major has a list of StudentMajor instances.  That means
that there is redundancy in those lists: the list of StudentMajors in Student could be used to
formulate the list of StudentMajors in any given major.  But that redundancy makes searching
much easier.  The question becomes whether the work needed to keep those two lists synchronized
is worth the improved ease/performance in searching that the redundant data gives you.
"""
import getpass
from datetime import datetime
from pprint import pprint
import pymongo
from pymongo import MongoClient
from pymongo import errors


def drop_collection(schema_ref, collection_name: str):
    """
    Little utility for dropping collections and letting the user know.
    :param schema_ref:          The reference to the current schema.
    :param collection_name:     The name of the collection to drop within that schema.
    :return:                    None
    """
    if collection_name in schema_ref.list_collection_names():
        print(f'Dropping collection: {collection_name}')
        schema_ref[collection_name].drop()


def pcoll(banner: str, recs):
    """
    Print out all the documents in recs.
    :param banner:  The prompt that you want displayed to the console.
    :param recs:    The iterable list of records (documents) that you want printed.
    :return:        None
    """
    print(banner)
    for rec in recs:
        pprint(rec)


"""
This little program is meant to demonstrate how to work with documents that include an array.  A one 
to many design pattern will require that the parent manage an array of references to the children,
which is similar to the bi-directional relationships that we saw in SQLAlchemy.
"""
if __name__ == '__main__':
    password: str = getpass.getpass('Mongo DB password -->')
    username: str = input('Database username [CECS-323-Spring-2023-user] -->') or \
                    "CECS-323-Spring-2023-user"
    project: str = input('Mongo project name [cecs-323-spring-2023] -->') or \
                   "CECS-323-Spring-2023"
    hash_name: str = input('7-character database hash [puxnikb] -->') or "puxnikb"
    cluster = f"mongodb+srv://{username}:{password}@{project}.{hash_name}.mongodb.net/?retryWrites=true&w=majority"
    print(f"Cluster: mongodb+srv://{username}:********@{project}.{hash_name}.mongodb.net/?retryWrites=true&w=majority")
    client = MongoClient(cluster)
    # As a test that the connection worked, print out the database names.
    print(f"The current database names in this cluster are: {client.list_database_names()}")
    # The "Arrays" database is just for this demonstration.  There is nothing significant about
    # the name of the variable nor the database.
    arrays = client['Arrays']  # Create pointer to the Array database
    collections = arrays.list_collection_names()  # prove to myself that I have a collection.
    print(f"The current collections in the Schema database are: {collections}")
    # Make sure that I start with a clean slate for testing.
    drop_collection(arrays, 'products')
    drop_collection(arrays, 'orders')
    arrays.create_collection("products")
    # build my test data.
    # Note that typically you would have a quantity on hand for each product, the manufacturer, the supplier
    # and other pieces of information.  I'm intentionally not bothering with those details to keep this simple.
    # It is important to note that the products collection is not just the authoritative repository of information
    # on products, it is also the authoritative list of what products we have to choose from.  If a given
    # product is not in this collection, we don't stock it.
    #
    # This array of products is just a convenience to allow me to insert all of them at once.  In the database,
    # each array element will be stored as a single document (very simple one at that) in the products collection.
    products = [
        {
            '_id': '076174716511',  # This is the UPC number.  I know it's unique, so I'll use it for the ID.
            'name': 'Stanley 85 Piece Mechanics Tool Set',
            'MSRP': 79.64  # Manufacturer's Suggested Retail Price, independent of the customer.
        },
        {
            '_id': '662679428112',
            'name': 'Deep Standard Length Master Socket Set, 6 and 12 Point, 181 Pieces',
            'MSRP': 123.66
        },
        {
            '_id': '076174748581',
            'name': 'Stanley STMT74858 1/4", 3/8" Drive Mechanics Tool Set, 97 Piece',
            'MSRP': 91.79
        },
        {
            '_id': '076174515114',
            'name': '16 oz Head, Straight Rip Claw Hammer',
            'MSRP': 18.56
        },
        {
            '_id': '049448144105',
            'name': 'Johnson Level Torpedo 9-in Magnetic Torpedo Level',
            'MSRP': 19.00
        }
    ]
    charlie = "Charlie's Bicycle Repair"  # Just so I don't have to type this name again.
    arrays['products'].insert_many(products)  # Put all of my product docs in at once.
    UPC_pull = '049448144105'  # This is the Product that I'm going to pull later.
    # Orders is a list of documents.  I'm going to insert all of these orders at once, and each order will
    # have a list of products (order_details) that appear on the order itself.
    orders = [
        {
            'customer_name': "Ben's automotive",
            'order_date': datetime.utcnow(),  # Local current time WITH timezone.
            'order_details': [
                {
                    'UPC': UPC_pull,
                    'price_each': 15.67,  # Price given to this customer for this product on this order.
                    'quantity': 3
                },
                {
                    'UPC': '076174716511',
                    'price_each': 76.85,
                    'quantity': 2
                }
            ]
        },
        {
            'customer_name': charlie,  # We can substitute variables in wherever we want/need
            'order_date': datetime.utcnow(),
            'order_details': [  # The list of items in this order
                {
                    'UPC': UPC_pull,
                    'price_each': 15.67,  # Price given to this customer for this product on this order.
                    'quantity': 3
                },
                {
                    'UPC': '076174515114',
                    'price_each': 17.28,
                    'quantity': 1
                }
            ]
        }
    ]
    arrays['orders'].insert_many(orders)
    # Find all the orders that have UPC: 049448144105 somewhere in the order.  The string order_details.UPC
    # specifies to MongoDB that we are looking in the order_details array and the UPC attribute within
    # each object within that array.  You can nest this dot notation however deep you like.
    pcoll('Orders with UPC: 049448144105', arrays['orders'].find({'order_details.UPC': '049448144105'}))
    # Add 076174716511 to each order placed by "Charlie's Bicycle Repair".
    # Note that I do an update_many even though I'm sure that there will only be one document that
    # meets the criteria that I'm setting out.  MongoDB will just update the first document that meets
    # the criteria with update_one.  I'd rather that it threw an exception if there is more than one
    # document that meets the search criteria.
    UPC_push: str = '076174716511'  # The UPC of a product that we're going to push to the charlie customer order.
    arrays['orders'].update_many(
        {'customer_name': charlie},
        {'$push':
            {
                'order_details': {
                    'UPC': UPC_push,
                    'price_each': 77.01,
                    'quantity': 3
                }
            }
        }
    )
    pcoll(f'Orders with UPC: {UPC_push} after adding that product to {charlie} order',
          arrays['orders'].find({'order_details.UPC': UPC_push}))
    # Let's get rid of the order item '049448144105' from Charlie's Bicycle Repair order.  Note,
    # just the name of the customer is not unique, normally, we would search by the order_date
    # as well.  But I'm not as concerned about uniqueness constraints for this demonstration.
    arrays['orders'].update_many(
        {'customer_name': charlie},
        {'$pull':
            {
                'order_details': {'UPC': UPC_pull}
            }
        }
    )
    pcoll(f'Orders that still include UPC: {UPC_pull} after removing {UPC_pull} from {charlie}',
          arrays['orders'].find({'order_details.UPC': UPC_pull}))
    # An example of using $any
    UPC_any1: str = '076174515114'
    UPC_any2: str = '076174716511'
    pcoll(f'Orders that have either UPC: {UPC_any1} OR: {UPC_any2}',
          arrays['orders'].find(
              {
                  'order_details.UPC': {
                      '$in': [UPC_any1, UPC_any2]
                  }
              }
          )
          )
    # The $all does not care which order the elements occur in the array.  That is the behavior that we need
    # for a use case like this one.  I am honestly not sure what to do if the order IS significant.
    pcoll(f'Orders that have both UPC: {UPC_any1} AND: {UPC_any2}',
          arrays['orders'].find(
              {
                  'order_details.UPC': {
                      '$all': [UPC_any1, UPC_any2]
                  }
              }
          )
          )
    print('exiting normally')