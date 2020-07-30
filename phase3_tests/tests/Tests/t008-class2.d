interface Nameable {
    void setName(string name);
    string getName();
}

class Person implements Nameable {
    string name;

    void setName(string new_name) {
        name = new_name;
    }

    string getName() {
        return name;
    }

    int age;

    void setAge(int new_age) {
        age = new_age;
    }

    int getAge() {
        return age;
    }

    void print() {
        Print("Name: ", name, " Age: ", age);
    }
}

class Student extends Person {
    int grade;

    void setGrade(int new_grade) {
        grade = new_grade;
    }

    int getGrade() {
        return grade;
    }

    void print() {
        Print("Name: ", name, " Age: ", age, " Grade: ", grade);
    }
}

int main() {
    Nameable n;
    Person p;
    Person p1;
    person p2;
    Student s1;
    Student s2;

    p1 = new Person;
    p1.setName(ReadLine());
    p1.setAge(ReadInteger());

    p2 = new Person;
    n = p2;
    n.setName(ReadLine());
    p2.setAge(ReadInteger());

    s1 = new Student;
    s1.setName(ReadLine());
    s1.setAge(ReadInteger());
    s1.setGrade(ReadInteger());

    s2 = new Student;
    n = s2;
    n.setName(ReadLine());
    p = s2;
    p.setAge(ReadInteger());
    s2.setGrade(ReadInteger());

    p1.print();
    p2.print();
    s1.print();
    s2.print();

    n = p1;
    Print(n.getName());
    n = s2;
    Print(n.getName());

    p = p2;
    Print(p.getName());
    Print(p.getAge());
    p = s1;
    Print(p.getAge());
    p.print();

    n = s2;
    Print(n.getName());
}
