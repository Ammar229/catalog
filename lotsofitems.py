from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Items, User

engine = create_engine('postgresql+psycopg2://catalog:catalog@localhost/catalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Tester", email="Tester@udacity.com",
             picture='http://www.texasrevs.com/wp-content/uploads/2016/10/dummy-image.jpg')
session.add(User1)
session.commit()

# Items for FootBall
category1 = Category(name="Foot Ball")
session.add(category1)
session.commit()


item1 = Items(user_id=1, name="Shoes", description="Very Good Choose for profisinal player", category = category1)
session.add(item1)
session.commit()


item2 = Items(user_id=1, name="Ball", description="Ball very nice nice Yes", category = category1)
session.add(item2)
session.commit()


item3 = Items(user_id=1, name="T-shirt", description="This T-shirt for mess best player ever", category = category1)
session.add(item3)
session.commit()


item4 = Items(user_id=1, name="Card", description="Cards for Jagemnetal person", category = category1)
session.add(item4)
session.commit()



# Items for basketball
category1 = Category(name="Basket Ball")
session.add(category1)
session.commit()


item1 = Items(user_id=1, name="Boot", description="Very Good Boot for profisinal Basket Ball Player", category = category1)
session.add(item1)
session.commit()


item2 = Items(user_id=1, name="Red Ball", description="Ball for basket", category = category1)
session.add(item2)
session.commit()


item3 = Items(user_id=1, name="T-shirt", description="This T-shirt for maycel gordan best player Basket Ball ever", category = category1)
session.add(item3)
session.commit()


item4 = Items(user_id=1, name="whistle", description="whistle for Jadge", category = category1)
session.add(item4)
session.commit()



# Items for Tennis
category1 = Category(name="Tennis")
session.add(category1)
session.commit()


item1 = Items(user_id=1, name="Tennis Balls", description=''' It is a common misconception that young players can 
       immediately use the regular sized yellow balls''', category = category1)
session.add(item1)
session.commit()


item2 = Items(user_id=1, name="Shoes", description=" In regards to the shoes for a junior player", category = category1)
session.add(item2)
session.commit()


item3 = Items(user_id=1, name="Apparel", description="what they like and will feel most comfortable playing in", category = category1)
session.add(item3)
session.commit()


item4 = Items(user_id=1, name="Racket", description="Just like with the tennis balls, the racquets are also available in sizes", category = category1)
session.add(item4)
session.commit()



print "categories and items added!"