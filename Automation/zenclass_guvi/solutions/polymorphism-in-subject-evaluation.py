import sys

class Subject:
    def has_lab(self):
        pass
    
    def has_project(self):
        pass
    
    def get_theory_marks(self):
        pass

class LabSubject(Subject):
    def has_lab(self):
        return True
    
    def has_project(self):
        return False
    
    def get_theory_marks(self):
        return 70

class ProjectSubject(Subject):
    def has_lab(self):
        return False
    
    def has_project(self):
        return True
    
    def get_theory_marks(self):
        return 80

class TheorySubject(Subject):
    def has_lab(self):
        return False
    
    def has_project(self):
        return False
    
    def get_theory_marks(self):
        return 90

def main():
    class_map = {
        'LabSubject': LabSubject,
        'ProjectSubject': ProjectSubject,
        'TheorySubject': TheorySubject
    }
    
    method_map = {
        'has_lab': 'has_lab',
        'has_project': 'has_project',
        'get_theory_marks': 'get_theory_marks'
    }
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('LabSubject()') or line.startswith('ProjectSubject()') or line.startswith('TheorySubject()'):
            parts = line.split('()')
            class_name = parts[0].split('.')[-1]
            method_name = parts[1][1:] if len(parts) > 1 else ''
            
            if class_name in class_map:
                obj = class_map[class_name]()
                if method_name in method_map:
                    method = getattr(obj, method_map[method_name])
                    result = method()
                    print(result)

if __name__ == "__main__":
    main()
