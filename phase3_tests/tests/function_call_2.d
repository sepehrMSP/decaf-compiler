
void h() {
    Print("h");
    return;
}

void g() {
    Print("g");
    h();
    return;
}

void f(){
    Print("f");
    g();
    h();
    return;
}

int main()  {
    f();
    g();
    h();
}