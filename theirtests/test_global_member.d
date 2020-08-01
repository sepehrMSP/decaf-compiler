class Base {
    void f(){
        Print("Base");
    }
}

class Derived extends Base {
    void f() {
        Print("Derived");
    }
    void g(Derived b) {
        f(this, b);
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
  Derived d1;
  Derived d2;
  d1 = new Derived;
  d2 = new Derived;
  d1.g(d2);
}