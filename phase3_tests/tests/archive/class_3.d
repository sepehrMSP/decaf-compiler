class Animal {
    string name;
    int age;

    void set_name(string name2) {
        name = name2;
    }

    string get_name(){
        return this.name;
    }

    void init_age() {
        age = 0;
    }

    void add_age(int years) {
        age = age + years;
    }

    int get_age(){
        return age;
    }

     string battle(Animal b) {
        return "WRONG FIGHT";
     }

    void get_voice() {
        Print("....");
    }

    void init_power() {}
    int get_power() {}
    void add_power(int d) {}
}

class WildAnimal extends Animal {
    int power;
    void init_power() {
        power = 0;
    }

    void add_power (int d ){
        power = power + d;
    }

    int get_power() {
        return power;
    }

    string battle(Animal oth) {
        return "OKAY";
    }
}

class FarmAnimal extends Animal {
    int power;
    void init_power() {
        power = 0;
    }

    void add_power (int d ){
        power = power + d;
    }

    int get_power() {
        return power;
    }
}

class Lion extends WildAnimal {
    void get_voice() {
        Print("LION");
    }
}

class Tiger extends WildAnimal {
    void get_voice() {
        Print("TIGER");
    }
}

class Sheep extends FarmAnimal {
    void get_voice() {
        Print("SHEEP");
    }
}

int main() {
    Animal[] animals;
    int n;
    int years;
    int i;
    int query;

    Print("Num of animals");
    n = ReadInteger();

    animals = NewArray(n, Animal);

    for (i=0; i<n; i=i+1) {
string type;
        string name;

        Print("type and name of animal ", i);

        type = ReadLine();
        if (type == "L") {
            animals[i] = new Lion;
            //animals[i].init_power();
        } else if(type == "T") {
            animals[i] = new Tiger;
            //animals[i].init_power();
        }
        else {
            animals[i] = new Sheep;
            //animals[i].init_defence();
        }

        animals[i].init_age();
        name = ReadLine();
        animals[i].set_name(name);
        animals[i].init_power();
    }

    for (i=0; i<n; i=i+1) {
        animals[i].get_voice();
        Print(animals[i].get_name());
    }

    Print("Years :");

    years = ReadInteger();
    for (i=0; i<n; i=i+1) {
        animals[i].add_age(i * years);
    }

    Print("Queries :");

    query = ReadInteger();
    for (i=0; i<query; i=i+1) {
        int d;
        int id;
        Print("id and d");
        id = ReadInteger();
        d = ReadInteger();
        animals[id].add_power(d);
    }

    Print("Fights :");
    query = ReadInteger();
    for (i=0; i<query; i=i+1) {
        int i1;
        int i2;
        i1 = ReadInteger();
        i2 = ReadInteger();
        Print(animals[i1].battle(animals[i2]));
    }

}
