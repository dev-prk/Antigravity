from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def sound(self):
        pass

class Dog(Animal):
    def sound(self):
        return "Bark"

class Cat(Animal):
    def sound(self):
        return "Meow"

def main():
    animal_type = input().strip()
    
    if animal_type == "dog":
        animal = Dog()
    elif animal_type == "cat":
        animal = Cat()
    else:
        print(-1)
        return
    
    print(animal.sound())

if __name__ == "__main__":
    main()
