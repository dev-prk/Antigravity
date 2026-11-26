import sys

class Pet:
    def eat(self):
        pass
    
    def sleep(self):
        pass
    
    def make_sound(self):
        pass

class Cat(Pet):
    def eat(self):
        print("Cat is eating.")
    
    def sleep(self):
        print("Cat is sleeping.")
    
    def make_sound(self):
        print("Cat is purring.")

class Dog(Pet):
    def eat(self):
        print("Dog is eating.")
    
    def sleep(self):
        print("Dog is sleeping.")
    
    def make_sound(self):
        print("Dog is wagging its tail.")

class Bird(Pet):
    def eat(self):
        print("Bird is eating.")
    
    def sleep(self):
        print("Bird is sleeping.")
    
    def make_sound(self):
        print("Bird is chirping.")

def main():
    pets = {
        'cat': Cat,
        'dog': Dog,
        'bird': Bird
    }
    
    actions = ['eat', 'sleep', 'make_sound', 'quit']
    
    while True:
        try:
            line = input().strip()
        except EOFError:
            break
        
        if line.lower() == 'quit':
            print("Quitting the program.")
            break
        
        if line.lower() in pets:
            current_pet_type = line.lower()
        elif line.lower() in actions:
            if line.lower() == 'quit':
                print("Quitting the program.")
                break
            print("Invalid input. Please enter a valid action (feed/sleep/make_sound/quit).")
        else:
            print("Invalid input. Please enter a valid action (feed/sleep/make_sound/quit).")
            continue
        
        try:
            action_line = input().strip()
        except EOFError:
            break
        
        if action_line.lower() in actions:
            if action_line.lower() == 'quit':
                print("Quitting the program.")
                break
            
            if current_pet_type in pets:
                if action_line.lower() == 'eat':
                    pets[current_pet_type]().eat()
                elif action_line.lower() == 'sleep':
                    pets[current_pet_type]().sleep()
                elif action_line.lower() == 'make_sound':
                    pets[current_pet_type]().make_sound()
            else:
                print("Invalid input. Please enter a valid action (feed/sleep/make_sound/quit).")
        else:
            print("Invalid input. Please enter a valid action (feed/sleep/make_sound/quit).")

if __name__ == "__main__":
    main()
