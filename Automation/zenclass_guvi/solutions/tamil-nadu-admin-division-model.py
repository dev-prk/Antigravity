import sys

class City:
    def __init__(self, name, population):
        self.name = name
        self.population = population

    def print_details(self):
        print(f"City: {self.name}, Population: {self.population}")

class District(City):
    def __init__(self, name, population, num_cities):
        super().__init__(name, population)
        self.num_cities = num_cities

    def print_details(self):
        print(f"District: {self.name}, Population: {self.population}, Number of Cities: {self.num_cities}")

class TamilNadu(District):
    def __init__(self, name, population, num_districts):
        super().__init__(name, population, 0)  # num_cities not relevant for state
        self.num_districts = num_districts

    def print_details(self):
        print(f"State: {self.name}, Population: {self.population}, Number of Districts: {self.num_districts}")

def main():
    lines = sys.stdin.read().splitlines()
    if len(lines) < 3:
        return

    parts1 = lines[0].split(', ')
    city_name = parts1[0].strip()
    city_pop = int(parts1[1])

    parts2 = lines[1].split(', ')
    district_name = parts2[0].strip()
    district_pop = int(parts2[1])
    num_cities = int(parts2[2])

    parts3 = lines[2].split(', ')
    state_name = parts3[0].strip()
    state_pop = int(parts3[1])
    num_districts = int(parts3[2])

    city = City(city_name, city_pop)
    district = District(district_name, district_pop, num_cities)
    state = TamilNadu(state_name, state_pop, num_districts)

    city.print_details()
    district.print_details()
    state.print_details()

if __name__ == "__main__":
    main()
