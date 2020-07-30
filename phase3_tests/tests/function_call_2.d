
void h() {
    Print("h");
}

void g() {
    Print("g");
    h();
}

void f(){
    Print("f");
    g();
    h();
}

int main()  {
    f();
    g();
    h();
}