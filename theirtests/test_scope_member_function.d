
int get_sum(Base b1, Base b2) {
    return b1.get_value() + b2.get_value();
}

class Base {
    int value;
    int get_value() {return value;}
    void set_value(int x) {
        int x;
        x = 20;
        value = x;
    }
    void f(){
        Print("Base");
    }
    void g(Base b) {
        f(this, b);
        Print(get_sum(this, b));
    }
}

class Derived extends Base {
    void f() {
        Print("Derived");
    }
    void g(Base b) {
        f(this, b);
        Print(get_sum(this, b));
    }
}

void f(Base b1, Base b2) {
    Print("111111111111");
    b1.f();
    b2.f();
}

void f(Derived d1, Base b2) {
    Print("222222222222");
    d1.f();
    b2.f();
}

int main() {
  Base d1;
  Derived d2;
  d1 = new Base;
  d2 = new Derived;
  d1.set_value(100);
  d2.set_value(20000);
  d1.g(d2);
}