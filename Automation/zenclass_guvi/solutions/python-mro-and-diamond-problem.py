import sys

def mro_sequence(cls):
    """
    Returns the Method Resolution Order (MRO) for a given class as a list of class names.
    
    The MRO (also known as the C3 linearization in Python) determines the order in which 
    base classes are searched when looking for a method.
    
    Args:
        cls: A Python class object
        
    Returns:
        List of class names in MRO order, starting with the class itself and ending with 'object'
    """
    # Get the MRO tuple using the __mro__ attribute
    # This is computed by Python using the C3 linearization algorithm
    mro = cls.__mro__
    
    # Convert each class to its name
    return [c.__name__ for c in mro]

if __name__ == "__main__":
    # Read the class name from stdin
    class_name = sys.stdin.read().strip()
    
    # Define all the classes as specified in the problem
    class Citizen:
        def role_duties(self):
            return "Citizen duties"

    class Politician(Citizen):
        def role_duties(self):
            return "Politician duties"

    class PublicServant(Citizen):
        def role_duties(self):
            return "Public servant duties"

    class Mayor(Politician, PublicServant):
        def role_duties(self):
            return "Mayor duties"

    class Voter(Citizen):
        def role_duties(self):
            return "Voter duties"

    class Candidate(Citizen):
        def role_duties(self):
            return "Candidate duties"
        
    class ElectedOfficial(Voter, Candidate):
        def role_duties(self):
            return "Elected official duties"

    class Activist(Citizen):
        def role_duties(self):
            return "Activist duties"

    class ActivistPolitician(Activist, Politician):
        def role_duties(self):
            return "Activist politician duties"

    class Worker(Citizen):
        def role_duties(self):
            return "Worker duties"
    
    class Delegate(Politician, Worker):
        def role_duties(self):
            return "Delegate duties"
    
    class WorkingPolitician(Worker, Politician):
        def role_duties(self):
            return "Working politician duties"

    # Get the class from the global namespace
    cls = globals()[class_name]
    
    # Get and print the MRO
    result = mro_sequence(cls)
    print(result)
