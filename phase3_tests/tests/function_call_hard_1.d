
bool check(double x, double y){
    Print("check");
    return (x > y);
}

void g(int z, int x){
    Print(z);
    Print(x);
}

void z(bool z){
    Print("zz!");
    if (z){
        Print("good z");
    }else{
        Print("bad z");
    }
}

bool ge_5(int inp){
    if (inp >= 5){
        Print("true");
        return true;
    }
    Print("pulse");
    return false;
}

bool while_cond(){
    Print("while...");
    return ge_5(ReadInteger());
}

bool and_cond(int x){
    Print("Andy mandy");
    if(x==1){
        return false;
    }
    return true;
}

void jumper_3(int x){
    Print(x);
    x = 1;
    Print(x);
}

void jumper_2(int y){
    jumper_3(y);
    Print(y);
    jumper_3(y+1);
}

void jumper_1(int x){
    jumper_2(x);
    Print(x);
    jumper_2(x);
}

void f(){
    int x = 5;
    int y = 10;
    g(x, x+y);
    Print(x);
    Print(y);
    double d2 = 2.5;
    double d5 = 5.5;
    if (check(d2, d5)){
        Print("t");
        z(true);
    }else{
        Print("f");
        z(false);
    }

    while (while_cond() and and_cond(ReadInteger())){
        Print("loop");
    }

    jumper_1(10);

    return;
}

int main()  {
    f();
}
